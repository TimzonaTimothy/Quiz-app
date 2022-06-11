from http.client import HTTPResponse
from django.shortcuts import render,redirect,reverse, get_object_or_404
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from .models import Payment
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
#serial
def serial(request):
    if request.method == 'POST':
        serial_num = request.POST['serial']
        user = request.user
        stu = Payment.objects.get(user=user)
        print(stu.serial)
        if serial_num == stu.serial:
            # return redirect('/afterlogin')
            return HttpResponseRedirect('/student/student-exam')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('/student/serial')
    return render(request, 'student/studentserial.html', {})

def studentlogin(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            # code = request.POST['serial']

            
                
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                
                # if code != main.code:
                    
                #     messages.error(request, 'Invalid Serial Supplied')
                #     return redirect('/student/studentlogin')
                #     print(main.code)
                # else:
                auth.login(request,user)
                messages.success(request, ', Welcome '+user.first_name)
                # return redirect('/afterlogin')
                return redirect('/student/serial')
                # return HttpResponseRedirect('/student/student-exam')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('/student/studentlogin')
        return render(request, 'student/studentlogin.html', {})

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')


def student_signup_view(request: HttpRequest) -> HttpResponse:
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    code = "2021/2022/"
    
    mydict={'userForm':userForm,'studentForm':studentForm}
    
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            amount_paid = request.POST['amount']
            payment = Payment.objects.create(amount_paid=amount_paid,user=user)
            payment.serial += '/2022'
            payment.save();
            

            mail_subject = 'Thank you for registrating with us!'
            message = render_to_string('student/order_received_email.html', {
                'user' : user,
                'payment':payment,
            })
            to_email = user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            # return HttpResponseRedirect('studentlogin')
            
            return render(request, 'student/payment.html',{'payment':payment, 'user':user})   
    else: 
        return render(request,'student/studentsignup.html',context=mydict)

def verify_payment(request: HttpRequest, ref: str) -> HttpResponse:
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, 'Registration Successfull')
    else:
        messages.error(request, "Verfication Failed")
    return redirect('/student/studentsignup')



def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()

        return HttpResponseRedirect('view-result')



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student).last()
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  