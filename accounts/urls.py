from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^login/', views.log_in, name='login'),
    url(r'^index/', views.index, name='index'),
    url(r'^logout/', views.log_out, name='logout'),
    url(r'^summary/',views.summary,name='summary'),
    url(r'^keepaccount/',views.keepaccount,name='keepaccount'),
    url(r'^member/',views.member,name='member'),
    url(r'^budget/',views.budgetview,name='budget'),
    url(r'^monthcount/',views.monthcount,name='monthcount'),
    url(r'^charts/',views.charts,name='charts'),
    ]
urlpatterns += staticfiles_urlpatterns()