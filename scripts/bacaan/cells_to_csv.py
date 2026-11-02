"""Turn the Word table dump of the Sinode GKJ "Daftar Bacaan Harian" into
the two CSV files that `manage.py import_bacaan` reads.

Step 1 (Windows, needs Microsoft Word):
    powershell -File scripts/bacaan/dump_word_tables.ps1 -Doc "<full path>.doc" -Out cells.tsv
Step 2:
    python scripts/bacaan/cells_to_csv.py cells.tsv website/data/bacaan_2026.csv website/data/tema_bulan_2026.csv

The source document has typos and a few broken rows; the fixes below are
specific to the 2026 list and are printed so they can be checked by eye.
"""
import csv
import re
import sys
from collections import defaultdict
from datetime import date

MONTHS = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'oktpber': 10,
    'november': 11, 'desember': 12,
}
MONTH_NAMES = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
               'Agustus', 'September', 'Oktober', 'November', 'Desember']
DAYS = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']
DATE_RE = re.compile(r'^(\w+)[.,]?\s+(\d{1,2})\s+(\w+)\s+(\d{4,5})$', re.I)
THEME_RE = re.compile(r'^Tema (\w+) (\d{4}):\s*(.+)$')

# Exact-cell corrections for clear typos in the 2026 source.
REF_FIXES = {
    'Kolose 16:9-21': 'Keluaran 16:9-21',        # 6 Mar, between Keluaran 16:1-8 and 16:27-35
    'Mazmur 80:7-1': 'Mazmur 80:7-15',           # 1 Okt, rest of the week is 80:7-15
    'Tesalonika 4:9-12': '1 Tesalonika 4:9-12',  # 29 Jun, 2 Tesalonika has 3 chapters
    'Yabobus 2:14-26': 'Yakobus 2:14-26',
}

fixes_log = []


def clean_ref(text):
    text = re.sub(r'\s*/\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().rstrip(';').strip()
    text = text.replace('Masmur', 'Mazmur')
    text = re.sub(r'^Kisah\.? Pr\.? ?Rasul ?', 'Kisah Pr. Rasul ', text)
    text = re.sub(r'(atau |; )Kisah\.? Pr\.? ?Rasul ?', r'\1Kisah Pr. Rasul ', text)
    text = re.sub(r'([a-z])(\d)', r'\1 \2', text)          # Mazmur33 -> Mazmur 33
    text = re.sub(r'(^|atau |; )III ', r'\g<1>3 ', text)
    text = re.sub(r'(^|atau |; )II ', r'\g<1>2 ', text)
    text = re.sub(r'(^|atau |; )I ', r'\g<1>1 ', text)
    text = re.sub(r'(^|atau |; )(\d) raja-raja', r'\1\2 Raja-raja', text)
    if text in REF_FIXES:
        fixes_log.append(f'  ref: {text!r} -> {REF_FIXES[text]!r}')
        text = REF_FIXES[text]
    return text


def parse_date(line):
    m = DATE_RE.match(line.strip())
    if not m:
        return None
    day_name, day, month, year = m.groups()
    year = int(year)
    if year == 20206:
        year = 2026
    if year == 2025:  # "Minggu, 4 Oktober 2025" in a 2026 list
        year = 2026
    d = date(year, MONTHS[month.lower()], int(day))
    if DAYS[d.weekday()] != day_name.lower():
        raise ValueError(f'weekday mismatch: {line!r} is a {DAYS[d.weekday()]}')
    canonical = f'{day_name}, {int(day)} {MONTH_NAMES[d.month - 1]} {d.year}'
    if line.strip() != canonical:
        fixes_log.append(f'  date: {line.strip()!r} -> {d.isoformat()}')
    return d


def split_label(parts):
    labels, colour = [], ''
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith('(') and p.endswith(')'):
            colour = p[1:-1].strip().title().replace(' Atau ', ' atau ')
        else:
            labels.append(p.replace('MInggu', 'Minggu'))
    return ' · '.join(labels), colour


def main(cells_path, readings_out, themes_out):
    tables, rows = [], defaultdict(dict)
    with open(cells_path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line == '---TABLE---':
                tables.append(rows)
                rows = defaultdict(dict)
                continue
            r, c, text = line.split('\t', 2)
            rows[int(r)][int(c)] = text

    readings, themes = [], []
    for table in tables:
        for r in sorted(table):
            cells = table[r]
            first = cells.get(1, '').strip()
            m = THEME_RE.match(first.split(' / ')[0])
            if m:
                month, year, tema = m.groups()
                extra = ' '.join(first.split(' / ')[1:]).strip()
                themes.append([year, MONTHS[month.lower()], tema.strip(), extra.title()])
                continue
            if first.startswith('HARI, TANGGAL') or not first:
                continue
            parts = first.split(' / ')
            refs = [clean_ref(cells.get(c, '')) for c in (2, 3, 4, 5)]
            tema = re.sub(r'\s*/\s*', ' ', cells.get(6, '')).strip()
            tema = re.sub(r'\s+', ' ', tema).replace('Kristenn', 'Kristen')
            d = parse_date(parts[0])
            if d is None:
                label, colour = split_label(parts)
                if any(refs):
                    # A second service on the previous date (e.g. "Paskah Sore")
                    readings.append([readings[-1][0], label, colour, *refs, tema])
                else:
                    # Label row split off by a page break: belongs to the row above
                    prev = readings[-1]
                    prev[1] = ' · '.join(x for x in (prev[1], label) if x)
                    prev[2] = prev[2] or colour
                continue
            label, colour = split_label(parts[1:])
            if refs[0].startswith('Mazmur') and not refs[1].startswith('Mazmur'):
                # 9-11 Juli: the psalm and the first reading are in swapped columns
                fixes_log.append(f'  swap: {d} {refs[0]!r} <-> {refs[1]!r}')
                refs[0], refs[1] = refs[1], refs[0]
            readings.append([d, label, colour, *refs, tema])

    order = defaultdict(int)
    with open(readings_out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['tanggal', 'urutan', 'keterangan', 'warna',
                    'bacaan_1', 'tanggapan', 'bacaan_2', 'injil', 'tema'])
        for row in readings:
            d = row[0]
            w.writerow([d.isoformat(), order[d], *row[1:]])
            order[d] += 1
    with open(themes_out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['tahun', 'bulan', 'tema', 'keterangan'])
        w.writerows(themes)

    dates = sorted(order)
    print(f'{len(readings)} readings over {len(dates)} days '
          f'({dates[0]} .. {dates[-1]}), {len(themes)} monthly themes')
    print('Corrections applied:')
    print('\n'.join(fixes_log) or '  none')


if __name__ == '__main__':
    main(*sys.argv[1:4])
