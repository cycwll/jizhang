from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.admin import widgets
import time


class LoginForm(forms.Form):
	uid = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' ,'id':'uid', 'placeholder': 'Username'}))
	pwd = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control' ,'id':'pwd', 'placeholder': 'Password'}))

class AccountForm(forms.Form):
	name = forms.CharField(max_length=256,widget=forms.TextInput(attrs={'placeholder':'如买衣服'}))
	money = forms.CharField(max_length=256)
	type = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control',}),queryset=type.objects.all(),empty_label='请选择类型...')
	who = forms.CharField(max_length=256)
	date = forms.DateTimeField(widget=widgets.AdminDateWidget, label=u'日期',initial=timezone.now())

class MemberForm(forms.Form):
	name = forms.CharField(label='名称',max_length=64,widget=forms.TextInput(attrs={'placeholder':'如老公或者媳妇家'}))
class BudgetForm(forms.Form):
	budget = forms.CharField(label='预算',max_length=64,widget=forms.TextInput(attrs={'placeholder':'设置本月预算'}))