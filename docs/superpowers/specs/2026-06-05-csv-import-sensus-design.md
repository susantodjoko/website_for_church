# CSV Import — Sensus Warga Design

**Date:** 2026-06-05
**Scope:** Django admin upload view for importing GKJ Salatiga member census CSV data
**Files affected:** `members/importers.py` (new), `members/forms.py` (new), `members/admin.py`, 2 admin templates

---

## 1. Architecture

Three components, cleanly separated:

```
members/
├── importers.py          ← pure import logic (no HTTP, fully testable)
├── forms.py              ← CsvImportForm with FileField
├── admin.py              ← custom view + button on Member changelist
└── templates/admin/members/member/
    ├── changelist.html        ← extends default, adds Import button
    ├── import_sensus.html     ← upload form page
    └── import_result.html     ← results summary page
```

**Flow:**
1. Admin opens Member list → clicks **Import Sensus CSV** button
2. Uploads CSV file → submits form
3. Django reads file in-memory (no disk write), passes rows to `importers.py`
4. Results page shows: imported N / updated M / skipped K + error table

**`ImportResult` dataclass returned by importer:**
```python
@dataclass
class ImportResult:
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list = field(default_factory=list)
    # errors format: [{'row': N, 'name': '...', 'reason': '...'}]
```

The import logic has no HTTP dependency — takes a list of row dicts, returns `ImportResult`. Can be called from a management command later.

---

## 2. Import Logic (`members/importers.py`)

**Public function:** `import_sensus_rows(rows: list[dict]) -> ImportResult`

Each `dict` in `rows` is one CSV row keyed by column header (as returned by `csv.DictReader`).

### CSV Column → Model Field Mapping

| CSV column | Member field | Normalization |
|---|---|---|
| `No. induk gereja` | `no_sensus` | Key for upsert; empty/invalid → auto `IMPORT-{N}` |
| `Nama lengkap` | `nama_lengkap` | Strip whitespace |
| `Jenis kelamin` | `jenis_kelamin` | "laki-laki" → `L`, "permpuan"/"perempuan" → `P` |
| `Tempat lahir` | `tempat_lahir` | Strip |
| `Tanggal lahir` | `tanggal_lahir` | Multi-format parser |
| `Alamat domisili` | `alamat_domisili` | |
| `No. telepon` | `nomor_telepon` | |
| `Alamat sesuai KTP` | `alamat_ktp` | |
| `Blok` | → `Keluarga.blok` | "CK01" → "CK1" |
| `Status perkawinan` | `status_perkawinan` | Title-case match |
| `Kategori usia` | `status` | Prefix match (see below) |
| `kategori kewargaan` | `kewargaan` | Title-case match |
| `Golongan darah` | `gol_darah` | Uppercase |
| `pendidikan terakhir` | `pendidikan` | Normalise /sederajat suffix |
| `No. KK` | → `Keluarga.no_kk_gereja` | find-or-create Keluarga |
| `status dalam keluarga` | `ket_status` | "kepala keluarga" → "KK" |
| `pekerjaan` | `pekerjaan` | |
| `Status rumah tinggal` | `status_rumah_tinggal` | Title-case match |
| `Tempat kebaktian` | `tempat_kebaktian` | "induk" → "Induk" |
| `Jika di pertanyaan sebelumnya...` | `nama_gereja_lain` | |
| `Baptis oleh` | `baptis_oleh` | Non-empty also sets `sudah_baptis=True` |
| `tanggal baptis` | `tanggal_baptis` | Multi-format parser |
| `tempat baptis` | `tempat_baptis` | |
| `sidhi oleh` | `sidi_oleh` | Non-empty also sets `sudah_sidi=True` |
| `tanggal sidhi` | `tanggal_sidi` | Multi-format parser |
| `tempat sidhi` | `tempat_sidi` | |
| `nikah oleh` | `nikah_oleh` | |
| `tanggal nikah` | `tanggal_nikah` | Multi-format parser |
| `tempat nikah` | `tempat_nikah` | |
| `Minat pelayanan gerejawi` | `minat_pelayanan_gerejawi` | |
| `minat pelayanan umum` | `minat_pelayanan_umum` | |

### Date Parser

Tries formats in order, returns `None` if all fail (row continues, date left blank):

```python
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
# Also handles:
# - "29 Januari 1956" / "08 MEI 1976" → replace Indonesian month name → strptime
# - "14051973" (8 raw digits) → DDMMYYYY
# - Strips extra spaces, dashes, dots before trying
```

### Blok Normalization

```python
import re
def normalize_blok(raw: str) -> str:
    m = re.match(r'([A-Za-z]+)0*(\d+)', raw.strip())
    return f"{m.group(1).upper()}{m.group(2)}" if m else raw.upper()
# "CK01" → "CK1",  "JT04" → "JT4",  "JB02" → "JB2"
```

### Kategori Usia Normalization

```python
USIA_MAP = {
    'anak': 'Anak',
    'remaja': 'Remaja',
    'pemuda': 'Pemuda',
    'keluarga muda': 'Keluarga Muda',
    'dewasa': 'Dewasa',
    'adiyuswa': 'Adiyuswa',
}
# Match by lowercase prefix of the CSV value
```

### Upsert Strategy

1. If `no_sensus` is non-empty and not a placeholder (`-`, `--`, placeholder text):
   → `Member.objects.update_or_create(no_sensus=sensus, defaults={...})`
2. If empty/invalid:
   → Try `Member.objects.filter(nama_lengkap__iexact=name, tanggal_lahir=dob).first()`
   → If found: update. If not: create with `no_sensus = f"IMPORT-{row_number}"`

### Keluarga Handling

If `No. KK` column is non-empty and not a placeholder:
```python
Keluarga.objects.get_or_create(
    no_kk_gereja=kk,
    defaults={
        'nama_keluarga': nama_lengkap,
        'blok': blok,
        'alamat': alamat_ktp or alamat_domisili,
    }
)
```
If `No. KK` is empty: `member.keluarga = None`.

### Pendidikan Normalization

```python
PENDIDIKAN_MAP = {
    'tidak sekolah': 'Tidak Sekolah',
    'belum tamat sd': 'Tidak Sekolah',
    'sd': 'SD', 'smp': 'SMP', 'sma': 'SMA',
    'd1': 'D1', 'd2': 'D2', 'd3': 'D3', 'd4': 'D4',
    's1': 'S1', 's2': 'S2', 's3': 'S3',
    'mahasiswa': 'Lainnya', 'kuliah': 'Lainnya',
}
# Match by stripping "/sederajat" suffix then lowercase lookup
```

---

## 3. Admin UI

### URL
`/admin/members/member/import-sensus/`

### Upload page (`import_sensus.html`)
Extends `admin/base_site.html`. Contains:
- Page title: "Import Sensus CSV"
- Single `<form enctype="multipart/form-data">` with `CsvImportForm`
- Submit button: "Import"

### Results page (`import_result.html`)
Extends `admin/base_site.html`. Shows:
- Summary counts: Imported N / Updated M / Skipped K
- Error table (row number, name, reason) — only shown if errors > 0
- "Back to Member List" link

### Button on changelist (`changelist.html`)
Extends `admin/change_list.html`:
```html
{% block object-tools-items %}
  <li>
    <a href="import-sensus/" class="addlink">Import Sensus CSV</a>
  </li>
  {{ block.super }}
{% endblock %}
```

### Admin view registration (`members/admin.py`)
```python
class MemberAdmin(admin.ModelAdmin):
    change_list_template = 'admin/members/member/changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom = [path('import-sensus/', self.admin_site.admin_view(self.import_sensus_view))]
        return custom + urls

    def import_sensus_view(self, request):
        if request.method == 'POST':
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                decoded = csv_file.read().decode('utf-8-sig')  # handles BOM from Excel
                reader = csv.DictReader(io.StringIO(decoded))
                result = import_sensus_rows(list(reader))
                return render(request, 'admin/members/member/import_result.html',
                              {'result': result, **self.admin_site.each_context(request)})
        else:
            form = CsvImportForm()
        return render(request, 'admin/members/member/import_sensus.html',
                      {'form': form, **self.admin_site.each_context(request)})
```

### `CsvImportForm` (`members/forms.py`)
```python
class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='File CSV',
        help_text='Format: Google Form Sensus Warga GKJ Salatiga (.csv)'
    )
```

---

## 4. Error Handling

- A row is **skipped** only if `nama_lengkap` is empty (can't create a nameless member)
- Date parse failures: field left `None`, row still imported, error noted in result
- Unknown blok: field left blank, error noted
- All other field failures: best-effort import, error noted
- Exception during a row: row skipped, exception message in error list, import continues

---

## 5. Testing Checklist

- [ ] Upload a valid CSV → correct imported/updated counts
- [ ] Upload same CSV again → all rows show as "updated", count matches
- [ ] Row with empty no_sensus → gets `IMPORT-{N}` and is created
- [ ] Row with duplicate no_sensus → existing record updated
- [ ] Row with unparseable date → imported with `tanggal_lahir=None`, error noted
- [ ] Row with blok "CK01" → normalized to "CK1"
- [ ] Row with empty nama_lengkap → skipped, counted in skipped
- [ ] CSV with Windows BOM (Excel export) → handled correctly
- [ ] Import button visible on Member changelist in admin
