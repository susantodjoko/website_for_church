# GKJ Salatiga Church Website — Design Spec

**Date:** 2026-05-06
**Project directory:** `C:\Users\user\Documents\django_web`
**Stack:** Django 5 · SQLite · Custom CSS · Django Admin
**Reference sources:**
- `C:\Users\user\Documents\church_website\church-website-build-guide.md` — Elevation-inspired design
- `C:\Users\user\Documents\GKJ\gkj_app` — existing GKJ member management system

---

## 1. Overview

A Django web application for GKJ (Gereja Kristen Jawa) Salatiga combining two things:

1. **Public-facing church website** — Elevation Church-inspired modern layout adapted to GKJ's identity (deep blue `#1B4F8A` accent, English language). Sermons, events, ministries, service times, about, and plan-a-visit pages. All content managed through Django admin.

2. **Member management system** — Internal area (staff login required) for managing congregation data: members, families, church council, weekly service attendance, and simplified tithe/funeral fund records.

A `LEARNING_GUIDE.md` at the project root serves as a step-by-step practice reference combining both source documents.

---

## 2. Architecture

**Approach:** Two Django apps in one project. Clean separation between public content and internal member data.

```
django_web/
├── manage.py
├── requirements.txt
├── LEARNING_GUIDE.md
├── church_site/              ← Django project (settings, root URLs)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── website/                  ← App 1: Public-facing site
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/website/
├── members/                  ← App 2: Member management
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/members/
├── static/
│   ├── css/style.css
│   ├── js/
│   └── images/
└── media/                    ← Uploaded images & thumbnails
```

**Database:** SQLite (development default, upgrade path to PostgreSQL documented in LEARNING_GUIDE).
**Templates:** Django built-in template engine. All pages extend `base.html`.
**Styling:** Custom CSS using design token variables from the build guide, with GKJ blue replacing Elevation orange.
**Auth:** Django's built-in auth. Staff flag controls member area access.

---

## 3. Data Models

### `website` app

#### `HeroSlide`
| Field | Type | Notes |
|---|---|---|
| headline | CharField(200) | Bold hero text |
| subheadline | CharField(300) | Secondary text |
| cta_primary_text | CharField(100) | Primary button label |
| cta_primary_url | CharField(200) | Primary button URL |
| cta_secondary_text | CharField(100) | Secondary button label |
| cta_secondary_url | CharField(200) | Secondary button URL |
| background_image | ImageField | Fallback/hero image |
| is_active | BooleanField | Only one active at a time |

#### `SermonSeries`
| Field | Type | Notes |
|---|---|---|
| name | CharField(200) | Series name |
| description | TextField | Optional series description |
| thumbnail | ImageField | Series cover image |

#### `Sermon`
| Field | Type | Notes |
|---|---|---|
| title | CharField(200) | Message title |
| series | ForeignKey(SermonSeries) | nullable |
| pastor | CharField(100) | Speaker name |
| date | DateField | Sermon date |
| description | TextField | Short description |
| youtube_url | URLField | YouTube embed link |
| thumbnail | ImageField | Sermon thumbnail |
| is_featured | BooleanField | Shows on homepage |
| topic | CharField(50, choices) | faith/family/purpose/prayer — for filtering |

#### `Ministry`
| Field | Type | Notes |
|---|---|---|
| name | CharField(100) | Ministry name |
| description | TextField | Short description |
| image | ImageField | Showcase image |
| order | PositiveIntegerField | Controls display order |

#### `ServiceTime`
| Field | Type | Notes |
|---|---|---|
| campus_name | CharField(100) | e.g. "Main Campus", "Online" |
| address | TextField | Street address or stream info |
| times | TextField | Free text e.g. "Sunday · 8:00 AM" |
| is_online | BooleanField | Toggles online campus styling |
| link_label | CharField(100) | e.g. "Plan your visit" |
| link_url | CharField(200) | e.g. /visit/ |

#### `Event`
| Field | Type | Notes |
|---|---|---|
| title | CharField(200) | Event name |
| date | DateField | Event date |
| time | TimeField | Start time |
| location | CharField(200) | Venue name |
| description | TextField | Event details |
| image | ImageField | Event banner |
| registration_url | URLField | External reg link, optional |
| is_published | BooleanField | Controls visibility |

#### `AboutPage` (singleton)
| Field | Type | Notes |
|---|---|---|
| mission_statement | TextField | Hero text on about page |
| pastor_name | CharField(100) | Lead pastor name |
| pastor_bio | TextField | Bio paragraph |
| pastor_photo | ImageField | Pastor headshot |
| value_1_title … value_4_title | CharField(100) | Four core values |
| value_1_body … value_4_body | TextField | Value descriptions |

---

### `members` app

#### `Keluarga`
| Field | Type | Notes |
|---|---|---|
| no_kk_gereja | CharField(20, unique) | Church family card number |
| nama_keluarga | CharField(200) | Family name |
| blok | CharField(10, choices) | 23 blok choices (CK1–KY5) |
| alamat | TextField | Home address |

#### `Member`
Full field set from the GKJ reference app:
`no_sensus`, `nama_lengkap`, `jenis_kelamin`, `tempat_lahir`, `tanggal_lahir`, `nomor_telepon`, `status` (Dewasa/Anak), `kewargaan` (Warga/Simpatisan/Titipan/Luar Kota/Meninggal), `gol_darah`, `pendidikan`, `pekerjaan`, `ket_status` (KK/Istri/Anak/Lainnya), `sudah_baptis`, `sudah_sidi`, `tanggal_wafat`, `pelayanan_diikuti`, `ibadah_sering_diikuti`, `keluarga` (FK→Keluarga, SET_NULL). Audit trail via `simple_history`.

#### `Majelis`
`member` (FK), `jabatan` (choices), `periode_mulai`, `periode_selesai`, `aktif`

#### `IbadahMingguan`
`tanggal`, `minggu_ke` — with inline `IbadahService` records (nama_service, jumlah_hadir, jumlah_persembahan)

#### `Perpuluhan` (simplified)
`member` (FK), `tanggal`, `jumlah`, `metode_pembayaran`, `keterangan` — admin only, no custom views

#### `IuranPralenan` (simplified)
`member` (FK), `tanggal`, `jumlah`, `metode_pembayaran`, `keterangan` — admin only, no custom views

#### `MemberStatusHistory`
`member` (FK), `status_lama`, `status_baru`, `keterangan`, `tanggal`, `dicatat_oleh` (FK→User)

---

## 4. URL Structure

### Public (`website` app)
| URL | View | Template |
|---|---|---|
| `/` | `home` | `website/home.html` |
| `/sermons/` | `sermon_list` | `website/sermons.html` |
| `/sermons/<int:pk>/` | `sermon_detail` | `website/sermon_detail.html` |
| `/events/` | `event_list` | `website/events.html` |
| `/about/` | `about` | `website/about.html` |
| `/visit/` | `visit` | `website/visit.html` |

### Members area (`members` app — `@login_required`)
| URL | View | Template |
|---|---|---|
| `/members/` | `member_list` | `members/member_list.html` |
| `/members/<int:pk>/` | `member_detail` | `members/member_detail.html` |
| `/members/families/` | `family_list` | `members/family_list.html` |

---

## 5. Django Admin Configuration

### `website` admin
- **`HeroSlide`** — `list_display`: headline, is_active. Override `has_add_permission` to allow only 1 active slide at a time.
- **`Sermon`** — `list_display`: title, series, pastor, date, is_featured. `list_filter`: series, topic. `search_fields`: title, pastor.
- **`Event`** — `list_display`: title, date, time, is_published. `list_filter`: is_published, date.
- **`Ministry`** — `list_display`: name, order. Ordered by `order`. Inline edit of order field.
- **`AboutPage`** — `has_add_permission` returns False if a row already exists (singleton).

### `members` admin
- **`Member`** — `list_display`: nama_lengkap, kewargaan, jenis_kelamin, tanggal_lahir. `search_fields`: nama_lengkap, no_sensus. `list_filter`: kewargaan, jenis_kelamin, sudah_baptis, sudah_sidi.
- **`Keluarga`** — `list_display`: nama_keluarga, blok, no_kk_gereja. `list_filter`: blok. `search_fields`: nama_keluarga.
- **`Perpuluhan`** / **`IuranPralenan`** — `list_display`: member, tanggal, jumlah. `search_fields`: member__nama_lengkap.
- **`IbadahMingguan`** — `IbadahService` as inline. `list_display`: tanggal, minggu_ke.

---

## 6. Design System

Adapted from the Elevation Church build guide, rebranded for GKJ:

```css
:root {
  --color-primary:      #1B4F8A;   /* GKJ deep blue */
  --color-primary-dark: #153D6B;   /* Hover state */
  --color-dark:         #1A1A1A;
  --color-dark-2:       #2C2C2C;
  --color-light:        #F7F7F5;
  --color-white:        #FFFFFF;
  --color-text:         #1A1A1A;
  --color-text-muted:   #6B6B6B;
  --color-border:       #E5E5E3;
  --font-sans: 'Inter', -apple-system, sans-serif;
  /* Spacing, radius, transitions — same as build guide */
}
```

**Navbar:** Fixed, transparent on hero, dark on scroll. Logo: "GKJ Salatiga". Links: Sermons · Events · About · Visit. Staff login link in actions.
**Hero:** Full-screen image (no video for simplicity). Bold headline from `HeroSlide`. Two CTA buttons.
**Footer:** Dark background, church address, social links, copyright.

---

## 7. Learning Guide (`LEARNING_GUIDE.md`)

A practice reference at the project root combining both source documents. Structure:

1. Setup — Python virtual environment, Django install, project scaffold
2. Apps — creating `website` and `members` with `startapp`
3. Models — field types explained, ForeignKey, choices, ImageField
4. Migrations — `makemigrations`, `migrate`, understanding migration files
5. Admin — registering models, `list_display`, `search_fields`, `list_filter`, singleton pattern
6. Views — function-based views, context dictionaries, `@login_required`
7. URL routing — project `urls.py` vs app `urls.py`, `include()`
8. Templates — `base.html` inheritance, `{% block %}`, `{% url %}`, `{{ var }}`
9. Static files — `{% load static %}`, CSS design tokens, JS
10. Media files — `ImageField`, `MEDIA_ROOT`, serving in development
11. Public pages — building each page section by section (matching build guide)
12. Member list view — pagination with `Paginator`, search with `Q` objects
13. Admin customization — `has_add_permission`, inline models, custom `list_display`
14. Next steps — PostgreSQL, Gunicorn, Nginx, deployment to a VPS

---

## 8. Out of Scope (for now)


- Excel export (Perpuluhan, IuranPralenan)
- Bulk payment entry
- Statistics dashboard / charts
- Birthday list view
- Role-based access beyond staff/non-staff
- Contact / visit registration form
- Deployment configuration
