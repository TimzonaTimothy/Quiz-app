from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    serial = models.CharField(max_length=100, default=get_random_string(length=10))
    amount_paid = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    code = models.CharField(max_length=8, blank=True, unique=True, null=True,default=get_random_string(length=8))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


    def __str__(self):
        return self.amount_paid
 
    
