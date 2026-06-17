from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
import re
from .models import Profile

def signup(request):
    if request.method == 'POST':
        email_data = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['password-check']

        if not email_data:
            messages.error(request, '이메일을 다시 입력해주세요.')
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=email_data).exists():
            messages.error(request, '이미 사용 중인 이메일입니다.')
            return render(request, 'accounts/signup.html')

        elif len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            messages.error(request, '알파벳 대문자, 소문자 포함 8글자 이상입력하세요')
            return render(request, 'accounts/signup.html')

        elif password != confirm:
            messages.error(request, '설정한 비밀번호와 불일치합니다.')
            return render(request, 'accounts/signup.html')
            
        else:
            request.session['temp_email'] = email_data
            request.session['temp_password'] = password
            return redirect('accounts:signup_nickname')

    return render(request, 'accounts/signup.html')

def signup_nickname(request):
    if request.method =='POST':    
        nickname = request.POST['nickname']

        email_data = request.session.get('temp_email')
        password = request.session.get('temp_password')

        newuser = User.objects.create_user(
            username=email_data,
            password=password,
        )
        
        profile = Profile(
            user=newuser,
            nickname=nickname,
        )
        profile.save()
            
        auth.login(request, newuser)

        if 'temp_email' in request.session:
            del request.session['temp_email']
            del request.session['temp_password']
        
        return redirect('main:dashboard')

    return render(request, 'accounts/signup_nickname.html')
    

def login(request):
    if request.method == 'POST':
        email_data = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(request, username=email_data, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('main:dashboard')
        else:
            return render(request, 'accounts/login.html')
            
    elif request.method == 'GET':
        return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    return redirect('main:onboarding')


