from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

#用户
class NewUser(AbstractUser):            #继承django自带的认证系统
    phone_number = models.CharField(default='',max_length=15)

    def __str__(self):
        return self.first_name

class type(models.Model):
    name = models.CharField(u'类型',max_length=32)
    description = models.TextField(u'描述',max_length=256, null=True, blank=True)
    def __str__(self):
        return  self.name

class who(models.Model):
    name = models.CharField(u'所属',max_length=32)
    user = models.ForeignKey(NewUser, verbose_name='用户')
    def __str__(self):
        return  self.name

class accountbook(models.Model):
    name = models.CharField(u'开销名称',max_length=256)
    user = models.ForeignKey(NewUser,verbose_name='用户')
    money = models.IntegerField(u'金额')
    type = models.ForeignKey(type, verbose_name=u'类型')
    who = models.ForeignKey(who, verbose_name=u'所属', null=True, blank=True)
    date = models.DateTimeField(u'日期', default=timezone.now)
    def __str__(self):
        return  self.name

#classify subtotal of month
class MonthCount(models.Model):
    user =models.ForeignKey(NewUser,verbose_name='用户')
    date = models.DateTimeField(u'日期',auto_now_add=True)
    type_sum = models.IntegerField(default=0,blank=True,null=True)
    type = models.ForeignKey(type)

#subtotal of month
class MonthCountSum(models.Model):
    user =models.ForeignKey(NewUser,verbose_name='用户')
    date = models.DateTimeField(u'日期',auto_now_add=True)
    sum = models.IntegerField(default=0,blank=True,null=True)

#budget
class budget(models.Model):
    user = models.ForeignKey(NewUser, verbose_name='用户')
    date = models.DateTimeField(u'日期',auto_now=True)
    budget = models.IntegerField(blank=True,null=True)
    real_cost = models.IntegerField(default=0,blank=True,null=True)



