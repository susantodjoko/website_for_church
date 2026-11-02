# Bacaan Harian: Daily Bible Reading Page

## Problem

The Sinode GKJ publishes a yearly *Daftar Bacaan Harian*: for every day, a first reading, a psalm (tanggapan), a second reading, and on Sundays and feast days also a Gospel reading, a theme and the liturgical colour. Members currently get it as a Word/PDF file ([docs/DAFTAR BACAAN HARIAN 2026, Sinode GKJ.pdf](../../DAFTAR%20BACAAN%20HARIAN%202026,%20Sinode%20GKJ.pdf)). The website should show the readings day by day, so that clicking a day shows that day's verses.

## Status (2026-11-02)

The demo is built locally (references with links to SABDA). It is **not committed and not deployed**. Showing the verse text inline is waiting on permission from LAI (see *Licensing* below).

## Licensing: why the text isn't on our site (yet)

The readings use LAI's Terjemahan Baru (TB), which is copyrighted. LAI's rules ([alkitab.or.id/tentang-kami/penggunaan-teks](https://www.alkitab.or.id/tentang-kami/penggunaan-teks)) allow free non-commercial church use only within these limits:

- **no more than 1,000 verses**, and
- **not a whole book** of the Bible,
- with the notice **"Dikutip dari ALKITAB (TB) © LAI 1974"** at the end of the quote.

A full year of readings is roughly 10,000+ verses and includes whole books (Filemon on 2 Feb, 2 Yohanes on 9 Mar), so showing the text on our site needs LAI's written permission. LAI's site terms also forbid copying its content into a database or scraping it.

Because of this, the feature is built in two phases:

1. **Phase 1 (built):** the site shows the references only. Each reference links to the passage on alkitab.sabda.org, which shows TB. A link doesn't copy any text, so no permission is needed.
2. **Phase 2 (after permission):** clicking a day shows the TB text on our page, fetched from LAI's official Bible API (`bible-api.alkitab.or.id`). The API needs a key: write to info@alkitab.or.id with the subject "Permohonan akses Bible API", which also serves as the permission request. Also ask whether we may cache the text on our server. Plan for phase 2:
   - fetch only when a day is opened, never during page load;
   - cache each passage after the first fetch (if LAI allows), since the readings are fixed for the year;
   - use a short timeout (~3 s) and fall back to the SABDA link if the API is slow or down;
   - show the required © LAI notice under the text.

   Only the part that produces the text changes. The model, the import and the page layout stay as they are.

## Phase 1 design

### Where it appears

- **`/bacaan/`**, linked from the navbar as "Bacaan" (after Publikasi). It shows one week, Monday to Sunday, and opens on the current week. Each day is a `<details>` element; today is open and marked "Hari ini". "Minggu lalu" / "Minggu depan" step through weeks with `?minggu=YYYY-MM-DD` (any date in the week). The month's theme is shown at the top, and if a week spans two months both themes are shown.
- **Home page:** a "Bacaan Hari Ini" strip just below the hero with today's readings (first alternative of each) and a link to the week page. It's hidden when there's no data for today.

"Today" is calculated in Asia/Jakarta time (`_jakarta_today()` in `website/views.py`). The server's `TIME_ZONE` is UTC, so without this the reading would only change at 07:00 WIB. The site's locale is `en-us`, so day and month names come from the `HARI` / `BULAN` lists in the view.

### Data model (`website/models.py`, migration `0021_bacaan_harian`)

**`BacaanHarian`**: one row per service per day.

| Field | Notes |
|---|---|
| `tanggal` | Date. Not unique: 1 Jan, 29 Mar and 5 Apr 2026 have two services. |
| `urutan` | Order within the date (0, 1). |
| `keterangan` | e.g. "Minggu Adven I", "Paskah Sore". Several labels are joined with " · ". |
| `warna` | Liturgical colour, e.g. "Putih atau Hijau". |
| `bacaan_1`, `tanggapan`, `bacaan_2`, `injil` | References as printed. Alternatives are kept as "A atau B". |
| `tema` | The day's theme (Sundays and feast days). |

`readings()` returns `[(label, [(ref, sabda_url), ...]), ...]`, skips empty fields, and splits "atau" into separate choices. The psalm (`tanggapan`) is imported and stored but deliberately **not shown** on the site, at the user's request (2026-11-02). Add it back to the list in `readings()` to show it again.

**`TemaBulan`**: `tahun`, `bulan`, `tema`, `keterangan` (e.g. "Bulan Keluarga"), unique per year and month.

Both models are registered on the default admin and on the content admin.

### SABDA links (`sabda_url()` in `website/models.py`)

These URLs have the form `https://alkitab.sabda.org/passage.php?passage=<ref>`. We tested this endpoint with plain Indonesian book names, multiple ranges (`Rut 3:1-13;4:13-22`, `Mazmur 72:1-7,10-14`) and whole books. The function normalises the printed references:

- "Kisah Pr. Rasul" becomes "Kisah Para Rasul".
- Optional verses in parentheses are kept, so "Yohanes 1: (1-9), 10-18" becomes `Yohanes 1:1-9,10-18`.
- A new chapter after a comma gets `;`, so "3:16-22, 4:18-20" becomes `3:16-22;4:18-20`.
- Half-verse letters are dropped (`14a` → `14`).
- Single-chapter books get `1:`, so "3 Yohanes 9-12" becomes `3 Yohanes 1:9-12`.

### Data pipeline

The source is the `.doc` file. Plain text extraction (antiword, pdftotext) is unreliable: antiword drops every other table row, and the PDF columns come out jumbled. So the tables are read through Microsoft Word.

1. **Dump the tables** (Windows with Word installed):
   ```
   powershell -File scripts/bacaan/dump_word_tables.ps1 -Doc "<full path to .doc>" -Out cells.tsv
   ```
2. **Convert to CSV:**
   ```
   python scripts/bacaan/cells_to_csv.py cells.tsv website/data/bacaan_2026.csv website/data/tema_bulan_2026.csv
   ```
   The script checks that every weekday name matches its date and prints each correction it made. It also handles:
   - label rows that a page break split off (e.g. "(HITAM)", "Tutup Tahun"), which are merged into the row above;
   - rows without a date that have readings ("Paskah Sore"), which become a second service on the previous date.
3. **Import:**
   ```
   python manage.py import_bacaan website/data/bacaan_2026.csv --tema-bulan website/data/tema_bulan_2026.csv
   ```
   The import replaces existing rows for the dates in the file, so it is safe to run again.

The generated CSVs are committed, so the server only needs step 3.

### Corrections made to the 2026 source

Applied by `cells_to_csv.py`:

- **Dates:** "Jumat." → "Jumat," (16 Jan, 6 Feb), "20206" → 2026 (20 Mei), "Oktober 2025" → 2026 (4 Okt), "Oktpber" (27 Okt), "oktober" (31 Okt).
- **References:**
  - "Kolose 16:9-21" → Keluaran 16:9-21 (6 Mar; Kolose has 4 chapters, and the week reads Keluaran 16)
  - "Tesalonika 4:9-12" → 1 Tesalonika (29 Jun)
  - "Mazmur 80:7-1" → 80:7-15 (1 Okt)
  - "Yabobus" → Yakobus (27 Okt)
- **Columns:** on 9–11 Juli the psalm and the first reading were in swapped columns.
- **Spelling:** "Masmur", missing spaces ("Mazmur33"), "Kisah. Pr. Rasul", Roman numerals ("I Samuel" → "1 Samuel"), "MInggu", "Kristenn".

**Still to check with the source / Sinode** (left as printed):

- 15 Juni: "Tesalonika 3:1-5" (1 or 2 Tesalonika?)
- 25 Juli: "1 Raja-raja 1" and "Raja-raja 2:1-4" look garbled
- 11 Juli: the readings repeat 10 Juli's
- 12 Des: "Mazmur 26", where the rest of the week is Mazmur 126

These can be fixed in the admin, or in the CSV followed by a re-import.

### Files

- `website/models.py`: `sabda_url`, `BacaanHarian`, `TemaBulan`
- `website/migrations/0021_bacaan_harian.py`
- `website/views.py`: `bacaan`, `_jakarta_today`, `bacaan_today` in `home`
- `website/urls.py`: `bacaan/`
- `website/admin.py`: `BacaanHarianAdmin`, `TemaBulanAdmin`
- `website/templates/website/bacaan.html`; home strip in `home.html`; navbar link in `templates/base.html`
- `static/css/style.css`: "BACAAN HARIAN" section (CSS version bumped to `?v=2026-11-02a`)
- `website/management/commands/import_bacaan.py`
- `website/data/bacaan_2026.csv`, `website/data/tema_bulan_2026.csv`
- `scripts/bacaan/dump_word_tables.ps1`, `scripts/bacaan/cells_to_csv.py`
- `website/tests.py`: `BacaanHarianTest`

## Deploying (when approved)

Follow the usual VPS steps (back up the DB first, because there is a migration), then add the import:

```
venv/bin/python manage.py migrate
venv/bin/python manage.py import_bacaan website/data/bacaan_2026.csv --tema-bulan website/data/tema_bulan_2026.csv
```

## Next year

When the Sinode publishes the 2027 list:

1. Run steps 1–3 of the pipeline on the new `.doc`.
2. Read the correction log and check the result by eye.
3. Review `REF_FIXES` in `cells_to_csv.py`, because its typo fixes are specific to 2026.
