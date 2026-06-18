from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from accounts.models import Profile

def mypage(request, id):
    profile_user = get_object_or_404(USer, pk=id)
    profile = get_object_or_404(Profile, user=profile_user)

    context = {
        'profile_user': profile_user,
        'profile': profile,
    }

    return render(request, 'users/mypage.html, context')
