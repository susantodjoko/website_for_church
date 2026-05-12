# GKJ Salatiga Church Website — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Django 5 web application for GKJ Salatiga combining a public-facing church website with an internal member management system, managed entirely through Django Admin.

**Architecture:** Two Django apps (`website` for public content, `members` for internal data) share one project (`church_site`). Public pages are open to all; the members area is gated behind `@login_required`. All content (sermons, events, hero slides, about page) is entered via Django Admin.

**Tech Stack:** Python 3.12+, Django 5.x, SQLite (default), Pillow (ImageField support), django-simple-history (member audit trail), Custom CSS (no external CSS framework), Inter font (Google Fonts)

---

## File Map

Files you will create, organized by task:

```
django_web/
├── manage.py                          ← Task 2 (auto-generated)
├── requirements.txt                   ← Task 1
├── LEARNING_GUIDE.md                  ← Task 12
├── church_site/
│   ├── settings.py                   ← Task 2 (modify)
│   ├── urls.py                       ← Task 7 (modify)
│   └── wsgi.py                       ← Task 2 (auto-generated)
├── website/
│   ├── models.py                     ← Task 3
│   ├── admin.py                      ← Task 4
│   ├── views.py                      ← Task 7
│   ├── urls.py                       ← Task 7
│   ├── tests.py                      ← Tasks 3, 7
│   └── templates/website/
│       ├── home.html                 ← Task 8
│       ├── sermons.html              ← Task 9
│       ├── sermon_detail.html        ← Task 9
│       ├── events.html               ← Task 10
│       ├── about.html                ← Task 10
│       └── visit.html                ← Task 10
├── members/
│   ├── models.py                     ← Task 11
│   ├── admin.py                      ← Task 11
│   ├── views.py                      ← Task 13
│   ├── urls.py                       ← Task 13
│   ├── tests.py                      ← Tasks 11, 13
│   └── templates/members/
│       ├── member_list.html          ← Task 14
│       ├── member_detail.html        ← Task 14
│       └── family_list.html          ← Task 14
├── templates/
│   └── base.html                     ← Task 6
├── static/
│   ├── css/style.css                 ← Task 5
│   └── js/main.js                   ← Task 5
└── media/                            ← Task 2 (create empty dir)
```

---

## Task 1: Set Up Python Virtual Environment & Dependencies

**Why:** A virtual environment keeps your project's packages isolated from your system Python. This means different projects can use different Django versions without conflicts.

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Open a terminal in the project directory**

On Windows, open PowerShell and navigate to your project:

```powershell
cd C:\Users\user\Documents\django_web
```

- [ ] **Step 2: Create a virtual environment**

```powershell
python -m venv venv
```

**What this does:** Creates a `venv/` folder containing a private copy of Python and pip. All packages you install will go here, not into your system Python.

- [ ] **Step 3: Activate the virtual environment**

```powershell
venv\Scripts\activate
```

Your terminal prompt should now start with `(venv)`. You must activate this every time you open a new terminal to work on this project.

- [ ] **Step 4: Install Django and dependencies**

```powershell
pip install Django Pillow django-simple-history
```

**What each package does:**
- `Django` — the web framework
- `Pillow` — required for `ImageField` (uploading photos/images)
- `django-simple-history` — automatically records every change to a model (audit trail for members)

- [ ] **Step 5: Save exact versions to requirements.txt**

```powershell
pip freeze > requirements.txt
```

**Why:** `requirements.txt` lets anyone reproduce your exact environment with `pip install -r requirements.txt`.

- [ ] **Step 6: Verify installation**

```powershell
python -m django --version
```

Expected output: `5.x.x` (any 5.x version is fine)

---

## Task 2: Create Django Project & Initial Configuration

**Why:** `django-admin startproject` generates the project skeleton — settings, URL routing, WSGI server config. We then configure it for our needs (media files, static files, template directories).

**Files:**
- Modify: `church_site/settings.py`
- Create: `media/` (empty directory)

- [ ] **Step 1: Create the Django project**

```powershell
django-admin startproject church_site .
```

**The `.` at the end is important** — it tells Django to create the project files in the current directory (not inside a subdirectory). After this you should see `manage.py` and a `church_site/` folder.

- [ ] **Step 2: Create the media directory**

```powershell
mkdir media
mkdir static\css
mkdir static\js
mkdir static\images
mkdir templates
```

- [ ] **Step 3: Open `church_site/settings.py` and make these changes**

Find `INSTALLED_APPS` and replace it:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simple_history',   # audit trail package
    'website',          # public church site (we'll create this next)
    'members',          # member management (we'll create this later)
]
```

Find `MIDDLEWARE` and add one line after `'django.contrib.sessions.middleware.SessionMiddleware'`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',  # ← add this
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Find `TEMPLATES` and update the `DIRS` key:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # ← add this so Django finds base.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

At the bottom of `settings.py`, add these lines after `STATIC_URL`:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/members/'
```

**What these do:**
- `STATICFILES_DIRS` — tells Django where your CSS/JS files live during development
- `MEDIA_URL` / `MEDIA_ROOT` — where uploaded images (hero, sermon thumbnails, etc.) are stored
- `LOGIN_URL` — when a page requires login, redirect here (we reuse Django Admin's login)
- `LOGIN_REDIRECT_URL` — after login, go to the members list

- [ ] **Step 4: Run initial database migration**

```powershell
python manage.py migrate
```

**What this does:** Django ships with built-in models (users, sessions, admin). This command creates the SQLite database file (`db.sqlite3`) and builds those tables.

Expected output: Several `OK` lines ending with `Running migrations`.

- [ ] **Step 5: Create a superuser (admin account)**

```powershell
python manage.py createsuperuser
```

Enter a username, email, and password when prompted. You'll use this to log into Django Admin.

- [ ] **Step 6: Test the development server**

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` in your browser. You should see the Django admin login page. Log in with the superuser you just created.

Press `Ctrl+C` to stop the server.

- [ ] **Step 7: Commit**

```powershell
git init
git add manage.py requirements.txt church_site/
git commit -m "feat: initialize Django project with church_site settings"
```

---

## Task 3: Create `website` App & Models

**Why:** In Django, an "app" is a self-contained module. All public-facing church content lives in the `website` app. Models are Python classes that map to database tables.

**Files:**
- Create: `website/models.py` (full replace)
- Create: `website/tests.py` (full replace)

- [ ] **Step 1: Create the website app**

```powershell
python manage.py startapp website
```

This creates the `website/` folder with `models.py`, `views.py`, `admin.py`, and `tests.py`.

- [ ] **Step 2: Write the failing model tests**

Open `website/tests.py` and replace its contents:

```python
from django.test import TestCase
from datetime import date
from .models import HeroSlide, Sermon, SermonSeries, Ministry, ServiceTime, Event, AboutPage


class HeroSlideModelTest(TestCase):
    def test_str_returns_headline(self):
        slide = HeroSlide(headline='Welcome to GKJ')
        self.assertEqual(str(slide), 'Welcome to GKJ')


class SermonModelTest(TestCase):
    def test_str_returns_title(self):
        sermon = Sermon(title='Walking by Faith')
        self.assertEqual(str(sermon), 'Walking by Faith')

    def test_ordered_newest_first(self):
        s1 = Sermon.objects.create(
            title='Old', pastor='P', date=date(2024, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        s2 = Sermon.objects.create(
            title='New', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz'
        )
        sermons = list(Sermon.objects.all())
        self.assertEqual(sermons[0], s2)
        self.assertEqual(sermons[1], s1)


class MinistryModelTest(TestCase):
    def test_ordered_by_order_field(self):
        m1 = Ministry.objects.create(name='Youth', description='', order=2)
        m2 = Ministry.objects.create(name='Worship', description='', order=1)
        ministries = list(Ministry.objects.all())
        self.assertEqual(ministries[0], m2)
        self.assertEqual(ministries[1], m1)


class AboutPageModelTest(TestCase):
    def test_str(self):
        about = AboutPage(mission_statement='Loving God')
        self.assertEqual(str(about), 'About Page')
```

- [ ] **Step 3: Run tests to confirm they fail (models not defined yet)**

```powershell
python manage.py test website
```

Expected: `ImportError` or `ModuleNotFoundError` — the models don't exist yet.

- [ ] **Step 4: Write `website/models.py`**

Replace the contents of `website/models.py`:

```python
from django.db import models


class HeroSlide(models.Model):
    headline = models.CharField(max_length=200)
    subheadline = models.CharField(max_length=300)
    cta_primary_text = models.CharField(max_length=100)
    cta_primary_url = models.CharField(max_length=200)
    cta_secondary_text = models.CharField(max_length=100, blank=True)
    cta_secondary_url = models.CharField(max_length=200, blank=True)
    background_image = models.ImageField(upload_to='hero/', blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.headline


class SermonSeries(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='series/', blank=True)

    class Meta:
        verbose_name_plural = 'Sermon Series'

    def __str__(self):
        return self.name


class Sermon(models.Model):
    TOPIC_CHOICES = [
        ('faith', 'Faith'),
        ('family', 'Family'),
        ('purpose', 'Purpose'),
        ('prayer', 'Prayer'),
    ]

    title = models.CharField(max_length=200)
    series = models.ForeignKey(
        SermonSeries, null=True, blank=True, on_delete=models.SET_NULL
    )
    pastor = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    youtube_url = models.URLField()
    thumbnail = models.ImageField(upload_to='sermons/', blank=True)
    is_featured = models.BooleanField(default=False)
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Ministry(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='ministry/', blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Ministries'

    def __str__(self):
        return self.name


class ServiceTime(models.Model):
    campus_name = models.CharField(max_length=100)
    address = models.TextField()
    times = models.TextField()
    is_online = models.BooleanField(default=False)
    link_label = models.CharField(max_length=100)
    link_url = models.CharField(max_length=200)

    def __str__(self):
        return self.campus_name


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True)
    registration_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title


class AboutPage(models.Model):
    mission_statement = models.TextField()
    pastor_name = models.CharField(max_length=100)
    pastor_bio = models.TextField()
    pastor_photo = models.ImageField(upload_to='about/', blank=True)
    value_1_title = models.CharField(max_length=100)
    value_1_body = models.TextField()
    value_2_title = models.CharField(max_length=100)
    value_2_body = models.TextField()
    value_3_title = models.CharField(max_length=100)
    value_3_body = models.TextField()
    value_4_title = models.CharField(max_length=100)
    value_4_body = models.TextField()

    def __str__(self):
        return 'About Page'
```

**Key concepts used:**
- `CharField` — short text (max_length is required)
- `TextField` — long text (no max_length needed)
- `ImageField` — stores the file path; `upload_to` sets the subfolder inside `media/`
- `BooleanField` — True/False checkbox
- `ForeignKey` — links one model to another; `on_delete=SET_NULL` means "don't delete the sermon if the series is deleted"
- `class Meta` — controls ordering, plural names, etc.

- [ ] **Step 5: Create and apply migrations**

```powershell
python manage.py makemigrations website
python manage.py migrate
```

**What this does:** `makemigrations` reads your models and creates a migration file (a Python script describing the database schema changes). `migrate` executes those scripts against the database.

- [ ] **Step 6: Run tests — they should now pass**

```powershell
python manage.py test website
```

Expected: `OK` with 4 tests passing.

- [ ] **Step 7: Commit**

```powershell
git add website/
git commit -m "feat: add website app models (Sermon, Event, Ministry, HeroSlide, etc.)"
```

---

## Task 4: Configure `website` Admin

**Why:** Django Admin gives you a free, fully-featured content management interface. By registering your models and customizing `list_display`, `search_fields`, and `list_filter`, you control what editors see.

**Files:**
- Modify: `website/admin.py` (full replace)

- [ ] **Step 1: Write `website/admin.py`**

Replace the contents of `website/admin.py`:

```python
from django.contrib import admin
from .models import HeroSlide, SermonSeries, Sermon, Ministry, ServiceTime, Event, AboutPage


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['headline', 'is_active']


@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ['title', 'series', 'pastor', 'date', 'is_featured']
    list_filter = ['series', 'topic']
    search_fields = ['title', 'pastor']


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = ['campus_name', 'is_online']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'is_published']
    list_filter = ['is_published', 'date']


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one AboutPage to exist at a time (singleton pattern)
        return not AboutPage.objects.exists()
```

**Key concepts:**
- `@admin.register(Model)` — the decorator registers a model with a custom admin class in one step
- `list_display` — columns shown in the list view
- `list_filter` — sidebar filters
- `search_fields` — which fields the search box queries
- `has_add_permission` — overriding this to return `False` when one row exists prevents duplicates (singleton pattern for AboutPage)

- [ ] **Step 2: Verify admin works**

```powershell
python manage.py runserver
```

Go to `http://127.0.0.1:8000/admin/`. You should see all seven models listed under "Website". Try adding a Sermon — you should see the fields defined in your model.

Stop the server with `Ctrl+C`.

- [ ] **Step 3: Commit**

```powershell
git add website/admin.py
git commit -m "feat: register website models in Django admin with custom display"
```

---

## Task 5: Static Files — CSS Design System & JavaScript

**Why:** All visual styling goes in one CSS file. We use CSS custom properties (variables) as "design tokens" — defining colors, spacing, and fonts once in `:root` and referencing them everywhere. This makes global changes (e.g., changing the primary color) a one-line edit.

**Files:**
- Create: `static/css/style.css`
- Create: `static/js/main.js`

- [ ] **Step 1: Create `static/css/style.css`**

```css
/* ===========================
   DESIGN TOKENS
   =========================== */
:root {
  --color-primary:      #1B4F8A;
  --color-primary-dark: #153D6B;
  --color-dark:         #1A1A1A;
  --color-dark-2:       #2C2C2C;
  --color-light:        #F7F7F5;
  --color-white:        #FFFFFF;
  --color-text:         #1A1A1A;
  --color-text-muted:   #6B6B6B;
  --color-border:       #E5E5E3;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  --space-xs:  0.5rem;
  --space-sm:  1rem;
  --space-md:  1.5rem;
  --space-lg:  2.5rem;
  --space-xl:  4rem;
  --space-2xl: 6rem;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;

  --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.12);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.16);

  --transition: 0.25s ease;
  --nav-height: 70px;
}

/* ===========================
   RESET & BASE
   =========================== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  font-family: var(--font-sans);
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text);
  background: var(--color-white);
}

img { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
ul { list-style: none; }

/* ===========================
   LAYOUT
   =========================== */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-md);
}

.section { padding: var(--space-2xl) 0; }
.section--dark { background: var(--color-dark); color: var(--color-white); }
.section--light { background: var(--color-light); }

.section__title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--space-lg);
  text-align: center;
}

.section__cta {
  text-align: center;
  margin-top: var(--space-lg);
}

/* ===========================
   BUTTONS
   =========================== */
.btn {
  display: inline-block;
  padding: 0.75rem 1.75rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition), color var(--transition), border-color var(--transition);
  border: 2px solid transparent;
}

.btn--primary { background: var(--color-primary); color: var(--color-white); }
.btn--primary:hover { background: var(--color-primary-dark); }

.btn--secondary {
  background: transparent;
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.btn--secondary:hover { background: var(--color-primary); color: var(--color-white); }

.btn--outline { background: transparent; border-color: var(--color-primary); color: var(--color-primary); }
.btn--outline:hover { background: var(--color-primary); color: var(--color-white); }

.btn--outline-light { background: transparent; border-color: var(--color-white); color: var(--color-white); }
.btn--outline-light:hover { background: var(--color-white); color: var(--color-dark); }

/* ===========================
   NAVBAR
   =========================== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  z-index: 1000;
  transition: background var(--transition), box-shadow var(--transition);
}

.navbar.scrolled {
  background: var(--color-dark);
  box-shadow: var(--shadow-md);
}

.navbar__inner {
  display: flex;
  align-items: center;
  height: 100%;
  gap: var(--space-md);
}

.navbar__logo {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-white);
  flex-shrink: 0;
}

.navbar__links {
  display: flex;
  gap: var(--space-md);
  margin-left: auto;
}

.navbar__links a {
  color: rgba(255,255,255,0.85);
  font-weight: 500;
  font-size: 0.95rem;
  transition: color var(--transition);
}
.navbar__links a:hover { color: var(--color-white); }

.navbar__actions { margin-left: var(--space-sm); }

.navbar__toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  flex-direction: column;
  gap: 5px;
  padding: 4px;
  margin-left: auto;
}

.navbar__toggle span {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--color-white);
}

/* ===========================
   HERO
   =========================== */
.hero {
  position: relative;
  height: 100vh;
  min-height: 600px;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero__bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
}

.hero__bg--default {
  background: linear-gradient(135deg, var(--color-primary), var(--color-dark));
}

.hero__overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
}

.hero__content {
  position: relative;
  z-index: 1;
  color: var(--color-white);
  max-width: 700px;
}

.hero__headline {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: var(--space-md);
}

.hero__sub {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: var(--space-lg);
  max-width: 500px;
}

.hero__ctas {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

/* ===========================
   CARDS
   =========================== */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-md);
}

.card {
  background: var(--color-white);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition), box-shadow var(--transition);
  display: flex;
  flex-direction: column;
}

.card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.card--ministry { background: var(--color-dark-2); color: var(--color-white); }

.card__img { width: 100%; height: 200px; object-fit: cover; }

.card__body {
  padding: var(--space-md);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card__tag {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary);
  margin-bottom: var(--space-xs);
}
.card--ministry .card__tag { color: rgba(255,255,255,0.6); }

.card__title { font-size: 1.15rem; font-weight: 700; margin-bottom: var(--space-xs); line-height: 1.3; }

.card__meta { font-size: 0.85rem; color: var(--color-text-muted); margin-bottom: var(--space-xs); }
.card--ministry .card__meta { color: rgba(255,255,255,0.6); }

.card__text { font-size: 0.95rem; color: var(--color-text-muted); margin-bottom: var(--space-sm); flex: 1; }
.card--ministry .card__text { color: rgba(255,255,255,0.75); }

/* ===========================
   SERVICE TIMES
   =========================== */
.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-md);
}

.service-card {
  background: var(--color-light);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  text-align: center;
  border-top: 4px solid var(--color-primary);
}

.service-card--online { border-top-color: #27ae60; }

.service-card__name { font-size: 1.3rem; font-weight: 700; margin-bottom: var(--space-xs); }
.service-card__times { font-size: 1rem; font-weight: 600; color: var(--color-primary); margin-bottom: var(--space-xs); }
.service-card__address { font-size: 0.9rem; color: var(--color-text-muted); margin-bottom: var(--space-md); }

/* ===========================
   PAGE HEADER (inner pages)
   =========================== */
.page-header {
  padding: calc(var(--nav-height) + var(--space-xl)) 0 var(--space-xl);
  background: var(--color-dark);
  color: var(--color-white);
  text-align: center;
}

.page-header__title { font-size: 2.5rem; font-weight: 800; }
.page-header__sub { font-size: 1.1rem; opacity: 0.75; margin-top: var(--space-xs); }

/* ===========================
   SERMON DETAIL
   =========================== */
.sermon-detail {
  padding: calc(var(--nav-height) + var(--space-xl)) 0 var(--space-2xl);
}

.video-embed {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
}

.video-embed iframe {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  border: 0;
}

.sermon-detail__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* ===========================
   ABOUT PAGE
   =========================== */
.about-pastor {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-xl);
  align-items: start;
  margin-bottom: var(--space-2xl);
}

.about-pastor__photo {
  border-radius: var(--radius-lg);
  width: 100%;
  object-fit: cover;
  aspect-ratio: 3/4;
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.value-card {
  background: var(--color-light);
  padding: var(--space-lg);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-primary);
}

.value-card__title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
  color: var(--color-primary);
}

/* ===========================
   FILTER BAR (sermons page)
   =========================== */
.filter-bar {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
  margin-bottom: var(--space-lg);
}

.filter-btn {
  padding: 0.4rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  font-size: 0.85rem;
  cursor: pointer;
  background: var(--color-white);
  color: var(--color-text);
  transition: var(--transition);
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
}

/* ===========================
   FOOTER
   =========================== */
.footer {
  background: var(--color-dark);
  color: var(--color-white);
  padding: var(--space-2xl) 0 var(--space-lg);
}

.footer__inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
  align-items: start;
  margin-bottom: var(--space-lg);
}

.footer__name { font-size: 1.4rem; font-weight: 800; margin-bottom: var(--space-xs); }
.footer__tagline { color: rgba(255,255,255,0.6); font-size: 0.9rem; }

.footer__links { display: flex; flex-direction: column; gap: var(--space-xs); }
.footer__links a { color: rgba(255,255,255,0.75); font-size: 0.95rem; transition: color var(--transition); }
.footer__links a:hover { color: var(--color-white); }

.footer__copy {
  grid-column: 1 / -1;
  text-align: center;
  color: rgba(255,255,255,0.4);
  font-size: 0.85rem;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: var(--space-md);
}

/* ===========================
   MEMBERS AREA
   =========================== */
.members-layout {
  padding: calc(var(--nav-height) + var(--space-lg)) 0 var(--space-2xl);
}

.members-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.members-header h1 { font-size: 1.75rem; font-weight: 700; }

.search-form { display: flex; gap: var(--space-xs); }

.search-form input {
  padding: 0.6rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  min-width: 240px;
  font-family: var(--font-sans);
}

.search-form input:focus { outline: none; border-color: var(--color-primary); }

.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background: var(--color-light);
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.data-table tr:hover td { background: var(--color-light); }
.data-table a { color: var(--color-primary); font-weight: 500; }

.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge--warga    { background: #dbeafe; color: #1e40af; }
.badge--simpatisan { background: #fef9c3; color: #854d0e; }
.badge--meninggal { background: #f3f4f6; color: #6b7280; }
.badge--titipan  { background: #fce7f3; color: #9d174d; }
.badge--luar.kota { background: #dcfce7; color: #166534; }

.pagination {
  display: flex;
  justify-content: center;
  gap: var(--space-xs);
  margin-top: var(--space-lg);
  flex-wrap: wrap;
}

.pagination a,
.pagination span {
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  font-size: 0.9rem;
}

.pagination a:hover { background: var(--color-primary); color: var(--color-white); border-color: var(--color-primary); }
.pagination .current { background: var(--color-primary); color: var(--color-white); border-color: var(--color-primary); }

/* ===========================
   MEMBER DETAIL
   =========================== */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-xs) var(--space-lg);
  margin-bottom: var(--space-lg);
}

.detail-item__label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin-bottom: 2px;
}

.detail-item__value { font-size: 0.95rem; font-weight: 500; }

.detail-section {
  background: var(--color-light);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  margin-bottom: var(--space-md);
}

.detail-section h3 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: var(--space-md);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ===========================
   RESPONSIVE
   =========================== */
@media (max-width: 768px) {
  .navbar__links { display: none; }

  .navbar__links.open {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: var(--nav-height);
    left: 0; right: 0;
    background: var(--color-dark);
    padding: var(--space-md);
    gap: var(--space-sm);
  }

  .navbar__actions { display: none; }
  .navbar__toggle { display: flex; }

  .hero__headline { font-size: 2.2rem; }
  .about-pastor { grid-template-columns: 1fr; }
  .values-grid { grid-template-columns: 1fr; }
  .footer__inner { grid-template-columns: 1fr; }
  .detail-grid { grid-template-columns: 1fr; }
  .card-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 2: Create `static/js/main.js`**

```javascript
// Navbar: transparent on hero, dark background after scrolling 50px
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// Mobile hamburger menu toggle
const toggle = document.getElementById('navToggle');
const links = document.getElementById('navLinks');
if (toggle) {
  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
  });
}
```

- [ ] **Step 3: Commit**

```powershell
git add static/
git commit -m "feat: add CSS design system and navbar JS"
```

---

## Task 6: Create `base.html` — Shared Page Template

**Why:** Every page on the site shares the same navbar and footer. Instead of duplicating that HTML, we write it once in `base.html`. Individual page templates "extend" base.html and fill in the `{% block content %}` area. This is Django's template inheritance.

**Files:**
- Create: `templates/base.html`

- [ ] **Step 1: Create `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}GKJ Salatiga{% endblock %}</title>
  {% load static %}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>

  <nav class="navbar" id="navbar">
    <div class="container navbar__inner">
      <a href="{% url 'website:home' %}" class="navbar__logo">GKJ Salatiga</a>

      <button class="navbar__toggle" id="navToggle" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>

      <ul class="navbar__links" id="navLinks">
        <li><a href="{% url 'website:sermon_list' %}">Sermons</a></li>
        <li><a href="{% url 'website:event_list' %}">Events</a></li>
        <li><a href="{% url 'website:about' %}">About</a></li>
        <li><a href="{% url 'website:visit' %}">Visit</a></li>
      </ul>

      <div class="navbar__actions">
        {% if user.is_staff %}
          <a href="{% url 'members:member_list' %}" class="btn btn--outline">Members</a>
        {% else %}
          <a href="/admin/login/?next=/members/" class="btn btn--outline">Staff Login</a>
        {% endif %}
      </div>
    </div>
  </nav>

  <main>
    {% block content %}{% endblock %}
  </main>

  <footer class="footer">
    <div class="container">
      <div class="footer__inner">
        <div class="footer__brand">
          <p class="footer__name">GKJ Salatiga</p>
          <p class="footer__tagline">Gereja Kristen Jawa Salatiga</p>
        </div>
        <div class="footer__links">
          <a href="{% url 'website:home' %}">Home</a>
          <a href="{% url 'website:sermon_list' %}">Sermons</a>
          <a href="{% url 'website:event_list' %}">Events</a>
          <a href="{% url 'website:about' %}">About</a>
          <a href="{% url 'website:visit' %}">Visit</a>
        </div>
      </div>
      <p class="footer__copy">&copy; 2026 GKJ Salatiga. All rights reserved.</p>
    </div>
  </footer>

  <script src="{% static 'js/main.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

**Key template tags:**
- `{% load static %}` — loads the `static` tag library so `{% static 'css/style.css' %}` works
- `{% url 'website:home' %}` — generates the URL for the `home` view in the `website` app namespace
- `{% block title %}` — a slot that child templates can override
- `{% block content %}` — a slot for the page's main content
- `{% if user.is_staff %}` — Django's auth system puts the logged-in user in the template context automatically

- [ ] **Step 2: Commit**

```powershell
git add templates/
git commit -m "feat: add base.html with navbar and footer"
```

---

## Task 7: Website Views & URL Routing

**Why:** Views are Python functions that receive an HTTP request and return an HTML response. URL patterns map URL paths (like `/sermons/`) to view functions. Django has two levels: the project-level `urls.py` routes to apps, and each app has its own `urls.py`.

**Files:**
- Modify: `website/views.py` (full replace)
- Create: `website/urls.py`
- Modify: `church_site/urls.py` (full replace)
- Modify: `website/tests.py` (add view tests)

- [ ] **Step 1: Write view tests first**

Add to `website/tests.py` (append after the existing tests):

```python
from django.urls import reverse


class HomeViewTest(TestCase):
    def test_returns_200(self):
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)

    def test_uses_home_template(self):
        response = self.client.get(reverse('website:home'))
        self.assertTemplateUsed(response, 'website/home.html')


class SermonListViewTest(TestCase):
    def test_returns_200(self):
        response = self.client.get(reverse('website:sermon_list'))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_topic(self):
        from datetime import date
        Sermon.objects.create(
            title='Faith Talk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc', topic='faith'
        )
        Sermon.objects.create(
            title='Family Life', pastor='P', date=date(2025, 2, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz', topic='family'
        )
        response = self.client.get(reverse('website:sermon_list') + '?topic=faith')
        self.assertEqual(len(response.context['sermons']), 1)
        self.assertEqual(response.context['sermons'][0].title, 'Faith Talk')
```

- [ ] **Step 2: Run tests — they fail because URLs and views don't exist yet**

```powershell
python manage.py test website
```

Expected: errors about missing URL configuration.

- [ ] **Step 3: Write `website/views.py`**

```python
from django.shortcuts import render, get_object_or_404
from .models import HeroSlide, Sermon, Ministry, ServiceTime, Event, AboutPage


def home(request):
    hero = HeroSlide.objects.filter(is_active=True).first()
    featured_sermons = Sermon.objects.filter(is_featured=True)[:3]
    ministries = Ministry.objects.all()[:6]
    service_times = ServiceTime.objects.all()
    upcoming_events = Event.objects.filter(is_published=True)[:3]
    return render(request, 'website/home.html', {
        'hero': hero,
        'featured_sermons': featured_sermons,
        'ministries': ministries,
        'service_times': service_times,
        'upcoming_events': upcoming_events,
    })


def sermon_list(request):
    topic = request.GET.get('topic', '')
    sermons = Sermon.objects.all()
    if topic:
        sermons = sermons.filter(topic=topic)
    return render(request, 'website/sermons.html', {'sermons': sermons, 'topic': topic})


def sermon_detail(request, pk):
    sermon = get_object_or_404(Sermon, pk=pk)
    video_id = _extract_youtube_id(sermon.youtube_url)
    return render(request, 'website/sermon_detail.html', {
        'sermon': sermon,
        'video_id': video_id,
    })


def event_list(request):
    events = Event.objects.filter(is_published=True)
    return render(request, 'website/events.html', {'events': events})


def about(request):
    about_page = AboutPage.objects.first()
    return render(request, 'website/about.html', {'about': about_page})


def visit(request):
    service_times = ServiceTime.objects.all()
    return render(request, 'website/visit.html', {'service_times': service_times})


def _extract_youtube_id(url):
    """Extract the 11-character video ID from a YouTube URL."""
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return ''
```

- [ ] **Step 4: Create `website/urls.py`**

```python
from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('sermons/', views.sermon_list, name='sermon_list'),
    path('sermons/<int:pk>/', views.sermon_detail, name='sermon_detail'),
    path('events/', views.event_list, name='event_list'),
    path('about/', views.about, name='about'),
    path('visit/', views.visit, name='visit'),
]
```

**What `app_name = 'website'` does:** This sets a URL namespace. In templates, `{% url 'website:home' %}` references the `home` URL in the `website` namespace. Without namespacing, two apps could have conflicting URL names.

- [ ] **Step 5: Update `church_site/urls.py`**

Replace the full file:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('members/', include('members.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Why the `if settings.DEBUG` block?** In development, Django needs to serve uploaded media files itself. In production, your web server (Nginx) handles this.

- [ ] **Step 6: Run tests — they fail because templates don't exist yet**

```powershell
python manage.py test website
```

Expected: `TemplateDoesNotExist` errors.

- [ ] **Step 7: Commit what we have**

```powershell
git add website/views.py website/urls.py website/tests.py church_site/urls.py
git commit -m "feat: add website views and URL routing"
```

---

## Task 8: Home Page Template

**Why:** The home page is the most complex template — it has the full-screen hero, sermon cards, ministry grid, service times, and events. We build it once and reuse the card/grid patterns on other pages.

**Files:**
- Create: `website/templates/website/home.html`

- [ ] **Step 1: Create the `website/templates/website/` directory structure**

```powershell
mkdir website\templates\website
```

- [ ] **Step 2: Create `website/templates/website/home.html`**

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}GKJ Salatiga — Welcome{% endblock %}

{% block content %}

<!-- HERO SECTION -->
<section class="hero">
  {% if hero and hero.background_image %}
    <div class="hero__bg" style="background-image: url('{{ hero.background_image.url }}')"></div>
  {% else %}
    <div class="hero__bg hero__bg--default"></div>
  {% endif %}
  <div class="hero__overlay"></div>
  <div class="container hero__content">
    <h1 class="hero__headline">
      {% if hero %}{{ hero.headline }}{% else %}Welcome to GKJ Salatiga{% endif %}
    </h1>
    <p class="hero__sub">
      {% if hero %}{{ hero.subheadline }}{% else %}A community of faith, hope, and love.{% endif %}
    </p>
    <div class="hero__ctas">
      {% if hero %}
        <a href="{{ hero.cta_primary_url }}" class="btn btn--primary">{{ hero.cta_primary_text }}</a>
        {% if hero.cta_secondary_text %}
          <a href="{{ hero.cta_secondary_url }}" class="btn btn--outline-light">{{ hero.cta_secondary_text }}</a>
        {% endif %}
      {% else %}
        <a href="{% url 'website:visit' %}" class="btn btn--primary">Plan Your Visit</a>
        <a href="{% url 'website:sermon_list' %}" class="btn btn--outline-light">Watch Sermons</a>
      {% endif %}
    </div>
  </div>
</section>

<!-- FEATURED SERMONS -->
{% if featured_sermons %}
<section class="section">
  <div class="container">
    <h2 class="section__title">Latest Messages</h2>
    <div class="card-grid">
      {% for sermon in featured_sermons %}
      <a href="{% url 'website:sermon_detail' sermon.pk %}" class="card">
        {% if sermon.thumbnail %}
          <img src="{{ sermon.thumbnail.url }}" alt="{{ sermon.title }}" class="card__img">
        {% endif %}
        <div class="card__body">
          {% if sermon.topic %}<p class="card__tag">{{ sermon.get_topic_display }}</p>{% endif %}
          <h3 class="card__title">{{ sermon.title }}</h3>
          <p class="card__meta">{{ sermon.pastor }} &middot; {{ sermon.date }}</p>
          <p class="card__text">{{ sermon.description|truncatewords:20 }}</p>
        </div>
      </a>
      {% endfor %}
    </div>
    <div class="section__cta">
      <a href="{% url 'website:sermon_list' %}" class="btn btn--secondary">View All Sermons</a>
    </div>
  </div>
</section>
{% endif %}

<!-- MINISTRIES -->
{% if ministries %}
<section class="section section--dark">
  <div class="container">
    <h2 class="section__title">Our Ministries</h2>
    <div class="card-grid">
      {% for ministry in ministries %}
      <div class="card card--ministry">
        {% if ministry.image %}
          <img src="{{ ministry.image.url }}" alt="{{ ministry.name }}" class="card__img">
        {% endif %}
        <div class="card__body">
          <h3 class="card__title">{{ ministry.name }}</h3>
          <p class="card__text">{{ ministry.description }}</p>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

<!-- SERVICE TIMES -->
{% if service_times %}
<section class="section">
  <div class="container">
    <h2 class="section__title">Join Us This Sunday</h2>
    <div class="service-grid">
      {% for service in service_times %}
      <div class="service-card {% if service.is_online %}service-card--online{% endif %}">
        <h3 class="service-card__name">{{ service.campus_name }}</h3>
        <p class="service-card__times">{{ service.times }}</p>
        <p class="service-card__address">{{ service.address }}</p>
        <a href="{{ service.link_url }}" class="btn btn--primary">{{ service.link_label }}</a>
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

<!-- UPCOMING EVENTS -->
{% if upcoming_events %}
<section class="section section--light">
  <div class="container">
    <h2 class="section__title">Upcoming Events</h2>
    <div class="card-grid">
      {% for event in upcoming_events %}
      <div class="card">
        {% if event.image %}
          <img src="{{ event.image.url }}" alt="{{ event.title }}" class="card__img">
        {% endif %}
        <div class="card__body">
          <h3 class="card__title">{{ event.title }}</h3>
          <p class="card__meta">{{ event.date }} &middot; {{ event.time|time:"H:i" }} &middot; {{ event.location }}</p>
          <p class="card__text">{{ event.description|truncatewords:20 }}</p>
          {% if event.registration_url %}
            <a href="{{ event.registration_url }}" class="btn btn--secondary" target="_blank">Register</a>
          {% endif %}
        </div>
      </div>
      {% endfor %}
    </div>
    <div class="section__cta">
      <a href="{% url 'website:event_list' %}" class="btn btn--secondary">View All Events</a>
    </div>
  </div>
</section>
{% endif %}

{% endblock %}
```

**Key template tags used:**
- `{% if %}` / `{% else %}` / `{% endif %}` — conditional rendering
- `{% for x in items %}` / `{% endfor %}` — loop
- `{{ sermon.get_topic_display }}` — for a `choices` field, Django auto-generates `get_fieldname_display()` which returns the human-readable label
- `{{ sermon.description|truncatewords:20 }}` — a filter that cuts text to 20 words
- `{{ event.time|time:"H:i" }}` — a filter that formats time as 24-hour HH:MM

- [ ] **Step 3: Run the development server and open the home page**

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The page should load with the navbar and footer. Since you haven't added any content yet, the hero will show the default gradient. Add a HeroSlide and ServiceTime in the admin to see them appear.

- [ ] **Step 4: Run tests — home view tests should pass now**

```powershell
python manage.py test website
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```powershell
git add website/templates/
git commit -m "feat: add home page template with hero, sermons, ministries, events sections"
```

---

## Task 9: Sermon Templates

**Files:**
- Create: `website/templates/website/sermons.html`
- Create: `website/templates/website/sermon_detail.html`

- [ ] **Step 1: Create `website/templates/website/sermons.html`**

```html
{% extends 'base.html' %}
{% block title %}Sermons — GKJ Salatiga{% endblock %}

{% block content %}
<header class="page-header">
  <div class="container">
    <h1 class="page-header__title">Messages</h1>
    <p class="page-header__sub">Watch and listen to our latest sermons</p>
  </div>
</header>

<section class="section">
  <div class="container">
    <div class="filter-bar">
      <a href="{% url 'website:sermon_list' %}"
         class="filter-btn {% if not topic %}active{% endif %}">All</a>
      <a href="?topic=faith"
         class="filter-btn {% if topic == 'faith' %}active{% endif %}">Faith</a>
      <a href="?topic=family"
         class="filter-btn {% if topic == 'family' %}active{% endif %}">Family</a>
      <a href="?topic=purpose"
         class="filter-btn {% if topic == 'purpose' %}active{% endif %}">Purpose</a>
      <a href="?topic=prayer"
         class="filter-btn {% if topic == 'prayer' %}active{% endif %}">Prayer</a>
    </div>

    <div class="card-grid">
      {% for sermon in sermons %}
      <a href="{% url 'website:sermon_detail' sermon.pk %}" class="card">
        {% if sermon.thumbnail %}
          <img src="{{ sermon.thumbnail.url }}" alt="{{ sermon.title }}" class="card__img">
        {% endif %}
        <div class="card__body">
          {% if sermon.topic %}<p class="card__tag">{{ sermon.get_topic_display }}</p>{% endif %}
          <h3 class="card__title">{{ sermon.title }}</h3>
          <p class="card__meta">{{ sermon.pastor }} &middot; {{ sermon.date }}</p>
          <p class="card__text">{{ sermon.description|truncatewords:20 }}</p>
        </div>
      </a>
      {% empty %}
      <p style="color: var(--color-text-muted);">No sermons found for this filter.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

- [ ] **Step 2: Create `website/templates/website/sermon_detail.html`**

```html
{% extends 'base.html' %}
{% block title %}{{ sermon.title }} — GKJ Salatiga{% endblock %}

{% block content %}
<div class="sermon-detail">
  <div class="container" style="max-width: 820px;">

    {% if video_id %}
    <div class="video-embed">
      <iframe
        src="https://www.youtube.com/embed/{{ video_id }}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
      </iframe>
    </div>
    {% endif %}

    {% if sermon.series %}
      <p class="card__tag">{{ sermon.series.name }}</p>
    {% endif %}

    <h1 style="font-size: 2rem; font-weight: 800; margin-bottom: 1rem; line-height: 1.2;">
      {{ sermon.title }}
    </h1>

    <div class="sermon-detail__meta">
      <span>{{ sermon.pastor }}</span>
      <span>&middot;</span>
      <span>{{ sermon.date }}</span>
      {% if sermon.topic %}
        <span>&middot;</span>
        <span>{{ sermon.get_topic_display }}</span>
      {% endif %}
    </div>

    <p style="line-height: 1.8; color: var(--color-text-muted);">{{ sermon.description }}</p>

    <div style="margin-top: 2rem;">
      <a href="{% url 'website:sermon_list' %}" class="btn btn--outline">&larr; Back to Sermons</a>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Commit**

```powershell
git add website/templates/website/sermons.html website/templates/website/sermon_detail.html
git commit -m "feat: add sermon list and sermon detail templates"
```

---

## Task 10: Events, About, and Visit Templates

**Files:**
- Create: `website/templates/website/events.html`
- Create: `website/templates/website/about.html`
- Create: `website/templates/website/visit.html`

- [ ] **Step 1: Create `website/templates/website/events.html`**

```html
{% extends 'base.html' %}
{% block title %}Events — GKJ Salatiga{% endblock %}

{% block content %}
<header class="page-header">
  <div class="container">
    <h1 class="page-header__title">Events</h1>
    <p class="page-header__sub">Stay connected with what's happening at GKJ Salatiga</p>
  </div>
</header>

<section class="section">
  <div class="container">
    <div class="card-grid">
      {% for event in events %}
      <div class="card">
        {% if event.image %}
          <img src="{{ event.image.url }}" alt="{{ event.title }}" class="card__img">
        {% endif %}
        <div class="card__body">
          <h3 class="card__title">{{ event.title }}</h3>
          <p class="card__meta">
            {{ event.date }} &middot; {{ event.time|time:"H:i" }} &middot; {{ event.location }}
          </p>
          <p class="card__text">{{ event.description }}</p>
          {% if event.registration_url %}
            <a href="{{ event.registration_url }}" class="btn btn--primary" target="_blank">Register</a>
          {% endif %}
        </div>
      </div>
      {% empty %}
      <p style="color: var(--color-text-muted);">No upcoming events.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

- [ ] **Step 2: Create `website/templates/website/about.html`**

```html
{% extends 'base.html' %}
{% block title %}About — GKJ Salatiga{% endblock %}

{% block content %}
<header class="page-header">
  <div class="container">
    <h1 class="page-header__title">About Us</h1>
    {% if about %}
      <p class="page-header__sub">{{ about.mission_statement }}</p>
    {% endif %}
  </div>
</header>

{% if about %}
<section class="section">
  <div class="container">

    <!-- Pastor section -->
    <div class="about-pastor">
      {% if about.pastor_photo %}
        <img src="{{ about.pastor_photo.url }}" alt="{{ about.pastor_name }}" class="about-pastor__photo">
      {% endif %}
      <div>
        <h2 style="font-size: 1.75rem; font-weight: 700; margin-bottom: 1rem;">
          {{ about.pastor_name }}
        </h2>
        <p style="color: var(--color-text-muted); line-height: 1.8;">{{ about.pastor_bio }}</p>
      </div>
    </div>

    <!-- Core Values -->
    <h2 class="section__title">Our Core Values</h2>
    <div class="values-grid">
      <div class="value-card">
        <h3 class="value-card__title">{{ about.value_1_title }}</h3>
        <p>{{ about.value_1_body }}</p>
      </div>
      <div class="value-card">
        <h3 class="value-card__title">{{ about.value_2_title }}</h3>
        <p>{{ about.value_2_body }}</p>
      </div>
      <div class="value-card">
        <h3 class="value-card__title">{{ about.value_3_title }}</h3>
        <p>{{ about.value_3_body }}</p>
      </div>
      <div class="value-card">
        <h3 class="value-card__title">{{ about.value_4_title }}</h3>
        <p>{{ about.value_4_body }}</p>
      </div>
    </div>

  </div>
</section>
{% else %}
<section class="section">
  <div class="container" style="text-align: center;">
    <p style="color: var(--color-text-muted);">About page content coming soon.</p>
  </div>
</section>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Create `website/templates/website/visit.html`**

```html
{% extends 'base.html' %}
{% block title %}Plan Your Visit — GKJ Salatiga{% endblock %}

{% block content %}
<header class="page-header">
  <div class="container">
    <h1 class="page-header__title">Plan Your Visit</h1>
    <p class="page-header__sub">We'd love to have you join us this Sunday</p>
  </div>
</header>

<section class="section">
  <div class="container">
    <div class="service-grid">
      {% for service in service_times %}
      <div class="service-card {% if service.is_online %}service-card--online{% endif %}">
        <h3 class="service-card__name">{{ service.campus_name }}</h3>
        <p class="service-card__times">{{ service.times }}</p>
        <p class="service-card__address">{{ service.address }}</p>
        <a href="{{ service.link_url }}" class="btn btn--primary">{{ service.link_label }}</a>
      </div>
      {% empty %}
      <p style="color: var(--color-text-muted);">Service information coming soon.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

- [ ] **Step 4: Run full test suite**

```powershell
python manage.py test website
```

Expected: All tests pass (OK).

- [ ] **Step 5: Add some sample data and verify all pages in the browser**

```powershell
python manage.py runserver
```

Visit these URLs and verify each page renders:
- `http://127.0.0.1:8000/` — home
- `http://127.0.0.1:8000/sermons/` — sermon list with filter buttons
- `http://127.0.0.1:8000/events/` — events
- `http://127.0.0.1:8000/about/` — about
- `http://127.0.0.1:8000/visit/` — visit / service times

- [ ] **Step 6: Commit**

```powershell
git add website/templates/website/
git commit -m "feat: add events, about, and visit page templates"
```

---

## Task 11: Create `members` App & Models

**Why:** The members app keeps congregation data separate from public website content. `simple_history` wraps the `Member` model to automatically log every change (who changed what field, when).

**Files:**
- Create: `members/models.py` (full replace)
- Create: `members/admin.py` (full replace)
- Create: `members/tests.py` (full replace)

- [ ] **Step 1: Create the members app**

```powershell
python manage.py startapp members
```

- [ ] **Step 2: Write failing model tests**

Replace `members/tests.py`:

```python
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
        self.assertEqual(members[0], m2)  # Anton comes before Zara
        self.assertEqual(members[1], m1)
```

- [ ] **Step 3: Run tests to confirm they fail**

```powershell
python manage.py test members
```

Expected: ImportError — models not defined yet.

- [ ] **Step 4: Write `members/models.py`**

```python
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

BLOK_CHOICES = [
    ('CK1', 'CK1'), ('CK2', 'CK2'), ('CK3', 'CK3'),
    ('GT1', 'GT1'), ('GT2', 'GT2'),
    ('JS1', 'JS1'), ('JS2', 'JS2'), ('JS3', 'JS3'),
    ('KD1', 'KD1'), ('KD2', 'KD2'),
    ('KP1', 'KP1'), ('KP2', 'KP2'),
    ('KS1', 'KS1'), ('KS2', 'KS2'),
    ('KT1', 'KT1'), ('KT2', 'KT2'), ('KT3', 'KT3'),
    ('KW1', 'KW1'), ('KW2', 'KW2'),
    ('KY1', 'KY1'), ('KY2', 'KY2'), ('KY3', 'KY3'), ('KY4', 'KY4'), ('KY5', 'KY5'),
]


class Keluarga(models.Model):
    no_kk_gereja = models.CharField(max_length=20, unique=True)
    nama_keluarga = models.CharField(max_length=200)
    blok = models.CharField(max_length=10, choices=BLOK_CHOICES)
    alamat = models.TextField()

    class Meta:
        verbose_name_plural = 'Keluarga'
        ordering = ['nama_keluarga']

    def __str__(self):
        return f'{self.nama_keluarga} ({self.no_kk_gereja})'


class Member(models.Model):
    JENIS_KELAMIN = [('L', 'Laki-laki'), ('P', 'Perempuan')]
    STATUS_CHOICES = [('Dewasa', 'Dewasa'), ('Anak', 'Anak')]
    KEWARGAAN_CHOICES = [
        ('Warga', 'Warga'),
        ('Simpatisan', 'Simpatisan'),
        ('Titipan', 'Titipan'),
        ('Luar Kota', 'Luar Kota'),
        ('Meninggal', 'Meninggal'),
    ]
    GOL_DARAH = [('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ('-', 'Tidak Diketahui')]
    KET_STATUS = [
        ('KK', 'Kepala Keluarga'),
        ('Istri', 'Istri'),
        ('Anak', 'Anak'),
        ('Lainnya', 'Lainnya'),
    ]
    PENDIDIKAN_CHOICES = [
        ('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA'), ('D3', 'D3'),
        ('S1', 'S1'), ('S2', 'S2'), ('S3', 'S3'), ('Lainnya', 'Lainnya'),
    ]

    no_sensus = models.CharField(max_length=20, unique=True)
    nama_lengkap = models.CharField(max_length=200)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN)
    tempat_lahir = models.CharField(max_length=100, blank=True)
    tanggal_lahir = models.DateField(null=True, blank=True)
    nomor_telepon = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Dewasa')
    kewargaan = models.CharField(max_length=20, choices=KEWARGAAN_CHOICES, default='Warga')
    gol_darah = models.CharField(max_length=5, choices=GOL_DARAH, blank=True)
    pendidikan = models.CharField(max_length=10, choices=PENDIDIKAN_CHOICES, blank=True)
    pekerjaan = models.CharField(max_length=100, blank=True)
    ket_status = models.CharField(max_length=10, choices=KET_STATUS, blank=True)
    sudah_baptis = models.BooleanField(default=False)
    sudah_sidi = models.BooleanField(default=False)
    tanggal_wafat = models.DateField(null=True, blank=True)
    pelayanan_diikuti = models.TextField(blank=True)
    ibadah_sering_diikuti = models.TextField(blank=True)
    keluarga = models.ForeignKey(
        Keluarga, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='members'
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ['nama_lengkap']

    def __str__(self):
        return self.nama_lengkap


class Majelis(models.Model):
    JABATAN_CHOICES = [
        ('Pendeta', 'Pendeta'),
        ('Penatua', 'Penatua'),
        ('Diaken', 'Diaken'),
        ('Wiyata', 'Wiyata'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='majelis_records')
    jabatan = models.CharField(max_length=20, choices=JABATAN_CHOICES)
    periode_mulai = models.DateField()
    periode_selesai = models.DateField(null=True, blank=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Majelis'

    def __str__(self):
        return f'{self.member} — {self.jabatan}'


class IbadahMingguan(models.Model):
    tanggal = models.DateField(unique=True)
    minggu_ke = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Ibadah Mingguan'
        verbose_name_plural = 'Ibadah Mingguan'
        ordering = ['-tanggal']

    def __str__(self):
        return str(self.tanggal)


class IbadahService(models.Model):
    ibadah = models.ForeignKey(IbadahMingguan, on_delete=models.CASCADE, related_name='services')
    nama_service = models.CharField(max_length=100)
    jumlah_hadir = models.PositiveIntegerField(default=0)
    jumlah_persembahan = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.ibadah} — {self.nama_service}'


class Perpuluhan(models.Model):
    METODE = [('Tunai', 'Tunai'), ('Transfer', 'Transfer'), ('Lainnya', 'Lainnya')]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='perpuluhan')
    tanggal = models.DateField()
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=20, choices=METODE)
    keterangan = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Perpuluhan'
        ordering = ['-tanggal']

    def __str__(self):
        return f'{self.member} — {self.tanggal}'


class IuranPralenan(models.Model):
    METODE = [('Tunai', 'Tunai'), ('Transfer', 'Transfer'), ('Lainnya', 'Lainnya')]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='iuran_pralenan')
    tanggal = models.DateField()
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=20, choices=METODE)
    keterangan = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Iuran Pralenan'
        ordering = ['-tanggal']

    def __str__(self):
        return f'{self.member} — {self.tanggal}'


class MemberStatusHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='status_history')
    status_lama = models.CharField(max_length=20)
    status_baru = models.CharField(max_length=20)
    keterangan = models.TextField(blank=True)
    tanggal = models.DateField(auto_now_add=True)
    dicatat_oleh = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = 'Member Status History'
        ordering = ['-tanggal']

    def __str__(self):
        return f'{self.member} — {self.tanggal}'
```

**Key concepts:**
- `history = HistoricalRecords()` — simple_history adds this field. Every time a Member row is saved or deleted, a snapshot is stored in a separate `members_historicalmember` table automatically.
- `related_name='members'` — allows `keluarga_instance.members.all()` to get all members of a family
- `auto_now_add=True` — automatically sets the field to the current date when the row is first created

- [ ] **Step 5: Write `members/admin.py`**

```python
from django.contrib import admin
from .models import (
    Keluarga, Member, Majelis,
    IbadahMingguan, IbadahService,
    Perpuluhan, IuranPralenan, MemberStatusHistory
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

**New concept:** `TabularInline` — displays related records (IbadahService rows) directly inside the parent (IbadahMingguan) form, as a table. `extra = 1` means one blank row is shown by default.

- [ ] **Step 6: Create and apply migrations**

```powershell
python manage.py makemigrations members
python manage.py migrate
```

- [ ] **Step 7: Run tests**

```powershell
python manage.py test members
```

Expected: OK — 3 tests pass.

- [ ] **Step 8: Commit**

```powershell
git add members/
git commit -m "feat: add members app with models, admin, and initial tests"
```

---

## Task 12: (Optional) LEARNING_GUIDE.md

This is a reference document at the project root explaining everything step by step for future reference.

**Files:**
- Create: `LEARNING_GUIDE.md`

- [ ] **Step 1: Create `LEARNING_GUIDE.md` at the project root**

```markdown
# GKJ Salatiga — Django Learning Guide

A step-by-step reference for understanding how this project is built.

## 1. Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 2. Project Structure

- `church_site/` — Project configuration (settings, root URLs)
- `website/` — Public-facing church site
- `members/` — Internal member management (staff-only)
- `static/` — CSS, JS, images
- `media/` — User-uploaded files (images)
- `templates/` — Shared templates (base.html)

## 3. Models

Models are Python classes that map to database tables. Each attribute becomes a column.

```python
class Sermon(models.Model):
    title = models.CharField(max_length=200)   # text, max 200 chars
    date  = models.DateField()                 # stores a date
    is_featured = models.BooleanField()        # True/False
```

Run `python manage.py makemigrations` after changing models.
Run `python manage.py migrate` to apply changes to the database.

## 4. Admin

Register models in `admin.py` to manage them in `/admin/`:

```python
@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ['title', 'pastor', 'date']
    search_fields = ['title', 'pastor']
```

## 5. Views

Views are functions that receive a request and return a rendered template:

```python
def sermon_list(request):
    sermons = Sermon.objects.all()
    return render(request, 'website/sermons.html', {'sermons': sermons})
```

`Sermon.objects.all()` queries all rows from the database.

## 6. URL Routing

Map URLs to views in `urls.py`:

```python
urlpatterns = [
    path('sermons/', views.sermon_list, name='sermon_list'),
    path('sermons/<int:pk>/', views.sermon_detail, name='sermon_detail'),
]
```

`<int:pk>` captures an integer from the URL and passes it as `pk` to the view.

## 7. Templates

Templates use `{% %}` for logic and `{{ }}` for variables:

```html
{% for sermon in sermons %}
  <h3>{{ sermon.title }}</h3>
  <p>{{ sermon.pastor }} · {{ sermon.date }}</p>
{% endfor %}
```

## 8. Template Inheritance

`base.html` defines the shared structure. Pages extend it:

```html
{% extends 'base.html' %}
{% block content %}
  <h1>Page content here</h1>
{% endblock %}
```

## 9. Static Files

In templates: `{% load static %}` then `{% static 'css/style.css' %}`.
In `settings.py`: `STATICFILES_DIRS = [BASE_DIR / 'static']`.

## 10. Media Files (Images)

`ImageField` stores the file path. Pillow must be installed.
Access in templates: `{{ sermon.thumbnail.url }}`.
In development, add `static(MEDIA_URL, document_root=MEDIA_ROOT)` to `urls.py`.

## 11. Pagination

```python
from django.core.paginator import Paginator
paginator = Paginator(members, 25)   # 25 per page
page = paginator.get_page(request.GET.get('page'))
```

In template: `{% for member in page %}`.

## 12. Search with Q objects

```python
from django.db.models import Q
members = Member.objects.filter(
    Q(nama_lengkap__icontains=query) | Q(no_sensus__icontains=query)
)
```

`Q` objects let you combine filter conditions with `|` (OR) and `&` (AND).

## 13. Login Required

```python
from django.contrib.auth.decorators import login_required

@login_required
def member_list(request):
    ...
```

Set `LOGIN_URL` in settings to control where unauthenticated users are redirected.
```

- [ ] **Step 2: Commit**

```powershell
git add LEARNING_GUIDE.md
git commit -m "docs: add learning guide for project reference"
```

---

## Task 13: Members Views & URL Routing

**Files:**
- Create: `members/views.py` (full replace)
- Create: `members/urls.py`
- Modify: `members/tests.py` (add view tests)

- [ ] **Step 1: Write failing view tests**

Add to `members/tests.py`:

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Keluarga, Member


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
```

- [ ] **Step 2: Run tests to confirm they fail**

```powershell
python manage.py test members
```

Expected: errors because views and URLs don't exist.

- [ ] **Step 3: Write `members/views.py`**

```python
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Member, Keluarga


@login_required
def member_list(request):
    query = request.GET.get('q', '')
    members = Member.objects.select_related('keluarga').all()
    if query:
        members = members.filter(
            Q(nama_lengkap__icontains=query) | Q(no_sensus__icontains=query)
        )
    paginator = Paginator(members, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'members/member_list.html', {'page': page, 'query': query})


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'members/member_detail.html', {'member': member})


@login_required
def family_list(request):
    query = request.GET.get('q', '')
    families = Keluarga.objects.all()
    if query:
        families = families.filter(nama_keluarga__icontains=query)
    paginator = Paginator(families, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'members/family_list.html', {'page': page, 'query': query})
```

**Key concepts:**
- `select_related('keluarga')` — fetches related Keluarga data in the same query (avoids N+1 query problem)
- `Paginator(queryset, 25)` — splits the queryset into pages of 25 items
- `paginator.get_page(page_number)` — safe — if the page number is invalid/missing, returns the first page

- [ ] **Step 4: Create `members/urls.py`**

```python
from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('families/', views.family_list, name='family_list'),
]
```

- [ ] **Step 5: Run tests — they fail because templates don't exist yet**

```powershell
python manage.py test members
```

Expected: `TemplateDoesNotExist` errors.

- [ ] **Step 6: Commit**

```powershell
git add members/views.py members/urls.py members/tests.py
git commit -m "feat: add members views and URL routing with login protection"
```

---

## Task 14: Members Templates

**Files:**
- Create: `members/templates/members/member_list.html`
- Create: `members/templates/members/member_detail.html`
- Create: `members/templates/members/family_list.html`

- [ ] **Step 1: Create the template directory**

```powershell
mkdir members\templates\members
```

- [ ] **Step 2: Create `members/templates/members/member_list.html`**

```html
{% extends 'base.html' %}
{% block title %}Members — GKJ Salatiga{% endblock %}

{% block content %}
<div class="members-layout">
  <div class="container">

    <div class="members-header">
      <h1>Members</h1>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <a href="{% url 'members:family_list' %}" class="btn btn--outline">Families</a>
        <a href="/admin/" class="btn btn--primary">Admin</a>
      </div>
    </div>

    <form class="search-form" method="get" style="margin-bottom: 1.5rem;">
      <input type="text" name="q" value="{{ query }}" placeholder="Search by name or ID...">
      <button type="submit" class="btn btn--primary">Search</button>
    </form>

    <table class="data-table">
      <thead>
        <tr>
          <th>No. Sensus</th>
          <th>Nama</th>
          <th>Status</th>
          <th>Kewargaan</th>
          <th>Keluarga</th>
        </tr>
      </thead>
      <tbody>
        {% for member in page %}
        <tr>
          <td>{{ member.no_sensus }}</td>
          <td>
            <a href="{% url 'members:member_detail' member.pk %}">{{ member.nama_lengkap }}</a>
          </td>
          <td>{{ member.status }}</td>
          <td>
            <span class="badge badge--{{ member.kewargaan|lower|cut:' ' }}">
              {{ member.kewargaan }}
            </span>
          </td>
          <td>{% if member.keluarga %}{{ member.keluarga.nama_keluarga }}{% else %}—{% endif %}</td>
        </tr>
        {% empty %}
        <tr><td colspan="5" style="color: var(--color-text-muted);">No members found.</td></tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="pagination">
      {% if page.has_previous %}
        <a href="?page={{ page.previous_page_number }}{% if query %}&q={{ query }}{% endif %}">&laquo; Prev</a>
      {% endif %}
      <span class="current">{{ page.number }} of {{ page.paginator.num_pages }}</span>
      {% if page.has_next %}
        <a href="?page={{ page.next_page_number }}{% if query %}&q={{ query }}{% endif %}">Next &raquo;</a>
      {% endif %}
    </div>

  </div>
</div>
{% endblock %}
```

**Pagination explained:**
- `page.has_previous` / `page.has_next` — whether there's a previous/next page
- `page.previous_page_number` / `page.next_page_number` — the page numbers
- We preserve the `q` query param in pagination links so search + pagination work together

- [ ] **Step 3: Create `members/templates/members/member_detail.html`**

```html
{% extends 'base.html' %}
{% block title %}{{ member.nama_lengkap }} — GKJ Salatiga{% endblock %}

{% block content %}
<div class="members-layout">
  <div class="container" style="max-width: 900px;">

    <div style="margin-bottom: 1.5rem;">
      <a href="{% url 'members:member_list' %}" class="btn btn--outline">&larr; Back to Members</a>
    </div>

    <h1 style="font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">
      {{ member.nama_lengkap }}
    </h1>
    <p style="color: var(--color-text-muted); margin-bottom: 2rem;">No. Sensus: {{ member.no_sensus }}</p>

    <!-- Personal Data -->
    <div class="detail-section">
      <h3>Data Pribadi</h3>
      <div class="detail-grid">
        <div class="detail-item">
          <p class="detail-item__label">Jenis Kelamin</p>
          <p class="detail-item__value">{{ member.get_jenis_kelamin_display }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Status</p>
          <p class="detail-item__value">{{ member.status }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Kewargaan</p>
          <p class="detail-item__value">
            <span class="badge badge--{{ member.kewargaan|lower|cut:' ' }}">
              {{ member.kewargaan }}
            </span>
          </p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Tempat, Tanggal Lahir</p>
          <p class="detail-item__value">
            {{ member.tempat_lahir|default:"—" }}{% if member.tanggal_lahir %}, {{ member.tanggal_lahir }}{% endif %}
          </p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Nomor Telepon</p>
          <p class="detail-item__value">{{ member.nomor_telepon|default:"—" }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Golongan Darah</p>
          <p class="detail-item__value">{{ member.gol_darah|default:"—" }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Pendidikan</p>
          <p class="detail-item__value">{{ member.pendidikan|default:"—" }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Pekerjaan</p>
          <p class="detail-item__value">{{ member.pekerjaan|default:"—" }}</p>
        </div>
      </div>
    </div>

    <!-- Church Status -->
    <div class="detail-section">
      <h3>Status Gereja</h3>
      <div class="detail-grid">
        <div class="detail-item">
          <p class="detail-item__label">Sudah Baptis</p>
          <p class="detail-item__value">{% if member.sudah_baptis %}Ya{% else %}Belum{% endif %}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Sudah Sidi</p>
          <p class="detail-item__value">{% if member.sudah_sidi %}Ya{% else %}Belum{% endif %}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Ket. Status dalam Keluarga</p>
          <p class="detail-item__value">{{ member.ket_status|default:"—" }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-item__label">Keluarga</p>
          <p class="detail-item__value">
            {% if member.keluarga %}{{ member.keluarga.nama_keluarga }}{% else %}—{% endif %}
          </p>
        </div>
      </div>
    </div>

    {% if member.pelayanan_diikuti %}
    <div class="detail-section">
      <h3>Pelayanan</h3>
      <p>{{ member.pelayanan_diikuti }}</p>
    </div>
    {% endif %}

    {% if member.ibadah_sering_diikuti %}
    <div class="detail-section">
      <h3>Ibadah Sering Diikuti</h3>
      <p>{{ member.ibadah_sering_diikuti }}</p>
    </div>
    {% endif %}

    <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
      <a href="/admin/members/member/{{ member.pk }}/change/" class="btn btn--primary">Edit in Admin</a>
      <a href="{% url 'members:member_list' %}" class="btn btn--outline">Back to List</a>
    </div>

  </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Create `members/templates/members/family_list.html`**

```html
{% extends 'base.html' %}
{% block title %}Keluarga — GKJ Salatiga{% endblock %}

{% block content %}
<div class="members-layout">
  <div class="container">

    <div class="members-header">
      <h1>Keluarga</h1>
      <a href="{% url 'members:member_list' %}" class="btn btn--outline">&larr; Members</a>
    </div>

    <form class="search-form" method="get" style="margin-bottom: 1.5rem;">
      <input type="text" name="q" value="{{ query }}" placeholder="Search family name...">
      <button type="submit" class="btn btn--primary">Search</button>
    </form>

    <table class="data-table">
      <thead>
        <tr>
          <th>No. KK Gereja</th>
          <th>Nama Keluarga</th>
          <th>Blok</th>
          <th>Alamat</th>
          <th>Jumlah Anggota</th>
        </tr>
      </thead>
      <tbody>
        {% for family in page %}
        <tr>
          <td>{{ family.no_kk_gereja }}</td>
          <td>{{ family.nama_keluarga }}</td>
          <td>{{ family.blok }}</td>
          <td>{{ family.alamat|truncatechars:60 }}</td>
          <td>{{ family.members.count }}</td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="5" style="color: var(--color-text-muted);">No families found.</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="pagination">
      {% if page.has_previous %}
        <a href="?page={{ page.previous_page_number }}{% if query %}&q={{ query }}{% endif %}">&laquo; Prev</a>
      {% endif %}
      <span class="current">{{ page.number }} of {{ page.paginator.num_pages }}</span>
      {% if page.has_next %}
        <a href="?page={{ page.next_page_number }}{% if query %}&q={{ query }}{% endif %}">Next &raquo;</a>
      {% endif %}
    </div>

  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run the full test suite**

```powershell
python manage.py test
```

Expected: All tests pass (OK).

- [ ] **Step 6: Verify members area in the browser**

```powershell
python manage.py runserver
```

1. Open `http://127.0.0.1:8000/members/` — you should be redirected to the admin login
2. Log in with your superuser credentials
3. You should see the members list (empty at first — add members via `/admin/`)
4. Visit `http://127.0.0.1:8000/members/families/` to see the families list

- [ ] **Step 7: Final commit**

```powershell
git add members/templates/
git commit -m "feat: add members list, detail, and family list templates"
```

---

## Verification Checklist

After completing all tasks, verify the following:

- [ ] `python manage.py test` — all tests pass with no errors
- [ ] Home page (`/`) renders: hero, sermon cards (if data), ministry grid, service times, events
- [ ] Sermon list (`/sermons/`) shows topic filter buttons, clicking a filter works
- [ ] Sermon detail (`/sermons/1/`) embeds a YouTube video when `youtube_url` is set
- [ ] Events (`/events/`) renders event cards
- [ ] About (`/about/`) renders pastor section and values (after adding an AboutPage in admin)
- [ ] Visit (`/visit/`) renders service time cards
- [ ] `/members/` redirects unauthenticated visitors to the admin login
- [ ] After logging in as staff, `/members/` shows the paginated member table
- [ ] Search on `/members/` filters by name and ID
- [ ] `/members/families/` shows families with member count
- [ ] Django Admin at `/admin/` shows all models with correct list columns and filters
- [ ] Adding a Sermon in admin and marking `is_featured=True` makes it appear on the home page

---

## Next Steps (Out of Scope for Now)

Once the above is working, these are logical next steps:

1. **PostgreSQL** — swap SQLite for PostgreSQL for production: `pip install psycopg2-binary` and update `DATABASES` in settings
2. **Deployment** — Gunicorn + Nginx on a VPS, or Railway/Render cloud hosting
3. **Excel export** — `pip install openpyxl`, add a view that returns an `.xlsx` response for Perpuluhan/IuranPralenan data
4. **Statistics dashboard** — aggregate queries using `annotate()` and `Count()`
5. **Birthday list** — filter members by birth month with `tanggal_lahir__month`
