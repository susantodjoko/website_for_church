# Database Option 1 — Quick Wins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix a data bug, add query indexes, add created_at timestamps, and switch public detail URLs from integer PKs to human-readable slugs.

**Architecture:** All changes are additive — no existing data is deleted or restructured. The slug migration uses a two-step approach: add the nullable field first, populate existing records via Django shell, then apply the unique constraint. This ensures no data loss even if a DB already has rows.

**Tech Stack:** Django 5, SQLite (dev), `python manage.py` for migrations, Django shell for one-time population script.

---

### Task 1: Fix BLOK_CHOICES Bug

**Files:**
- Modify: `members/models.py`
- Test: `members/test.py`

- [ ] **Step 1: Write failing test**

Add this class to `members/test.py`:

```python
class BlokChoicesTest(TestCase):
    def test_km3_display_label_is_correct(self):
        m = Member(blok='KM3')
        self.assertEqual(m.get_blok_display(), 'KM3')
```

- [ ] **Step 2: Run test — confirm it fails**

```
python manage.py test members.test.BlokChoicesTest
```

Expected: FAIL with `AssertionError: 'KM1' != 'KM3'`

- [ ] **Step 3: Fix the bug**

In `members/models.py` line 11, change:
```python
('KM3', 'KM1'),
```
to:
```python
('KM3', 'KM3'),
```

- [ ] **Step 4: Run test — confirm it passes**

```
python manage.py test members.test.BlokChoicesTest
```

Expected: PASS

- [ ] **Step 5: Commit**

```
git add members/models.py members/test.py
git commit -m "fix: correct KM3 display label in BLOK_CHOICES"
```

---

### Task 2: Add Database Indexes

**Files:**
- Modify: `members/models.py`
- Modify: `website/models.py`
- New migration: auto-generated in `members/migrations/`
- New migration: auto-generated in `website/migrations/`

Indexes are transparent to application logic — no new tests needed. Existing tests verify nothing broke.

- [ ] **Step 1: Add db_index to three Member fields in `members/models.py`**

Find these three field definitions and add `db_index=True`:

```python
blok = models.CharField(max_length=10, choices=BLOK_CHOICES, db_index=True)
tanggal_lahir = models.DateField(null=True, blank=True, db_index=True)
kewargaan = models.CharField(max_length=20, choices=KEWARGAAN_CHOICES, default='Warga', db_index=True)
```

- [ ] **Step 2: Add db_index to Sermon.topic and WartaJemaat.category in `website/models.py`**

```python
# In the Sermon model:
topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, blank=True, db_index=True)

# In the WartaJemaat model:
category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='warta', db_index=True)
```

- [ ] **Step 3: Generate migrations for both apps**

```
python manage.py makemigrations members
python manage.py makemigrations website
```

Expected: one new migration file in each app's `migrations/` folder.

- [ ] **Step 4: Apply migrations**

```
python manage.py migrate
```

Expected: OK for all migrations.

- [ ] **Step 5: Run all tests to confirm nothing broke**

```
python manage.py test members website
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```
git add members/models.py website/models.py members/migrations/ website/migrations/
git commit -m "perf: add db_index to Member.kewargaan, blok, tanggal_lahir, Sermon.topic, WartaJemaat.category"
```

---

### Task 3: Add created_at Timestamps

**Files:**
- Modify: `website/models.py`
- Modify: `website/tests.py`
- New migration: auto-generated in `website/migrations/`

- [ ] **Step 1: Update the import line in `website/tests.py`**

The existing import only covers some models. Change it to include `WartaJemaat` and `Album`:

```python
from .models import HeroSlide, Sermon, SermonSeries, Ministry, ServiceTime, Event, AboutPage, WartaJemaat, Album
```

- [ ] **Step 2: Write failing tests**

Add these classes to `website/tests.py`:

```python
class SermonTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        sermon = Sermon.objects.create(
            title='Test Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        self.assertIsNotNone(sermon.created_at)


class WartaTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        warta = WartaJemaat.objects.create(
            title='Test Warta', date=date(2025, 1, 1)
        )
        self.assertIsNotNone(warta.created_at)


class EventTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        event = Event.objects.create(
            title='Test Event', date=date(2025, 1, 1),
            time='09:00', location='Church', description='desc'
        )
        self.assertIsNotNone(event.created_at)


class AlbumTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        album = Album.objects.create(
            title='Test Album', date=date(2025, 1, 1), cover_image=''
        )
        self.assertIsNotNone(album.created_at)
```

- [ ] **Step 3: Run tests — confirm they fail**

```
python manage.py test website.tests.SermonTimestampTest website.tests.WartaTimestampTest website.tests.EventTimestampTest website.tests.AlbumTimestampTest
```

Expected: FAIL with `AttributeError: 'Sermon' object has no attribute 'created_at'`

- [ ] **Step 4: Add created_at to four models in `website/models.py`**

Add `created_at = models.DateTimeField(auto_now_add=True)` as the last field in each of these four models:

```python
class Sermon(models.Model):
    # ... (all existing fields) ...
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ← add this line

class WartaJemaat(models.Model):
    # ... (all existing fields) ...
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ← add this line

class Event(models.Model):
    # ... (all existing fields) ...
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ← add this line

class Album(models.Model):
    # ... (all existing fields) ...
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ← add this line
```

- [ ] **Step 5: Generate and apply migration**

```
python manage.py makemigrations website
python manage.py migrate
```

`auto_now_add=True` tells Django to use `django.utils.timezone.now` for existing rows — no manual input required.

- [ ] **Step 6: Run all tests — confirm they pass**

```
python manage.py test website
```

Expected: all pass.

- [ ] **Step 7: Commit**

```
git add website/models.py website/migrations/ website/tests.py
git commit -m "feat: add created_at timestamp to Sermon, WartaJemaat, Event, Album"
```

---

### Task 4: Add Slug Fields to Sermon, WartaJemaat, Album

**Files:**
- Modify: `website/models.py`
- Modify: `website/tests.py`
- New migration: auto-generated in `website/migrations/`

Note: `Event` is skipped — it has no detail URL, so a slug field would be unused.

- [ ] **Step 1: Write failing slug tests**

Add these classes to `website/tests.py`:

```python
class SermonSlugTest(TestCase):
    def test_slug_auto_generated_on_save(self):
        sermon = Sermon.objects.create(
            title='Walking by Faith', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        self.assertEqual(sermon.slug, 'walking-by-faith-2025-06-01')

    def test_duplicate_slugs_get_numeric_suffix(self):
        Sermon.objects.create(
            title='Same Title', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        s2 = Sermon.objects.create(
            title='Same Title', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz'
        )
        self.assertEqual(s2.slug, 'same-title-2025-06-01-1')


class WartaSlugTest(TestCase):
    def test_slug_auto_generated_on_save(self):
        warta = WartaJemaat.objects.create(
            title='Warta Minggu Ini', date=date(2025, 6, 1)
        )
        self.assertEqual(warta.slug, 'warta-minggu-ini-2025-06-01')


class AlbumSlugTest(TestCase):
    def test_slug_auto_generated_on_save(self):
        album = Album.objects.create(
            title='Foto Natal', date=date(2025, 12, 25), cover_image=''
        )
        self.assertEqual(album.slug, 'foto-natal-2025-12-25')
```

- [ ] **Step 2: Run tests — confirm they fail**

```
python manage.py test website.tests.SermonSlugTest website.tests.WartaSlugTest website.tests.AlbumSlugTest
```

Expected: FAIL with `AttributeError: 'Sermon' object has no attribute 'slug'`

- [ ] **Step 3: Add slugify import to `website/models.py`**

Add at the top of the file, with the other imports:

```python
from django.utils.text import slugify
```

- [ ] **Step 4: Add SlugField and save() to Sermon in `website/models.py`**

Add inside the `Sermon` class, after `created_at`:

```python
slug = models.SlugField(max_length=220, blank=True, null=True)

def save(self, *args, **kwargs):
    if not self.slug:
        base = slugify(f"{self.title}-{self.date}")
        slug = base
        counter = 1
        while Sermon.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        self.slug = slug
    super().save(*args, **kwargs)
```

- [ ] **Step 5: Add SlugField and save() to WartaJemaat in `website/models.py`**

Add inside the `WartaJemaat` class, after `created_at`:

```python
slug = models.SlugField(max_length=220, blank=True, null=True)

def save(self, *args, **kwargs):
    if not self.slug:
        base = slugify(f"{self.title}-{self.date}")
        slug = base
        counter = 1
        while WartaJemaat.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        self.slug = slug
    super().save(*args, **kwargs)
```

- [ ] **Step 6: Add SlugField and save() to Album in `website/models.py`**

Add inside the `Album` class, after `created_at`:

```python
slug = models.SlugField(max_length=220, blank=True, null=True)

def save(self, *args, **kwargs):
    if not self.slug:
        base = slugify(f"{self.title}-{self.date}")
        slug = base
        counter = 1
        while Album.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        self.slug = slug
    super().save(*args, **kwargs)
```

- [ ] **Step 7: Generate and apply migration**

```
python manage.py makemigrations website
python manage.py migrate
```

- [ ] **Step 8: Run slug tests — confirm they pass**

```
python manage.py test website.tests.SermonSlugTest website.tests.WartaSlugTest website.tests.AlbumSlugTest
```

Expected: all pass.

- [ ] **Step 9: Commit**

```
git add website/models.py website/migrations/ website/tests.py
git commit -m "feat: add auto-generating slug field to Sermon, WartaJemaat, Album"
```

---

### Task 5: Populate Slugs on Existing Records + Apply Unique Constraint

**Files:**
- Modify: `website/models.py`
- New migration: auto-generated in `website/migrations/`

- [ ] **Step 1: Populate slugs on existing records**

Open the Django shell:

```
python manage.py shell
```

Run this script (paste block by block):

```python
from website.models import Sermon, WartaJemaat, Album
from django.utils.text import slugify

for Model in [Sermon, WartaJemaat, Album]:
    for obj in Model.objects.filter(slug__isnull=True):
        base = slugify(f"{obj.title}-{obj.date}")
        slug = base
        counter = 1
        while Model.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        obj.slug = slug
        obj.save()

# Verify — all three should print 0
print("Sermon without slug:", Sermon.objects.filter(slug__isnull=True).count())
print("WartaJemaat without slug:", WartaJemaat.objects.filter(slug__isnull=True).count())
print("Album without slug:", Album.objects.filter(slug__isnull=True).count())
```

Expected: all three counts print `0`. Exit with `exit()`.

- [ ] **Step 2: Apply unique constraint — update models**

In `website/models.py`, change the `slug` field definition in **all three models** — remove `null=True`, add `unique=True`:

```python
# In Sermon, WartaJemaat, and Album (all three):
slug = models.SlugField(max_length=220, unique=True, blank=True)
```

- [ ] **Step 3: Generate and apply migration**

```
python manage.py makemigrations website
python manage.py migrate
```

- [ ] **Step 4: Run all tests**

```
python manage.py test website
```

Expected: all pass.

- [ ] **Step 5: Commit**

```
git add website/models.py website/migrations/
git commit -m "feat: apply unique constraint to Sermon, WartaJemaat, Album slug fields"
```

---

### Task 6: Update URLs, Views, and Templates to Use Slugs

**Files:**
- Modify: `website/urls.py`
- Modify: `website/views.py`
- Modify: `website/templates/website/home.html` (2 changes)
- Modify: `website/templates/website/sermons.html` (1 change)
- Modify: `website/templates/website/series_detail.html` (1 change)
- Modify: `website/templates/website/warta.html` (1 change)
- Modify: `website/templates/website/gallery.html` (1 change)
- Modify: `website/tests.py`

- [ ] **Step 1: Write failing view tests**

Add these classes to `website/tests.py`:

```python
class SermonDetailSlugViewTest(TestCase):
    def test_detail_view_accessible_by_slug(self):
        sermon = Sermon.objects.create(
            title='Faith Walk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertEqual(response.status_code, 200)


class WartaDetailSlugViewTest(TestCase):
    def test_detail_view_accessible_by_slug(self):
        warta = WartaJemaat.objects.create(
            title='Warta Test', date=date(2025, 1, 1)
        )
        response = self.client.get(
            reverse('website:warta_detail', kwargs={'slug': warta.slug})
        )
        self.assertEqual(response.status_code, 200)


class AlbumDetailSlugViewTest(TestCase):
    def test_detail_view_accessible_by_slug(self):
        album = Album.objects.create(
            title='Foto Test', date=date(2025, 12, 25), cover_image=''
        )
        response = self.client.get(
            reverse('website:album_detail', kwargs={'slug': album.slug})
        )
        self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Run tests — confirm they fail**

```
python manage.py test website.tests.SermonDetailSlugViewTest website.tests.WartaDetailSlugViewTest website.tests.AlbumDetailSlugViewTest
```

Expected: FAIL with `NoReverseMatch` — the URL patterns still use `<int:pk>`.

- [ ] **Step 3: Update `website/urls.py`**

Change three path entries:

```python
path('sermons/<slug:slug>/', views.sermon_detail, name='sermon_detail'),
path('warta/<slug:slug>/',   views.warta_detail,  name='warta_detail'),
path('gallery/<slug:slug>/', views.album_detail,  name='album_detail'),
```

- [ ] **Step 4: Update three view functions in `website/views.py`**

Replace `sermon_detail`:

```python
def sermon_detail(request, slug):
    sermon = get_object_or_404(Sermon, slug=slug)
    video_id = _extract_youtube_id(sermon.youtube_url)
    return render(request, 'website/sermon_detail.html', {
        'sermon': sermon,
        'video_id': video_id,
    })
```

Replace `warta_detail`:

```python
def warta_detail(request, slug):
    warta = get_object_or_404(WartaJemaat, slug=slug)
    return render(request, 'website/warta_detail.html', {'warta': warta})
```

Replace `album_detail`:

```python
def album_detail(request, slug):
    album = get_object_or_404(Album, slug=slug)
    photos = album.photos.all()
    return render(request, 'website/album_detail.html', {
        'album': album,
        'photos': photos,
    })
```

- [ ] **Step 5: Update `website/templates/website/home.html`**

Change line 61 (sermon link):
```html
<a href="{% url 'website:sermon_detail' sermon.slug %}" class="card">
```

Change line 167 (warta link):
```html
<a href="{% url 'website:warta_detail' item.slug %}" class="btn btn--secondary">Baca Selengkapnya</a>
```

- [ ] **Step 6: Update `website/templates/website/sermons.html`**

Change line 29:
```html
<a href="{% url 'website:sermon_detail' sermon.slug %}" class="card">
```

- [ ] **Step 7: Update `website/templates/website/series_detail.html`**

Change line 16:
```html
<a href="{% url 'website:sermon_detail' sermon.slug %}" class="card">
```

- [ ] **Step 8: Update `website/templates/website/warta.html`**

Change line 44:
```html
<a href="{% url 'website:warta_detail' item.slug %}" class="btn btn--secondary">Baca Selengkapnya</a>
```

- [ ] **Step 9: Update `website/templates/website/gallery.html`**

Change line 18:
```html
<a href="{% url 'website:album_detail' album.slug %}" class="card">
```

- [ ] **Step 10: Run all tests**

```
python manage.py test members website
```

Expected: all tests pass.

- [ ] **Step 11: Commit**

```
git add website/urls.py website/views.py website/templates/ website/tests.py
git commit -m "feat: switch sermon, warta, album detail URLs from pk to slug"
```

---

## Summary

| Task | Change | Migration? |
|---|---|---|
| 1 | Fix KM3 display label | No |
| 2 | Add 5 db indexes | Yes (members + website) |
| 3 | Add created_at to 4 models | Yes (website) |
| 4 | Add nullable slug to 3 models | Yes (website) |
| 5 | Populate slugs + apply unique | Yes (website) |
| 6 | URLs / views / 5 templates | No |
