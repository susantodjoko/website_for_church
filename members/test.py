import csv
import io
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Keluarga, Member
from members.forms import CsvImportForm


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
from members.importers import parse_date, normalize_blok, import_sensus_rows


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


class ImportSensusRowsTest(TestCase):

    def _row(self, **overrides):
        defaults = {
            'No. induk gereja (lihat surat baptisi/sidhi/nikah)': '99999',
            'Nama lengkap': 'Budi Santoso',
            'Jenis kelamin': 'laki-laki',
            'Tempat lahir (sesuai KTP)': 'Salatiga',
            'Tanggal lahir (tanggal/bulan/tahun)': '01/01/1990',
            'Alamat domisili': 'Jl. Test 1',
            'No. telepon': '08123456789',
            'Alamat sesuai KTP': 'Jl. Test 1',
            'Blok (Kelompok PPA)': 'CK01',
            'Status perkawinan': 'menikah',
            'Kategori usia': 'dewasa (41-60 tahun)',
            'kategori kewargaan': 'warga',
            'Golongan darah': 'O',
            'pendidikan terakhir': 'S1',
            'No. KK (Kartu Kewargaan gereja) (diisi petugas)': '',
            'status dalam keluarga': 'kepala keluarga',
            'pekerjaan': 'swasta',
            'Status rumah tinggal': 'milik sendiri',
            'Tempat kebaktian': 'induk',
            'Jika di pertanyaan sebelumnya tempat kebaktian di gereja lain, isilah nama gerejanya dan kotanya': '',
            'Status (iman)': 'dewasa',
            'Baptis oleh (nama pembaptis) (lihat surat baptis)': 'Pdt. Test',
            'tanggal baptis (lihat surat baptis)': '25/12/2000',
            'sidhi oleh (nama pendeta) (lihat surat sidhi)': 'Pdt. Test',
            'tanggal sidhi (lihat surat sidhi)': '25/12/2010',
            'nikah oleh (lihat surat nikah)': '',
            'tanggal nikah (lihat surat nikah)': '',
            'tempat baptis (nama gereja) (lihat surat baptis)': 'GKJ Salatiga',
            'tempat sidhi (nama gereja) (lihat surat sidhi)': 'GKJ Salatiga',
            'tempat nikah (nama gereja/kota)': '',
            'status kewargaan gereja': 'warga',
            'Minat pelayanan gerejawi': 'paduan suara',
            'minat pelayanan umum': 'sosial',
        }
        defaults.update(overrides)
        return defaults

    def test_imports_new_member(self):
        result = import_sensus_rows([self._row()])
        self.assertEqual(result.imported, 1)
        self.assertEqual(result.updated, 0)
        self.assertTrue(Member.objects.filter(no_sensus='99999').exists())

    def test_updates_existing_member(self):
        import_sensus_rows([self._row()])
        result = import_sensus_rows([self._row(**{'Nama lengkap': 'Budi Updated'})])
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.imported, 0)
        self.assertEqual(Member.objects.get(no_sensus='99999').nama_lengkap, 'Budi Updated')

    def test_skips_row_with_empty_nama(self):
        result = import_sensus_rows([self._row(**{'Nama lengkap': ''})])
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.imported, 0)

    def test_empty_sensus_generates_temp_no(self):
        result = import_sensus_rows([self._row(**{
            'No. induk gereja (lihat surat baptisi/sidhi/nikah)': '-',
        })])
        self.assertEqual(result.imported, 1)
        self.assertTrue(Member.objects.filter(no_sensus__startswith='IMPORT-').exists())

    def test_sets_sudah_baptis_when_baptis_oleh_present(self):
        import_sensus_rows([self._row()])
        m = Member.objects.get(no_sensus='99999')
        self.assertTrue(m.sudah_baptis)
        self.assertEqual(m.baptis_oleh, 'Pdt. Test')

    def test_sets_sudah_sidi_when_sidi_oleh_present(self):
        import_sensus_rows([self._row()])
        m = Member.objects.get(no_sensus='99999')
        self.assertTrue(m.sudah_sidi)

    def test_creates_keluarga_when_kk_provided(self):
        import_sensus_rows([self._row(**{
            'No. KK (Kartu Kewargaan gereja) (diisi petugas)': 'CK2-TEST-001',
        })])
        self.assertTrue(Keluarga.objects.filter(no_kk_gereja='CK2-TEST-001').exists())

    def test_normalizes_blok_on_keluarga(self):
        import_sensus_rows([self._row(**{
            'No. KK (Kartu Kewargaan gereja) (diisi petugas)': 'CK2-TEST-002',
            'Blok (Kelompok PPA)': 'CK01',
        })])
        k = Keluarga.objects.get(no_kk_gereja='CK2-TEST-002')
        self.assertEqual(k.blok, 'CK1')

    def test_result_counts_multiple_rows(self):
        rows = [
            self._row(**{'No. induk gereja (lihat surat baptisi/sidhi/nikah)': '11111', 'Nama lengkap': 'Alice'}),
            self._row(**{'No. induk gereja (lihat surat baptisi/sidhi/nikah)': '22222', 'Nama lengkap': 'Bob'}),
            self._row(**{'Nama lengkap': ''}),
        ]
        result = import_sensus_rows(rows)
        self.assertEqual(result.imported, 2)
        self.assertEqual(result.skipped, 1)


class CsvImportFormTest(TestCase):
    def test_valid_csv_file_accepted(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile('test.csv', b'col1,col2\nval1,val2', content_type='text/csv')
        form = CsvImportForm(files={'csv_file': f})
        self.assertTrue(form.is_valid())

    def test_missing_file_invalid(self):
        form = CsvImportForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('csv_file', form.errors)


class CsvImportAdminViewTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin', password='pass', email='a@a.com'
        )
        self.client.login(username='admin', password='pass')

    def _csv_bytes(self):
        rows = [{
            'No. induk gereja (lihat surat baptisi/sidhi/nikah)': '55555',
            'Nama lengkap': 'Test Warga',
            'Jenis kelamin': 'perempuan',
            'Tempat lahir (sesuai KTP)': 'Salatiga',
            'Tanggal lahir (tanggal/bulan/tahun)': '01/06/1985',
            'Alamat domisili': 'Jl. Admin 1',
            'No. telepon': '',
            'Alamat sesuai KTP': 'Jl. Admin 1',
            'Blok (Kelompok PPA)': 'CK01',
            'Status perkawinan': 'menikah',
            'Kategori usia': 'dewasa (41-60 tahun)',
            'kategori kewargaan': 'warga',
            'Golongan darah': 'A',
            'pendidikan terakhir': 'S1',
            'No. KK (Kartu Kewargaan gereja) (diisi petugas)': '',
            'status dalam keluarga': 'istri',
            'pekerjaan': 'ASN',
            'Status rumah tinggal': 'milik sendiri',
            'Tempat kebaktian': 'induk',
            'Jika di pertanyaan sebelumnya tempat kebaktian di gereja lain, isilah nama gerejanya dan kotanya': '',
            'Status (iman)': 'dewasa',
            'Baptis oleh (nama pembaptis) (lihat surat baptis)': '',
            'tanggal baptis (lihat surat baptis)': '',
            'sidhi oleh (nama pendeta) (lihat surat sidhi)': '',
            'tanggal sidhi (lihat surat sidhi)': '',
            'nikah oleh (lihat surat nikah)': '',
            'tanggal nikah (lihat surat nikah)': '',
            'tempat baptis (nama gereja) (lihat surat baptis)': '',
            'tempat sidhi (nama gereja) (lihat surat sidhi)': '',
            'tempat nikah (nama gereja/kota)': '',
            'status kewargaan gereja': 'warga',
            'Minat pelayanan gerejawi': '',
            'minat pelayanan umum': '',
        }]
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode('utf-8')

    def test_get_import_page_returns_200(self):
        url = reverse('admin:members_member_import_sensus')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Import Sensus CSV')

    def test_post_valid_csv_shows_result(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('admin:members_member_import_sensus')
        f = SimpleUploadedFile('sensus.csv', self._csv_bytes(), content_type='text/csv')
        response = self.client.post(url, {'csv_file': f})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Import Selesai')
        self.assertTrue(Member.objects.filter(no_sensus='55555').exists())

    def test_member_changelist_has_import_button(self):
        url = reverse('admin:members_member_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'Import Sensus CSV')

    def test_unauthenticated_redirects(self):
        self.client.logout()
        url = reverse('admin:members_member_import_sensus')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
