import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile
from .models import Pot, PotAvatar, Proof


class CoreFlowTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()

        self.host = User.objects.create_user(username='host@test.com', password='Password1')
        self.member = User.objects.create_user(username='member@test.com', password='Password1')
        self.outsider = User.objects.create_user(username='outsider@test.com', password='Password1')

        Profile.objects.create(user=self.host, nickname='호스트')
        Profile.objects.create(user=self.member, nickname='멤버')
        Profile.objects.create(user=self.outsider, nickname='외부인')

        self.pot = Pot.objects.create(
            host=self.host,
            pot_name='아침 운동',
            days=7,
            fee=700,
            total_prize=2600,
            pot_people=3,
            pot_code='ABC123',
        )
        self.pot.participants.add(self.host, self.member)
        PotAvatar.objects.create(pot=self.pot, user=self.host, color='blue')
        PotAvatar.objects.create(pot=self.pot, user=self.member, color='pink')

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def make_image(self, name='proof.png'):
        image_data = BytesIO()
        Image.new('RGB', (10, 10), color='white').save(image_data, format='PNG')
        return SimpleUploadedFile(name, image_data.getvalue(), content_type='image/png')

    def test_dashboard_requires_login_and_has_d_day(self):
        response = self.client.get(reverse('main:dashboard'))
        self.assertRedirects(response, reverse('accounts:login'))

        self.client.force_login(self.host)
        response = self.client.get(reverse('main:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pots'][0].d_day, 6)

    def test_create_rejects_missing_values_without_server_error(self):
        self.client.force_login(self.host)
        response = self.client.post(reverse('main:create'), {
            'pot-name': '',
            'challenge_term': '7',
            'people': '2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '팟 이름을 입력해주세요.')
        self.assertEqual(Pot.objects.count(), 1)

    def test_join_normalizes_entry_code_and_deducts_points(self):
        self.client.force_login(self.outsider)
        response = self.client.post(reverse('main:join_pot_action'), {
            'entry_code': ' abc123 ',
        })
        self.assertRedirects(
            response,
            reverse('main:avatar_setting', args=[self.pot.id]),
        )
        self.assertTrue(self.pot.participants.filter(id=self.outsider.id).exists())
        self.outsider.profile.refresh_from_db()
        self.assertEqual(self.outsider.profile.point, 2800)

    def test_item_rejects_invalid_or_nonparticipant_target(self):
        self.client.force_login(self.host)
        detail_url = reverse('main:pot_detail', args=[self.pot.id])
        original_point = self.host.profile.point

        self.client.post(detail_url, {
            'treat-item': 'invalid-item',
            'select-people': str(self.member.id),
        })
        self.host.profile.refresh_from_db()
        self.assertEqual(self.host.profile.point, original_point)

        self.client.post(detail_url, {
            'treat-item': 'post',
            'select-people': str(self.outsider.id),
        })
        self.host.profile.refresh_from_db()
        self.assertEqual(self.host.profile.point, original_point)

        self.client.post(detail_url, {
            'treat-item': 'post',
            'select-people': 'not-a-number',
        })
        self.host.profile.refresh_from_db()
        self.assertEqual(self.host.profile.point, original_point)

    def test_valid_item_deducts_points_and_updates_avatar(self):
        self.client.force_login(self.host)
        response = self.client.post(reverse('main:pot_detail', args=[self.pot.id]), {
            'treat-item': 'post',
            'select-people': str(self.member.id),
        })
        self.assertRedirects(response, reverse('main:pot_detail', args=[self.pot.id]))

        self.host.profile.refresh_from_db()
        member_avatar = PotAvatar.objects.get(pot=self.pot, user=self.member)
        self.assertEqual(self.host.profile.point, 3450)
        self.assertEqual(member_avatar.item, 'post')

    def test_nonparticipant_cannot_access_photo_pages(self):
        self.client.force_login(self.outsider)
        before_url = reverse('main:before_photo', args=[self.pot.id])
        after_url = reverse('main:after_photo', args=[self.pot.id])
        self.assertRedirects(self.client.get(before_url), reverse('main:dashboard'))
        self.assertRedirects(self.client.get(after_url), reverse('main:dashboard'))

    def test_photo_upload_redirects_to_detail_and_blocks_duplicate(self):
        self.client.force_login(self.host)
        before_url = reverse('main:before_photo', args=[self.pot.id])
        detail_url = reverse('main:pot_detail', args=[self.pot.id])

        response = self.client.post(before_url, {'image': self.make_image()})
        self.assertRedirects(response, detail_url)
        self.assertEqual(Proof.objects.filter(pot=self.pot, user=self.host).count(), 1)

        response = self.client.post(before_url, {'image': self.make_image('second.png')})
        self.assertRedirects(response, detail_url)
        self.assertEqual(Proof.objects.filter(pot=self.pot, user=self.host).count(), 1)

    def test_invalid_proof_is_not_shown_as_authenticated(self):
        self.client.force_login(self.host)
        before_url = reverse('main:before_photo', args=[self.pot.id])
        self.client.post(before_url, {'image': self.make_image()})
        Proof.objects.filter(pot=self.pot, user=self.host).update(is_valid=False)

        response = self.client.get(reverse('main:pot_detail', args=[self.pot.id]))
        host_info = None
        for info in response.context['participant_infos']:
            if info['user'] == self.host:
                host_info = info
        self.assertIsNotNone(host_info)
        self.assertIsNone(host_info['proof'])
