"""account URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from accounts import views
from accounts import urls as accounts_urls

def i18n_javascript(request):
    return admin.site.i18n_javascript(request)
urlpatterns = [
    url(r'^admin/jsi18n', i18n_javascript),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include(accounts_urls), name='accounts_urls'),
]
