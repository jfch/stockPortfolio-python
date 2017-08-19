from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', auth_views.login, {'template_name': 'portfolio/login.html'}, name='login'),
    url(r'^register$', views.user_registration_web, name='registration'),
    url(r'^portfolio/logout$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^portfolio$', views.home_page, name='home'),
    url(r'^portfolio/result$', views.result_page, name='result')
]