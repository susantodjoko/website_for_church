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


from datetime import date
from members.importers import parse_date, normalize_blok


class ParseDateTest(TestCase):
    def test_slash_ddmmyyyy(self):
        self.assertEqual(parse_date('29/01/1956'), date(1956, 1, 29))

    def test_indonesian_month_name_lowercase(self):
        self.assertEqual(parse_date('29 Januari 1956'), date(1956, 1, 29))

    def test_indonesian_month_uppercase(self):
        self.assertEqual(parse_date('08 MEI 1976'), date(1976, 5, 8))

    def test_8_digit_raw_ddmmyyyy(self):
        self.assertEqual(parse_date('14051973'), date(1973, 5, 14))

    def test_dash_ddmmyyyy(self):
        self.assertEqual(parse_date('01-11-1977'), date(1977, 11, 1))

    def test_short_year_sep_70(self):
        self.assertEqual(parse_date('27-Sep-70'), date(1970, 9, 27))

    def test_dot_separated(self):
        self.assertEqual(parse_date('01.11.1977'), date(1977, 11, 1))

    def test_junk_dash_returns_none(self):
        self.assertIsNone(parse_date('-'))

    def test_empty_returns_none(self):
        self.assertIsNone(parse_date(''))

    def test_text_junk_returns_none(self):
        self.assertIsNone(parse_date('Belum baptis'))


class NormalizeBlokTest(TestCase):
    def test_strips_leading_zero(self):
        self.assertEqual(normalize_blok('CK01'), 'CK1')

    def test_strips_leading_zero_jt(self):
        self.assertEqual(normalize_blok('JT04'), 'JT4')

    def test_strips_leading_zero_jb(self):
        self.assertEqual(normalize_blok('JB02'), 'JB2')

    def test_no_leading_zero_unchanged(self):
        self.assertEqual(normalize_blok('KM3'), 'KM3')

    def test_lowercase_input_uppercased(self):
        self.assertEqual(normalize_blok('ck01'), 'CK1')

    def test_empty_string(self):
        self.assertEqual(normalize_blok(''), '')
