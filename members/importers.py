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
    '%d/%m/%y', '%d-%m-%y', '%d %m %Y', '%d %m %y',
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
        lower = re.sub(r'\b' + name + r'\b', num, lower)

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
    """'CK01' -> 'CK1', 'JT04' -> 'JT4'."""
    if not raw:
        return ''
    m = re.match(r'([A-Za-z]+)0*(\d+)', raw.strip())
    return f"{m.group(1).upper()}{m.group(2)}" if m else raw.strip().upper()


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
