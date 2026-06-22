from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
import re
from .models import Profile

def signup(request):
    if request.method == 'POST':
        email_data = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('password-check', '')

        if not email_data:
            return render(request, 'accounts/signup.html', {'error': '이메일을 다시 입력해주세요.'})

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email_data):
            return render(request, 'accounts/signup.html', {'error': '올바른 이메일 형식을 입력해주세요.'})

        if User.objects.filter(username=email_data).exists():
            return render(request, 'accounts/signup.html', {'error': '이미 사용 중인 이메일입니다.'})

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            context = {'error': '알파벳 대문자, 소문자 포함 8글자 이상 입력하세요.'}
            return render(request, 'accounts/signup.html', context)

        if password != confirm:
            return render(request, 'accounts/signup.html', {'error': '설정한 비밀번호와 불일치합니다.'})

        request.session['temp_email'] = email_data
        request.session['temp_password'] = password
        return redirect('accounts:signup_nickname')

    return render(request, 'accounts/signup.html')
def signup_nickname(request):
    email_data = request.session.get('temp_email')
    password = request.session.get('temp_password')

    if not email_data or not password:
        return redirect('accounts:signup')

    if request.method == 'POST':
        nickname = request.POST.get('nickname', '').strip()
        if not nickname or len(nickname) > 10:
            context = {'nickname_error': '닉네임은 1자 이상 10자 이하로 입력해주세요.'}
            return render(request, 'accounts/signup_nickname.html', context)

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
        email_data = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email_data or not password:
            return render(request, 'accounts/login.html', {'error': '이메일과 비밀번호를 입력해주세요.'})

        user = auth.authenticate(request, username=email_data, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('main:dashboard')

        return render(request, 'accounts/login.html', {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'})

    return render(request, 'accounts/login.html')
def logout(request):
    auth.logout(request)
    return redirect('main:onboarding')


