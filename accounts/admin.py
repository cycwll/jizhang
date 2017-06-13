from django.contrib import admin
from .models import *

class NewUserAdmin(admin.ModelAdmin):
    search_fields = ['first_name','username']
    list_display = ('first_name','username', 'phone_number', 'email')

class TypeAdmin(admin.ModelAdmin):
    list_display = ('name','description')

class AccountbookAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['type', 'who', 'date']
    list_display = ('name','user', 'money','type', 'who', 'date',)

class WhoAdmin(admin.ModelAdmin):
    list_display = ('name',)

class MonthCountAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'type_sum', 'type')

class MonthCountSumAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'sum')


admin.site.register(NewUser, NewUserAdmin)
admin.site.register(type, TypeAdmin)
admin.site.register(accountbook, AccountbookAdmin)
admin.site.register(who, WhoAdmin)
admin.site.register(MonthCount, MonthCountAdmin)
admin.site.register(MonthCountSum, MonthCountSumAdmin)
