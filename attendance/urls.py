from django.urls import path
from .views import *

urlpatterns = [
    
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('services/', services, name='services'),
    
    path('home/', home, name='home'),
    path('profile/', profile, name='profile'),
    path('delete_profile/', delete_profile,name='delete_profile'),
    path('take_attendance/', take_attendance, name='take_attendance'),
    path('dashboard/', dashboard, name='dashboard'),
    
    ]