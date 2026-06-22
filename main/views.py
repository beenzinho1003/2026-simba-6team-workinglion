from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import datetime
import random
import string

# Create your views here.
def onboarding(request):
    return render(request, 'pages/onboarding.html')

def signup_login(request):
    return render(request, 'pages/signup_login.html')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    today = datetime.date.today()
    pots = Pot.objects.filter(participants=request.user)
    for pot in pots:
        end_date = pot.start_date + datetime.timedelta(days=pot.days - 1)
        pot.d_day = max((end_date - today).days, 0)

    return render(request, 'pages/dashboard.html', {'pots': pots})

def pot_detail(request, pot_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    pot = get_object_or_404(Pot, pk=pot_id)

    if not pot.participants.filter(id=request.user.id).exists():
        return redirect('main:dashboard')

    today = datetime.date.today()
    end_date = pot.start_date + datetime.timedelta(days=pot.days - 1)
    d_day = max((end_date - today).days, 0)

    if request.method == 'POST':
        
        image = request.FILES.get('image')
        if image:
            if not Proof.objects.filter(
                pot=pot, 
                user=request.user,
                auth_date=today
            ).exists():
                proof = Proof(
                    pot=pot, 
                    user=request.user, 
                    image=image
                )
                proof.save()
            return redirect('main:pot_detail', pot_id=pot.id)

        treat_item = request.POST.get('treat-item')
        target_user_id = request.POST.get('select-people')

        if treat_item and target_user_id:
            prices = {'post': 50, 'poop': 100, 'glasses': 70, 'flower': 70, 'gyaru': 120}

            if treat_item not in prices:
                return redirect('main:pot_detail', pot_id=pot.id)

            if not target_user_id.isdigit():
                return redirect('main:pot_detail', pot_id=pot.id)

            if not pot.participants.filter(id=target_user_id).exists():
                return redirect('main:pot_detail', pot_id=pot.id)

            if str(request.user.id) == target_user_id:
                return redirect('main:pot_detail', pot_id=pot.id)

            target_user = get_object_or_404(User, pk=target_user_id)
            if not PotAvatar.objects.filter(pot=pot, user=target_user).exists():
                return redirect('main:pot_detail', pot_id=pot.id)

            price = prices[treat_item]
            my_profile = request.user.profile
            if my_profile.point >= price:
                my_profile.point -= price
                my_profile.save()

                target_avatar = PotAvatar.objects.get(pot=pot, user=target_user)
                target_avatar.item = treat_item
                target_avatar.save()

            return redirect('main:pot_detail', pot_id=pot.id)


    participants = pot.participants.all()
    participant_infos = []
    my_today_proof = None

    for participant in participants:
        proof = None
        avatar_color = None
        avatar_item = None
        
        if Proof.objects.filter(
            pot=pot,
            user=participant,
            auth_date=today,
            is_valid=True,
        ).exists():
            proof = Proof.objects.get(
                pot=pot,
                user=participant,
                auth_date=today,
                is_valid=True,
            )

        if PotAvatar.objects.filter(pot=pot, user=participant).exists():
            avatar = PotAvatar.objects.get(pot=pot, user=participant)
            avatar_color = avatar.color
            avatar_item = avatar.item

        if participant == request.user:
            my_today_proof = proof

        participant_infos.append({
            'user': participant,
            'proof': proof,
            'avatar_color': avatar_color,
            'avatar_item': avatar_item,
        })

    context = {
        'pot': pot,
        'participants': participants,
        'participant_infos': participant_infos,
        'my_today_proof': my_today_proof,
        'd_day': d_day,
    }
    return render(request, 'pages/pot_detail.html', context)

def pot_choice(request):
    return render(request, 'pages/pot-choice.html')

def join_pot(request, pot_id=None):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if pot_id:
        pot = get_object_or_404(Pot, pk=pot_id)
        return render(request, 'pages/join_pot.html', {'pot': pot})

    return render(request, 'pages/join_pot.html')

def join_pot_action(request, pot_id=None):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method != "POST":
        return redirect('main:join_pot')

    input_code = request.POST.get('entry_code', '').strip().upper()

    if not input_code:
        context = {'error': '입장코드를 입력해주세요.'}
        return render(request, 'pages/join_pot.html', context)

    if pot_id:
        pot = get_object_or_404(Pot, pk=pot_id)
    else:
        if not Pot.objects.filter(pot_code=input_code).exists():
            context = {'error': '존재하지 않는 입장코드입니다.'}
            return render(request, 'pages/join_pot.html', context)
        pot = Pot.objects.get(pot_code=input_code)

    user = request.user

    if pot.participants.filter(id=user.id).exists():
        context = {'error': '이미 참여 중인 팟입니다.'}
        return render(request, 'pages/join_pot.html', context)

    if pot.participants.count() >= pot.pot_people:
        context = {'error': '팟 정원이 모두 찼습니다.'}
        return render(request, 'pages/join_pot.html', context)

    user_profile = request.user.profile
    if input_code != pot.pot_code:
        context = {'error': '입장코드가 일치하지 않습니다.'}
        return render(request, 'pages/join_pot.html', context)

    if user_profile.point < pot.fee:
        context = {'error': '포인트가 부족합니다.'}
        return render(request, 'pages/join_pot.html', context)

    pot.participants.add(user)
    user_profile.point -= pot.fee
    user_profile.save()
    return redirect('main:avatar_setting', pot_id=pot.id)

def new_pot(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    user_profile = request.user.profile
    return render(request, 'pages/new_pot.html', {'user_profile': user_profile})


def create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method != 'POST':
        return redirect('main:new_pot')

    pot_name = request.POST.get('pot-name', '').strip()
    challenge_term = request.POST.get('challenge_term')
    people = request.POST.get('people')
    user_profile = request.user.profile

    if not pot_name:
        context = {'user_profile': user_profile, 'error': '팟 이름을 입력해주세요.'}
        return render(request, 'pages/new_pot.html', context)

    if len(pot_name) > 100:
        context = {'user_profile': user_profile, 'error': '팟 이름은 100자 이하로 입력해주세요.'}
        return render(request, 'pages/new_pot.html', context)

    if challenge_term not in ['7', '14', '30']:
        context = {'user_profile': user_profile, 'error': '챌린지 기간을 선택해주세요.'}
        return render(request, 'pages/new_pot.html', context)

    if people not in ['2', '3', '4', '5', '6']:
        context = {'user_profile': user_profile, 'error': '팟 인원을 선택해주세요.'}
        return render(request, 'pages/new_pot.html', context)

    days = int(challenge_term)
    pot_people = int(people)
    fee = days * 100

    new_pot = Pot(
        pot_name=pot_name,
        host=request.user,
        days=days,
        pot_people=pot_people,
        fee=fee,
        total_prize=(fee * pot_people) + 500,
    )

    string_pool = string.ascii_uppercase + string.digits
    while True:
        result = ''
        for i in range(6):
            result += random.choice(string_pool)

        if not Pot.objects.filter(pot_code=result).exists():
            break

    new_pot.pot_code = result
    new_pot.save()
    new_pot.participants.add(request.user)

    return redirect('main:avatar_setting', pot_id=new_pot.id)
def avatar_setting(request, pot_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    pot = get_object_or_404(Pot, pk=pot_id)

    if not pot.participants.filter(id=request.user.id).exists():
        return redirect('main:dashboard')

    selected_color = None
    my_avatar = None

    if PotAvatar.objects.filter(pot=pot, user=request.user).exists():
        my_avatar = PotAvatar.objects.get(pot=pot, user=request.user)
        selected_color = my_avatar.color

    used_colors = []
    avatars = PotAvatar.objects.filter(pot=pot)
    for avatar in avatars:
        if avatar.user != request.user:
            used_colors.append(avatar.color)

    error = None

    if request.method == 'POST':
        color = request.POST.get('color')
        colors = ['blue', 'purple', 'green', 'red', 'gray', 'pink']

        if not color or color not in colors:
            error = '색상을 선택해주세요.'
        elif PotAvatar.objects.filter(pot=pot, color=color).exists() and color != selected_color:
            error = '이미 다른 참가자가 선택한 색상입니다.'
        else:
            if my_avatar:
                my_avatar.color = color
                my_avatar.save()
            else:
                avatar = PotAvatar(
                    pot=pot,
                    user=request.user,
                    color=color,
                )
                avatar.save()
            return redirect('main:pot_detail', pot_id=pot.id)

    context = {
        'pot': pot,
        'selected_color': selected_color,
        'used_colors': used_colors,
        'error': error,
    }
    return render(request, 'pages/avatar_setting.html', context)

def before_photo(request, pot_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    pot = get_object_or_404(Pot, pk=pot_id)

    if not pot.participants.filter(id=request.user.id).exists():
        return redirect('main:dashboard')

    today = datetime.date.today()
    my_today_proof = None

    if Proof.objects.filter(pot=pot, user=request.user, auth_date=today).exists():
        my_today_proof = Proof.objects.get(pot=pot, user=request.user, auth_date=today)

    if request.method == 'POST':
        if my_today_proof:
            return redirect('main:pot_detail', pot_id=pot.id)

        image = request.FILES.get('image')
        if image:
            proof = Proof(pot=pot, user=request.user, image=image)
            proof.save()
            return redirect('main:pot_detail', pot_id=pot.id)

        context = {
            'pot': pot,
            'now': today,
            'my_today_proof': my_today_proof,
            'error': '인증사진을 선택해주세요.',
        }
        return render(request, 'pages/before_photo.html', context)

    context = {
        'pot': pot,
        'now': today,
        'my_today_proof': my_today_proof,
    }
    return render(request, 'pages/before_photo.html', context)

def after_photo(request, pot_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    pot = get_object_or_404(Pot, pk=pot_id)

    if not pot.participants.filter(id=request.user.id).exists():
        return redirect('main:dashboard')

    today = datetime.date.today()
    
    my_today_proof = Proof.objects.filter(pot=pot, user=request.user, auth_date=today).first()

    if not my_today_proof:
        return redirect('main:before_photo', pot_id=pot.id)

    votes = my_today_proof.votes.all()
    total_participants = pot.participants.count()
    responded_count = votes.count()
    
    agree_count = votes.filter(is_approved=True).count()
    disagree_count = votes.filter(is_approved=False).count()
    
    agree_pct = int((agree_count / responded_count) * 100) if responded_count > 0 else 0
    disagree_pct = 100 - agree_pct

    context = {
        'pot': pot,
        'now': today,
        'my_today_proof': my_today_proof,
        'total_participants': total_participants,
        'responded_count': responded_count,
        'agree_count': agree_count,
        'agree_pct': agree_pct,
        'disagree_count': disagree_count,
        'disagree_pct': disagree_pct,
    }
    return render(request, 'pages/after_photo.html', context)

def photo_vote(request, pot_id, target_user_id):
    pot = get_object_or_404(Pot, pk=pot_id)
    target_user = get_object_or_404(User, pk=target_user_id)
    today = datetime.date.today()

    proof = Proof.objects.filter(pot=pot, user=target_user, auth_date=today).first()

    if request.method == 'POST':
        vote_action = request.POST.get('vote')
        if proof and vote_action:
            vote, created = Vote.objects.get_or_create(proof=proof, voter=request.user, defaults={'is_approved': True})
            vote.is_approved = (vote_action == 'approve')
            vote.save()

            total_people = pot.participants.count()
            reject_count = proof.votes.filter(is_approved=False).count()
            
            if reject_count >= (total_people / 2):
                proof.is_valid = False
            else:
                proof.is_valid = True
            proof.save()

        return redirect('main:pot_detail', pot_id=pot.id)

    context = {
        'pot': pot,
        'target_user': target_user,
        'proof': proof,
    }
    return render(request, 'pages/photo_vote.html', context)


def complete(request, pot_id):
    pot = get_object_or_404(Pot, pk=pot_id)
    
    if not pot.is_completed:
        participants = pot.participants.all()
        rankings = []
        
        for p in participants:
            valid_count = Proof.objects.filter(pot=pot, user=p, is_valid=True).count()
            rankings.append({'user': p, 'count': valid_count})
        
        rankings.sort(key=lambda x: x['count'], reverse=True)
        
        if rankings:
            max_count = rankings[0]['count']
            winners = [r for r in rankings if r['count'] == max_count]
            
            if winners:
                prize_per_winner = pot.total_prize // len(winners)
                for w in winners:
                    profile = w['user'].profile
                    profile.point += prize_per_winner
                    profile.accumulated_point += prize_per_winner
                    profile.save()
                
        pot.is_completed = True
        pot.save()

    participants = pot.participants.all()
    final_rank = []
    for p in participants:
        valid_count = Proof.objects.filter(pot=pot, user=p, is_valid=True).count()
        final_rank.append({'user': p, 'count': valid_count})
    final_rank.sort(key=lambda x: x['count'], reverse=True)

    context = {
        'pot': pot,
        'final_rank': final_rank,
    }
    return render(request, 'pages/complete.html', context)