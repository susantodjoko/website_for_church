# Member Detail Tabs + Dashboard Improvements Design

**Date:** 2026-06-05
**Scope:** Reorganise member detail page into 4 tabs; add age distribution and birthday widget to staff dashboard
**Audience:** Staff only (roles to be designed separately later)
**Files affected:** `member_detail.html`, `dashboard.html`, `members/views.py`, `static/css/style.css`

---

## 1. Member Detail — Tab Structure

Four tabs using vanilla JS tab switching. Default active tab on load: **Data Pribadi**.

```
[ Data Pribadi ]  [ Iman ]  [ Pelayanan ]  [ Riwayat ]
```

### Tab 1: Data Pribadi
Personal and household information:

| Field | Display label |
|---|---|
| `jenis_kelamin` | Jenis Kelamin |
| `tempat_lahir` + `tanggal_lahir` | Tempat, Tanggal Lahir |
| `status` | Kategori Usia |
| `status_perkawinan` | Status Perkawinan |
| `gol_darah` | Golongan Darah |
| `pendidikan` | Pendidikan |
| `pekerjaan` | Pekerjaan |
| `nomor_telepon` | Nomor Telepon |
| `alamat_domisili` | Alamat Domisili |
| `alamat_ktp` | Alamat KTP |
| `blok` | Blok |
| `keluarga` | Keluarga |
| `ket_status` | Status dalam Keluarga |
| `status_rumah_tinggal` | Status Rumah Tinggal |

### Tab 2: Iman
Church membership and sacramental records:

| Field | Display label |
|---|---|
| `kewargaan` | Kewargaan |
| `tempat_kebaktian` | Tempat Kebaktian |
| `nama_gereja_lain` | Nama Gereja (jika lain) — only shown if filled |
| `sudah_baptis` + `baptis_oleh` + `tanggal_baptis` + `tempat_baptis` | Baptis |
| `sudah_sidi` + `sidi_oleh` + `tanggal_sidi` + `tempat_sidi` | Sidi |
| `nikah_oleh` + `tanggal_nikah` + `tempat_nikah` | Nikah — only shown if filled |

### Tab 3: Pelayanan
Ministry interests from census form:

| Field | Display label |
|---|---|
| `minat_pelayanan_gerejawi` | Minat Pelayanan Gerejawi |
| `minat_pelayanan_umum` | Minat Pelayanan Umum |
| `pelayanan_diikuti` | Pelayanan Diikuti (legacy) — only shown if filled |
| `ibadah_sering_diikuti` | Ibadah Sering Diikuti (legacy) — only shown if filled |

### Tab 4: Riwayat
Audit trail from `simple_history`. Shows all recorded changes to this member record.

Each row shows:
- Change type: `+` (ditambah), `~` (diubah), `-` (dihapus)
- For `~` (update): list of fields that changed with old value → new value

**No timestamp shown.**

---

## 2. Tab Switching — Vanilla JS

```html
<div class="tab-bar">
  <button class="tab-btn active" data-tab="pribadi">Data Pribadi</button>
  <button class="tab-btn" data-tab="iman">Iman</button>
  <button class="tab-btn" data-tab="pelayanan">Pelayanan</button>
  <button class="tab-btn" data-tab="riwayat">Riwayat</button>
</div>

<div id="tab-pribadi" class="tab-panel"><!-- content --></div>
<div id="tab-iman" class="tab-panel tab-panel--hidden"><!-- content --></div>
<div id="tab-pelayanan" class="tab-panel tab-panel--hidden"><!-- content --></div>
<div id="tab-riwayat" class="tab-panel tab-panel--hidden"><!-- content --></div>

<script>
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('tab-panel--hidden'));
      btn.classList.add('active');
      document.getElementById('tab-' + btn.dataset.tab).classList.remove('tab-panel--hidden');
    });
  });
</script>
```

---

## 3. CSS Additions (`static/css/style.css`)

```css
/* Tab bar */
.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.6rem 1.25rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--color-text-muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
}

.tab-btn:hover { color: var(--color-text); }

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.tab-panel--hidden { display: none; }
```

---

## 4. Dashboard Additions

### New section: Sebaran Kategori Usia
A table showing member count per age category (from `Member.status` field).

**View change** — add to `dashboard` context:
```python
by_status = Member.objects.values('status').annotate(total=Count('id')).order_by('status')
```

### New section: Ulang Tahun Pekan Ini
Members whose birthday (day + month) falls within the next 7 days. Same logic already used in the public home page `home()` view — extract to a shared helper and call from `dashboard()` too.

**View change** — add to `dashboard` context:
```python
from datetime import date, timedelta
today = date.today()
week_dates = [today + timedelta(days=i) for i in range(7)]
birthdays = []
for d in week_dates:
    for m in Member.objects.filter(
        tanggal_lahir__isnull=False,
        tanggal_lahir__month=d.month,
        tanggal_lahir__day=d.day,
    ).exclude(kewargaan='Meninggal'):
        birthdays.append({'member': m, 'date': d, 'is_today': d == today})
```

---

## 5. Files Changed Summary

| File | Change |
|---|---|
| `templates/members/member_detail.html` | Restructure into 4 tab panels + JS |
| `templates/members/dashboard.html` | Add Sebaran Usia table + Ulang Tahun Pekan Ini card |
| `members/views.py` | Add `by_status` and `birthdays` to dashboard context |
| `static/css/style.css` | Add tab CSS classes |

---

## 6. Testing Checklist

- [ ] Data Pribadi tab is active by default on page load
- [ ] Clicking each tab shows correct panel, hides others
- [ ] All new census fields appear in correct tab
- [ ] Riwayat shows history records with old→new values, no timestamp
- [ ] Dashboard shows Sebaran Usia table with correct counts
- [ ] Dashboard shows birthdays for next 7 days
- [ ] Tab state resets to Data Pribadi on page refresh (expected)
- [ ] No JS errors in browser console
