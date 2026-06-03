from django.test import TestCase
from .models import Keluarga, Member


class KeluargaModelTest(TestCase):
    def test_str(self):
        k = Keluarga(no_kk_gereja='001', nama_keluarga='Santoso')
        self.assertEqual(str(k), 'Santoso (001)')


class MemberModelTest(TestCase):
    def test_str(self):
        m = Member(nama_lengkap='Budi Santoso')
        self.assertEqual(str(m), 'Budi Santoso')

    def test_ordered_by_name(self):
        m1 = Member.objects.create(
            no_sensus='002', nama_lengkap='Zara', jenis_kelamin='P',
            kewargaan='Warga', status='Dewasa'
        )
        m2 = Member.objects.create(
            no_sensus='001', nama_lengkap='Anton', jenis_kelamin='L',
            kewargaan='Warga', status='Dewasa'
        )
        members = list(Member.objects.all())
        self.assertEqual(members[0], m2)
        self.assertEqual(members[1], m1)

from django.urls import reverse
from django.contrib.auth.models import User


class MemberListViewTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='pass', is_staff=True
        )

    def test_redirects_unauthenticated(self):
        response = self.client.get(reverse('members:member_list'))
        self.assertEqual(response.status_code, 302)

    def test_accessible_to_staff(self):
        self.client.login(username='staff', password='pass')
        response = self.client.get(reverse('members:member_list'))
        self.assertEqual(response.status_code, 200)

    def test_search_filters_by_name(self):
        self.client.login(username='staff', password='pass')
        Member.objects.create(no_sensus='001', nama_lengkap='Budi', jenis_kelamin='L', kewargaan='Warga', status='Dewasa')
        Member.objects.create(no_sensus='002', nama_lengkap='Sari', jenis_kelamin='P', kewargaan='Warga', status='Dewasa')
        response = self.client.get(reverse('members:member_list') + '?q=Budi')
        self.assertEqual(response.context['page'].paginator.count, 1)


class BlokChoicesTest(TestCase):
    def test_km3_display_label_is_correct(self):
        k = Keluarga(no_kk_gereja='001', nama_keluarga='Test', blok='KM3', alamat='Test')
        self.assertEqual(k.get_blok_display(), 'KM3')
