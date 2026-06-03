# Database Improvement — Option 1: Quick Wins

**Date:** 2026-06-03
**Scope:** Additive changes only — no existing data deleted or restructured
**Apps affected:** `members`, `website`

---

## 1. Bug Fix — BLOK_CHOICES

**File:** `members/models.py` line 11

The display label for `KM3` incorrectly reads `KM1`. Fix: change the tuple value.

```python
# Before
('KM3', 'KM1'),

# After
('KM3', 'KM3'),
```

No migration needed — choices are stored as the key value in the database, not the label.

---

## 2. Database Indexes

**File:** `members/models.py`

Add `db_index=True` to fields commonly used in filters and searches. One migration generated.

| Model | Field | Reason |
|---|---|---|
| `Member` | `kewargaan` | Filter by membership status (Warga, Simpatisan, etc.) |
| `Member` | `blok` | Filter members by blok/area |
| `Member` | `tanggal_lahir` | Birthday queries and age-range filters |
| `WartaJemaat` | `category` | Filter by warta / liturgi / pengumuman on public pages |
| `Sermon` | `topic` | Filter by topic on public sermons page |

```python
# members/models.py — Member
kewargaan = models.CharField(max_length=20, choices=KEWARGAAN_CHOICES, default='Warga', db_index=True)
blok = models.CharField(max_length=10, choices=BLOK_CHOICES, db_index=True)
tanggal_lahir = models.DateField(null=True, blank=True, db_index=True)

# website/models.py — WartaJemaat
category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='warta', db_index=True)

# website/models.py — Sermon
topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, blank=True, db_index=True)
```

---

## 3. Timestamps

**File:** `website/models.py`

Add `created_at = models.DateTimeField(auto_now_add=True)` to four models. `Member` is excluded because it already has `HistoricalRecords` which tracks creation and change history.

Models receiving `created_at`:
- `Sermon`
- `WartaJemaat`
- `Event`
- `Album`

Django will generate one migration. For existing rows, `auto_now_add=True` automatically uses `django.utils.timezone.now` as the default in the generated migration file — no manual prompt or intervention needed.

---

## 4. Slug Fields

**File:** `website/models.py`, `website/urls.py`, `website/views.py`, relevant templates

Add a `SlugField` to four public-facing models so URLs are human-readable and SEO-friendly.

Models receiving `slug`:
- `Sermon`
- `WartaJemaat`
- `Album`
- `Event`

### Model change

```python
from django.utils.text import slugify

# Add to each model:
slug = models.SlugField(max_length=220, unique=True, blank=True)

def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(f"{self.title}-{self.date}")
    super().save(*args, **kwargs)
```

### URL change

```python
# Before
path('sermon/<int:pk>/', views.sermon_detail, name='sermon_detail'),

# After
path('sermon/<slug:slug>/', views.sermon_detail, name='sermon_detail'),
```

### View change

```python
# Before
sermon = get_object_or_404(Sermon, pk=pk)

# After
sermon = get_object_or_404(Sermon, slug=slug)
```

### Existing records — one-time slug population

After running migrations, existing records will have empty slug fields. Run this in the Django shell once:

```python
from website.models import Sermon, WartaJemaat, Album, Event
from django.utils.text import slugify

for model in [Sermon, WartaJemaat, Album, Event]:
    for obj in model.objects.filter(slug=''):
        obj.slug = slugify(f"{obj.title}-{obj.date}")
        obj.save()
```

If two records produce the same slug (same title + date), add a counter suffix:

```python
base = slugify(f"{obj.title}-{obj.date}")
slug = base
counter = 1
while model.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
    slug = f"{base}-{counter}"
    counter += 1
obj.slug = slug
obj.save()
```

---

## Migration Order

1. `python manage.py makemigrations members` — indexes on Member fields
2. `python manage.py makemigrations website` — indexes on WartaJemaat/Sermon + timestamps + slugs
3. `python manage.py migrate`
4. Run the one-time slug population script in the Django shell
5. Verify all existing records have slugs before testing URLs

---

## Testing Checklist

- [ ] `BLOK_CHOICES` — check admin dropdown shows `KM3` correctly
- [ ] Indexes — run `python manage.py dbshell` and verify indexes with `.indexes` or `PRAGMA index_list`
- [ ] Timestamps — create a new Sermon/Event in admin, confirm `created_at` is populated
- [ ] Slugs — visit `/sermon/<slug>/`, `/warta/<slug>/`, `/album/<slug>/`, `/event/<slug>/` and confirm detail pages load
- [ ] Slugs — create a new record in admin and confirm slug is auto-generated
- [ ] No broken links — check that existing template `{% url %}` tags use slug, not pk
