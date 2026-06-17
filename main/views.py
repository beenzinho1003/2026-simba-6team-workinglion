from django.shortcuts import render

# Create your views here.
def onboarding(request):
    return render(request, 'pages/onboarding.html')

def signup_login(request):
    return render(request, 'pages/signup_login.html')

def dashboard(request):
    return render(request, 'pages/dashboard.html')

def create_pot(request):
    return render(request, 'pages/create_pot.html')

def join_pot(request):
    return render(request, 'pages/join_pot.html')