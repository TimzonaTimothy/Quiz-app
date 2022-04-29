from django.db import models
from django.contrib.auth.models import User
import secrets
from .paystack import PayStack

class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Student/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ref = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


    def __str__(self):
        return self.amount_paid

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)


    def amount_value(self) -> int: 
        return self.amount_paid * 100

    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount_paid)
        if status:
            if result['amount'] == self.amount_paid:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False 
    
