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
