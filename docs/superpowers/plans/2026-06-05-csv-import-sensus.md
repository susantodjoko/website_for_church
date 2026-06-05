# CSV Import Sensus — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Django admin upload view so staff can import the annual GKJ Salatiga member census CSV (from Google Forms) directly from the browser.

**Architecture:** The import logic lives in `members/importers.py` with no HTTP dependency — it takes a list of row dicts and returns an `ImportResult`. `members/admin.py` wires it to a custom admin view behind `/admin/members/member/import-sensus/`. Three templates handle the upload form, results page, and the Import button on the Member changelist.

**Tech Stack:** Django 5, Python stdlib (`csv`, `io`, `re`, `dataclasses`, `datetime`), Django admin templates.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `members/importers.py` | Create | All import logic — parse_date, normalizers, import_sensus_rows() |
| `members/forms.py` | Modify | Add CsvImportForm |
| `members/admin.py` | Modify | Add custom URL, import view, change_list_template |
| `members/templates/admin/members/member/changelist.html` | Create | Adds "Import Sensus CSV" button |
| `members/templates/admin/members/member/import_sensus.html` | Create | Upload form page |
| `members/templates/admin/members/member/import_result.html` | Create | Results summary page |
| `members/test.py` | Modify | Tests for importers and admin view |

---

### Task 1: Core Utilities — parse_date and normalize_blok

**Files:**
- Create: `members/importers.py`
- Modify: `members/test.py`

- [ ] **Step 1: Add failing tests to `members/test.py`**

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```
venv\Scripts\python manage.py test members.test.ParseDateTest members.test.NormalizeBlokTest
```

Expected: FAIL — `ImportError: cannot import name 'parse_date' from 'members.importers'`

- [ ] **Step 3: Create `members/importers.py` with utilities**

```python
import re
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime

from .models import Keluarga, Member

# ── Constants ──────────────────────────────────────────────────────────────

INDONESIAN_MONTHS = {
    'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
    'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
    'september': '09', 'oktober': '10', 'november': '11', 'desember': '12',
}

DATE_FORMATS = [
    '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d',
    '%d %b %Y', '%d-%b-%Y', '%d-%b-%y', '%d %b %y',
    '%d/%m/%y', '%d-%m-%y',
]

JUNK_VALUES = {
    '', '-', '--', '---', '_', '__', 'n/a', 'na', 'belum', 'none',
    'tidak ada', 'tdk ada', 'tdk', '–', '—',
}


# ── Result ─────────────────────────────────────────────────────────────────

@dataclass
class ImportResult:
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list = dataclass_field(default_factory=list)


# ── Low-level helpers ───────────────────────────────────────────────────────

def _clean(val):
    if val is None:
        return ''
    v = str(val).strip()
    return '' if v.lower() in JUNK_VALUES else v


def _is_junk(val):
    return not _clean(val)


def _normalize_header(h):
    return re.sub(r'\s+', ' ', h).strip()


def _normalize_row(raw_row):
    """Strip and collapse whitespace in column headers."""
    return {_normalize_header(k): v for k, v in raw_row.items()}


# ── Date parser ─────────────────────────────────────────────────────────────

def parse_date(raw):
    """Try multiple date formats. Returns a date or None."""
    if not raw or _is_junk(raw):
        return None
    raw = str(raw).strip()

    # Replace Indonesian month names (case-insensitive)
    lower = raw.lower()
    for name, num in INDONESIAN_MONTHS.items():
        lower = lower.replace(name, num)

    # Collapse stray whitespace / dashes around spaces
    cleaned = re.sub(r'\s*-\s*', '-', lower).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # 8-digit raw number → try DDMMYYYY
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 8:
        try:
            return datetime.strptime(digits, '%d%m%Y').date()
        except ValueError:
            pass

    for candidate in [cleaned, raw.strip()]:
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(candidate.strip(), fmt).date()
            except ValueError:
                continue
    return None


# ── Blok normalizer ─────────────────────────────────────────────────────────

def normalize_blok(raw):
    """'CK01' → 'CK1', 'JT04' → 'JT4'."""
    if not raw:
        return ''
    m = re.match(r'([A-Za-z]+)0*(\d+)', raw.strip())
    return f"{m.group(1).upper()}{m.group(2)}" if m else raw.strip().upper()
```

- [ ] **Step 4: Run tests — confirm they pass**

```
venv\Scripts\python manage.py test members.test.ParseDateTest members.test.NormalizeBlokTest
```

Expected: all 16 tests PASS.

- [ ] **Step 5: Commit**

```
git add members/importers.py members/test.py
git commit -m "feat: add parse_date and normalize_blok utilities to importers"
```

---

### Task 2: Field Normalizers + import_sensus_rows()

**Files:**
- Modify: `members/importers.py`
- Modify: `members/test.py`

- [ ] **Step 1: Add failing tests to `members/test.py`**

```python
from members.importers import import_sensus_rows


class ImportSensusRowsTest(TestCase):

    def _row(self, **overrides):
        """Build a minimal valid CSV row dict."""
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
            self._row(**{'Nama lengkap': ''}),  # skipped
        ]
        result = import_sensus_rows(rows)
        self.assertEqual(result.imported, 2)
        self.assertEqual(result.skipped, 1)
```

- [ ] **Step 2: Run tests — confirm they fail**

```
venv\Scripts\python manage.py test members.test.ImportSensusRowsTest
```

Expected: FAIL — `ImportError: cannot import name 'import_sensus_rows'`

- [ ] **Step 3: Add field normalizers and import_sensus_rows() to `members/importers.py`**

Append to `members/importers.py` after the `normalize_blok` function:

```python
# ── Field normalizers ───────────────────────────────────────────────────────

def _normalize_jenis_kelamin(val):
    v = val.strip().lower()
    if v in ('l', 'laki-laki', 'laki laki'):
        return 'L'
    if v in ('p', 'perempuan', 'permpuan', 'wanita'):
        return 'P'
    return ''


def _normalize_kategori_usia(val):
    lower = val.strip().lower()
    if lower.startswith('adiyuswa'):
        return 'Adiyuswa'
    if lower.startswith('keluarga muda'):
        return 'Keluarga Muda'
    if lower.startswith('pemuda'):
        return 'Pemuda'
    if lower.startswith('remaja'):
        return 'Remaja'
    if lower.startswith('anak'):
        return 'Anak'
    return 'Dewasa'


def _normalize_kewargaan(val):
    lower = val.strip().lower()
    if lower.startswith('simpatisan'):
        return 'Simpatisan'
    if lower.startswith('titipan'):
        return 'Titipan'
    if lower.startswith('tamu'):
        return 'Tamu'
    if lower.startswith('meninggal'):
        return 'Meninggal'
    if lower.startswith('warga tinggal') or lower.startswith('luar kota'):
        return 'Luar Kota'
    return 'Warga'


def _normalize_pendidikan(val):
    cleaned = val.strip().lower().replace('/sederajat', '').replace(' sederajat', '').strip()
    MAP = [
        ('tidak sekolah', 'Tidak Sekolah'), ('belum tamat', 'Tidak Sekolah'),
        ('belum sekolah', 'Tidak Sekolah'),
        ('sd', 'SD'), ('smp', 'SMP'), ('sma', 'SMA'),
        ('d1', 'D1'), ('d2', 'D2'), ('d3', 'D3'), ('d4', 'D4'),
        ('s1', 'S1'), ('s2', 'S2'), ('s3', 'S3'),
        ('mahasiswa', 'Lainnya'), ('kuliah', 'Lainnya'),
    ]
    for key, mapped in MAP:
        if cleaned.startswith(key):
            return mapped
    return 'Lainnya' if val.strip() else ''


def _normalize_ket_status(val):
    lower = val.strip().lower()
    if lower in ('kk', 'kepala keluarga'):
        return 'KK'
    if lower.startswith('istri'):
        return 'Istri'
    if lower.startswith('cucu'):
        return 'Cucu'
    if lower.startswith('nenek'):
        return 'Nenek'
    if lower.startswith('saudara'):
        return 'Saudara'
    if lower.startswith('anak'):
        return 'Anak'
    return 'Lainnya' if val.strip() else ''


def _normalize_status_perkawinan(val):
    lower = val.strip().lower()
    if lower.startswith('belum'):
        return 'Belum Menikah'
    if lower == 'menikah':
        return 'Menikah'
    if lower.startswith('janda'):
        return 'Janda'
    if lower.startswith('duda'):
        return 'Duda'
    if lower.startswith('single'):
        return 'Single Parent'
    return ''


def _normalize_status_rumah(val):
    lower = val.strip().lower()
    MAP = [
        ('milik sendiri', 'Milik Sendiri'),
        ('milik orang tua', 'Milik Orang Tua'),
        ('milik saudara', 'Milik Saudara'),
        ('milik nenek', 'Milik Orang Tua'),
        ('milik kakek', 'Milik Orang Tua'),
        ('kontrak', 'Kontrak'), ('sewa', 'Kontrak'),
        ('menumpang', 'Menumpang'),
        ('panti', 'Panti'),
    ]
    for key, mapped in MAP:
        if lower.startswith(key):
            return mapped
    return ''


def _normalize_tempat_kebaktian(val, nama_gereja):
    lower = val.strip().lower()
    if lower == 'induk':
        return 'Induk'
    if lower or nama_gereja.strip():
        return 'Gereja Lain'
    return ''


def _is_valid_sensus(val):
    if not val or val.strip().lower() in JUNK_VALUES:
        return False
    lower = val.strip().lower()
    reject = ('surat', 'baptis', 'sidhi', 'sidi', 'nikah', 'no/', 'no.')
    return not any(lower.startswith(r) for r in reject)


# ── Main import function ─────────────────────────────────────────────────────

def import_sensus_rows(rows):
    """Process a list of CSV row dicts. Returns ImportResult."""
    result = ImportResult()
    for row_num, raw_row in enumerate(rows, start=2):
        row = _normalize_row(raw_row)
        name = _clean(row.get('Nama lengkap', ''))
        if not name:
            result.skipped += 1
            continue
        try:
            _import_one(row, row_num, name, result)
        except Exception as exc:
            result.errors.append({'row': row_num, 'name': name, 'reason': str(exc)})
            result.skipped += 1
    return result


def _import_one(row, row_num, name, result):
    raw_sensus = _clean(row.get('No. induk gereja (lihat surat baptisi/sidhi/nikah)', ''))
    sensus = raw_sensus if _is_valid_sensus(raw_sensus) else None

    dob = parse_date(row.get('Tanggal lahir (tanggal/bulan/tahun)', ''))
    raw_blok = _clean(row.get('Blok (Kelompok PPA)', ''))
    blok = normalize_blok(raw_blok) if raw_blok else ''

    raw_gereja_lain = _clean(
        row.get('Jika di pertanyaan sebelumnya tempat kebaktian di gereja lain, isilah nama gerejanya dan kotanya', '')
    )
    baptis_oleh = _clean(row.get('Baptis oleh (nama pembaptis) (lihat surat baptis)', ''))
    sidi_oleh = _clean(row.get('sidhi oleh (nama pendeta) (lihat surat sidhi)', ''))

    fields = {
        'nama_lengkap': name,
        'jenis_kelamin': _normalize_jenis_kelamin(row.get('Jenis kelamin', '')),
        'tempat_lahir': _clean(row.get('Tempat lahir (sesuai KTP)', '')),
        'tanggal_lahir': dob,
        'nomor_telepon': _clean(row.get('No. telepon', '')),
        'alamat_domisili': _clean(row.get('Alamat domisili', '')),
        'alamat_ktp': _clean(row.get('Alamat sesuai KTP', '')),
        'status': _normalize_kategori_usia(row.get('Kategori usia', '')),
        'status_perkawinan': _normalize_status_perkawinan(row.get('Status perkawinan', '')),
        'kewargaan': _normalize_kewargaan(row.get('kategori kewargaan', '')),
        'gol_darah': _clean(row.get('Golongan darah', '')).upper()[:5],
        'pendidikan': _normalize_pendidikan(row.get('pendidikan terakhir', '')),
        'pekerjaan': _clean(row.get('pekerjaan', '')),
        'ket_status': _normalize_ket_status(row.get('status dalam keluarga', '')),
        'status_rumah_tinggal': _normalize_status_rumah(row.get('Status rumah tinggal', '')),
        'tempat_kebaktian': _normalize_tempat_kebaktian(
            row.get('Tempat kebaktian', ''), raw_gereja_lain
        ),
        'nama_gereja_lain': raw_gereja_lain,
        'sudah_baptis': bool(baptis_oleh),
        'baptis_oleh': baptis_oleh,
        'tanggal_baptis': parse_date(row.get('tanggal baptis (lihat surat baptis)', '')),
        'tempat_baptis': _clean(row.get('tempat baptis (nama gereja) (lihat surat baptis)', '')),
        'sudah_sidi': bool(sidi_oleh),
        'sidi_oleh': sidi_oleh,
        'tanggal_sidi': parse_date(row.get('tanggal sidhi (lihat surat sidhi)', '')),
        'tempat_sidi': _clean(row.get('tempat sidhi (nama gereja) (lihat surat sidhi)', '')),
        'nikah_oleh': _clean(row.get('nikah oleh (lihat surat nikah)', '')),
        'tanggal_nikah': parse_date(row.get('tanggal nikah (lihat surat nikah)', '')),
        'tempat_nikah': _clean(row.get('tempat nikah (nama gereja/kota)', '')),
        'minat_pelayanan_gerejawi': _clean(row.get('Minat pelayanan gerejawi', '')),
        'minat_pelayanan_umum': _clean(row.get('minat pelayanan umum', '')),
    }

    # Keluarga: find-or-create if a valid KK number is provided
    raw_kk = _clean(row.get('No. KK (Kartu Kewargaan gereja) (diisi petugas)', ''))
    keluarga = None
    if raw_kk and _is_valid_sensus(raw_kk):
        keluarga, _ = Keluarga.objects.get_or_create(
            no_kk_gereja=raw_kk,
            defaults={
                'nama_keluarga': name,
                'blok': blok or 'CK1',
                'alamat': fields['alamat_ktp'] or fields['alamat_domisili'] or '-',
            },
        )
    fields['keluarga'] = keluarga

    # Upsert
    if sensus:
        _, created = Member.objects.update_or_create(no_sensus=sensus, defaults=fields)
    else:
        # Fall back to name + dob match
        member = None
        if dob:
            member = Member.objects.filter(
                nama_lengkap__iexact=name, tanggal_lahir=dob
            ).first()
        if member:
            for k, v in fields.items():
                setattr(member, k, v)
            member.save()
            created = False
        else:
            # Generate unique temp sensus
            temp = f'IMPORT-{row_num:04d}'
            n = 1
            while Member.objects.filter(no_sensus=temp).exists():
                temp = f'IMPORT-{row_num:04d}-{n}'
                n += 1
            Member.objects.create(no_sensus=temp, **fields)
            created = True

    if created:
        result.imported += 1
    else:
        result.updated += 1
```

- [ ] **Step 4: Run tests — confirm they pass**

```
venv\Scripts\python manage.py test members.test.ImportSensusRowsTest
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Run full test suite**

```
venv\Scripts\python manage.py test members website
```

Expected: all pass.

- [ ] **Step 6: Commit**

```
git add members/importers.py members/test.py
git commit -m "feat: add import_sensus_rows() with field normalizers"
```

---

### Task 3: CsvImportForm

**Files:**
- Modify: `members/forms.py`
- Modify: `members/test.py`

- [ ] **Step 1: Add failing test to `members/test.py`**

```python
from members.forms import CsvImportForm


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
```

- [ ] **Step 2: Run tests — confirm they fail**

```
venv\Scripts\python manage.py test members.test.CsvImportFormTest
```

Expected: FAIL — `ImportError: cannot import name 'CsvImportForm'`

- [ ] **Step 3: Add CsvImportForm to `members/forms.py`**

Append to the existing `members/forms.py` (keep `MemberForm` unchanged):

```python
class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='File CSV Sensus',
        help_text='File .csv dari Google Form Sensus Warga GKJ Salatiga',
    )
```

- [ ] **Step 4: Run tests — confirm they pass**

```
venv\Scripts\python manage.py test members.test.CsvImportFormTest
```

Expected: PASS.

- [ ] **Step 5: Commit**

```
git add members/forms.py members/test.py
git commit -m "feat: add CsvImportForm to members/forms.py"
```

---

### Task 4: Admin Templates

**Files:**
- Create: `members/templates/admin/members/member/changelist.html`
- Create: `members/templates/admin/members/member/import_sensus.html`
- Create: `members/templates/admin/members/member/import_result.html`

No unit tests for templates — verified by the admin view integration test in Task 5.

- [ ] **Step 1: Create the template directory**

```
mkdir members\templates\admin\members\member
```

- [ ] **Step 2: Create `members/templates/admin/members/member/changelist.html`**

```html
{% extends "admin/change_list.html" %}
{% block object-tools-items %}
  <li>
    <a href="import-sensus/" class="addlink">Import Sensus CSV</a>
  </li>
  {{ block.super }}
{% endblock %}
```

- [ ] **Step 3: Create `members/templates/admin/members/member/import_sensus.html`**

```html
{% extends "admin/base_site.html" %}
{% load i18n %}

{% block content %}
<h1>Import Sensus CSV</h1>
<p>Unggah file .csv dari Google Form Sensus Warga GKJ Salatiga.</p>

<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  <table>{{ form.as_table }}</table>
  <p style="margin-top: 1rem;">
    <input type="submit" value="Import" class="button default">
    &nbsp;
    <a href="../">Batal</a>
  </p>
</form>
{% endblock %}
```

- [ ] **Step 4: Create `members/templates/admin/members/member/import_result.html`**

```html
{% extends "admin/base_site.html" %}

{% block content %}
<h1>Import Selesai</h1>

<p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
  ✅ Anggota baru: <strong>{{ result.imported }}</strong>
  &nbsp;&nbsp;
  🔄 Diperbarui: <strong>{{ result.updated }}</strong>
  &nbsp;&nbsp;
  ⏭ Dilewati: <strong>{{ result.skipped }}</strong>
</p>

{% if result.errors %}
<h2>Baris dengan masalah ({{ result.errors|length }})</h2>
<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr>
      <th style="text-align: left; padding: 0.5rem; border-bottom: 1px solid #ccc;">Baris</th>
      <th style="text-align: left; padding: 0.5rem; border-bottom: 1px solid #ccc;">Nama</th>
      <th style="text-align: left; padding: 0.5rem; border-bottom: 1px solid #ccc;">Alasan</th>
    </tr>
  </thead>
  <tbody>
    {% for err in result.errors %}
    <tr>
      <td style="padding: 0.4rem 0.5rem;">{{ err.row }}</td>
      <td style="padding: 0.4rem 0.5rem;">{{ err.name }}</td>
      <td style="padding: 0.4rem 0.5rem; color: #ba2121;">{{ err.reason }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
<p style="color: green;">Tidak ada kesalahan.</p>
{% endif %}

<p style="margin-top: 2rem;">
  <a href="../" class="button">Kembali ke Daftar Member</a>
</p>
{% endblock %}
```

- [ ] **Step 5: Commit**

```
git add members/templates/
git commit -m "feat: add admin templates for CSV import (changelist, form, result)"
```

---

### Task 5: Admin View Integration

**Files:**
- Modify: `members/admin.py`
- Modify: `members/test.py`

- [ ] **Step 1: Add failing integration tests to `members/test.py`**

```python
import csv
import io
from django.contrib.auth.models import User
from django.urls import reverse


class CsvImportAdminViewTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin', password='pass', email='a@a.com'
        )
        self.client.login(username='admin', password='pass')

    def _csv_bytes(self, rows=None):
        """Build a minimal valid CSV file as bytes."""
        if rows is None:
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```
venv\Scripts\python manage.py test members.test.CsvImportAdminViewTest
```

Expected: FAIL — `NoReverseMatch` for `admin:members_member_import_sensus`

- [ ] **Step 3: Replace `members/admin.py` with the full updated version**

```python
import csv
import io

from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from .forms import CsvImportForm
from .importers import import_sensus_rows
from .models import (
    Keluarga, Member, Majelis,
    IbadahMingguan, IbadahService,
    Perpuluhan, IuranPralenan, MemberStatusHistory,
)


class IbadahServiceInline(admin.TabularInline):
    model = IbadahService
    extra = 1


@admin.register(IbadahMingguan)
class IbadahMingguanAdmin(admin.ModelAdmin):
    list_display = ['tanggal', 'minggu_ke']
    inlines = [IbadahServiceInline]


@admin.register(Keluarga)
class KeluargaAdmin(admin.ModelAdmin):
    list_display = ['nama_keluarga', 'blok', 'no_kk_gereja']
    list_filter = ['blok']
    search_fields = ['nama_keluarga']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['nama_lengkap', 'kewargaan', 'jenis_kelamin', 'tanggal_lahir']
    search_fields = ['nama_lengkap', 'no_sensus']
    list_filter = ['kewargaan', 'jenis_kelamin', 'sudah_baptis', 'sudah_sidi']
    change_list_template = 'admin/members/member/changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'import-sensus/',
                self.admin_site.admin_view(self.import_sensus_view),
                name='members_member_import_sensus',
            ),
        ]
        return custom + urls

    def import_sensus_view(self, request):
        if request.method == 'POST':
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                decoded = csv_file.read().decode('utf-8-sig')  # handles Excel BOM
                reader = csv.DictReader(io.StringIO(decoded))
                result = import_sensus_rows(list(reader))
                return render(
                    request,
                    'admin/members/member/import_result.html',
                    {'result': result, **self.admin_site.each_context(request)},
                )
        else:
            form = CsvImportForm()
        return render(
            request,
            'admin/members/member/import_sensus.html',
            {'form': form, **self.admin_site.each_context(request)},
        )


@admin.register(Majelis)
class MajelisAdmin(admin.ModelAdmin):
    list_display = ['member', 'jabatan', 'aktif']
    list_filter = ['jabatan', 'aktif']


@admin.register(Perpuluhan)
class PerpuluhanAdmin(admin.ModelAdmin):
    list_display = ['member', 'tanggal', 'jumlah']
    search_fields = ['member__nama_lengkap']


@admin.register(IuranPralenan)
class IuranPralenanAdmin(admin.ModelAdmin):
    list_display = ['member', 'tanggal', 'jumlah']
    search_fields = ['member__nama_lengkap']


@admin.register(MemberStatusHistory)
class MemberStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'status_lama', 'status_baru', 'tanggal']
```

- [ ] **Step 4: Run integration tests — confirm they pass**

```
venv\Scripts\python manage.py test members.test.CsvImportAdminViewTest
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Run full test suite**

```
venv\Scripts\python manage.py test members website
```

Expected: all pass.

- [ ] **Step 6: Commit**

```
git add members/admin.py members/test.py
git commit -m "feat: add CSV import admin view for sensus warga"
```

---

## Summary

| Task | Files | Tests |
|---|---|---|
| 1 | `importers.py` (utilities) | 16 |
| 2 | `importers.py` (main logic) | 9 |
| 3 | `forms.py` | 2 |
| 4 | 3 admin templates | — |
| 5 | `admin.py` | 4 |

**How to use after implementation:**

1. Open `http://127.0.0.1:8000/admin/members/member/`
2. Click **Import Sensus CSV**
3. Upload the `.csv` file from Google Form
4. Review the results page — check the error table for rows that need manual attention
