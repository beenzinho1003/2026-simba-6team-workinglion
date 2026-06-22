from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class AccountFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user@test.com', password='Password1')
        Profile.objects.create(user=self.user, nickname='사용자')

    def test_signup_returns_context_error(self):
        response = self.client.post(reverse('accounts:signup'), {
            'email': '',
            'password': '',
            'password-check': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '이메일을 다시 입력해주세요.')

    def test_valid_signup_moves_to_nickname_step(self):
        response = self.client.post(reverse('accounts:signup'), {
            'email': 'new@test.com',
            'password': 'Password1',
            'password-check': 'Password1',
        })
        self.assertRedirects(response, reverse('accounts:signup_nickname'))
        self.assertEqual(self.client.session['temp_email'], 'new@test.com')

    def test_login_error_and_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'user@test.com',
            'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '이메일 또는 비밀번호가 올바르지 않습니다.')

        response = self.client.post(reverse('accounts:login'), {
            'email': 'user@test.com',
            'password': 'Password1',
        })
        self.assertRedirects(response, reverse('main:dashboard'))

    def test_logout_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('main:onboarding'))
        self.assertNotIn('_auth_user_id', self.client.session)