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
