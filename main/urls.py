from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [
    path('', onboarding, name='onboarding'),
    path('signup_login/', signup_login, name='signup_login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create_pot/', create_pot, name='create_pot'),
    path('join_pot/', join_pot, name='join_pot'),
]