from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [
    path('', onboarding, name='onboarding'),
    path('signup_login/', signup_login, name='signup_login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('pot/<int:pot_id>/', pot_detail, name='pot_detail'),
    path('pot/<int:pot_id>/avatar/', avatar_setting, name='avatar_setting'),
    path('pot_choice/', pot_choice, name='pot_choice'),
    path('join_pot/', join_pot, name='join_pot'),
    path('join_pot/<int:pot_id>', join_pot, name='join_pot'),
    path('new_pot/', new_pot, name='new_pot'), 
    path('create/', create, name='create'),
    path('join_pot_action/', join_pot_action, name='join_pot_action'),
    path('join_pot_action/<int:pot_id>/', join_pot_action, name='join_pot_action'),
    path('pot/<int:pot_id>/before_photo/', before_photo, name='before_photo'),
    path('pot/<int:pot_id>/after_photo/', after_photo, name='after_photo'),
    path('pot/<int:pot_id>/photo_vote/<int:target_user_id>/', photo_vote, name='photo_vote'),
    path('pot/<int:pot_id>/complete/', complete, name='complete'),
]
