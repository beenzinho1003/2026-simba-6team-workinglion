from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('mypage/<int:id>/', mypage, name='mypage'),
]