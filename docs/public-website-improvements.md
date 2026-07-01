# GKJ Salatiga — Public Website Improvements

A step-by-step implementation guide for extending the public-facing church website.

---

## Feature List

| # | Feature | Status |
|---|---|---|
| 1 | Pagination on News & Liturgi | [ ] |
| 2 | Search on News & Liturgi | [ ] |
| 3 | Home page — Latest News section | [ ] |
| 4 | Active navbar link | [ ] |
| 5 | Sermon Series page | [ ] |
| 6 | Related sermons on sermon detail | [ ] |
| 7 | Warta Jemaat page | [ ] |
| 8 | Photo Gallery | [ ] |
| 9 | Contact / Prayer Request form | [ ] |
| 10 | Google Maps on Visit page | [ ] |
| 11 | YouTube Live Stream on Home page | [ ] |
| 12 | 404 error page | [ ] |
| 13 | Back to top button | [ ] |
| 14 | Meta descriptions for SEO | [ ] |

---

## Feature 1: Pagination on News & Liturgi

**Why:** As content grows, a single page with all articles becomes slow and hard to navigate.

**Files to modify:**
- `website/views.py`
- `website/templates/website/news.html`
- `website/templates/website/liturgi.html`

### Step 1 — Update `views.py`

Replace the `news` and `liturgi_list` views:

```python
from django.core.paginator import Paginator

def news(request):
    news_list = News.objects.filter(is_published=True)
    paginator = Paginator(news_list, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/news.html', {'page': page})


def liturgi_list(request):
    liturgi_list = Liturgi.objects.filter(is_published=True)
    paginator = Paginator(liturgi_list, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/liturgi.html', {'page': page})
```

### Step 2 — Update `news.html`

Change `{% for item in news_list %}` to `{% for item in page %}` and add pagination controls at the bottom:

```html
{% for item in page %}
  ...card...
{% endfor %}

<div class="pagination">
  {% if page.has_previous %}
    <a href="?page={{ page.previous_page_number }}">&laquo; Prev</a>
  {% endif %}
  <span class="current">{{ page.number }} of {{ page.paginator.num_pages }}</span>
  {% if page.has_next %}
    <a href="?page={{ page.next_page_number }}">Next &raquo;</a>
  {% endif %}
</div>
```

### Step 3 — Apply same change to `liturgi.html`

Same pattern as news.html above.

---

## Feature 2: Search on News & Liturgi

**Why:** Makes it easy to find a specific article by title.

**Files to modify:**
- `website/views.py`
- `website/templates/website/news.html`
- `website/templates/website/liturgi.html`

### Step 1 — Update views

```python
def news(request):
    query = request.GET.get('q', '')
    news_list = News.objects.filter(is_published=True)
    if query:
        news_list = news_list.filter(title__icontains=query)
    paginator = Paginator(news_list, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/news.html', {'page': page, 'query': query})
```

### Step 2 — Add search form to `news.html`

Add above the card grid:

```html
<form method="get" class="search-form" style="margin-bottom: 1.5rem;">
  <input type="text" name="q" value="{{ query }}" placeholder="Search news...">
  <button type="submit" class="btn btn--primary">Search</button>
</form>
```

---

## Feature 3: Home Page — Latest News Section

**Why:** Keeps the home page fresh and drives visitors to the news page.

**Files to modify:**
- `website/views.py`
- `website/templates/website/home.html`

### Step 1 — Update `home` view

Add `latest_news` to the context:

```python
def home(request):
    ...
    latest_news = News.objects.filter(is_published=True)[:3]
    return render(request, 'website/home.html', {
        ...
        'latest_news': latest_news,
    })
```

### Step 2 — Add section to `home.html`

Add after the events section:

```html
{% if latest_news %}
<section class="section section--light">
  <div class="container">
    <h2 class="section__title">Latest News</h2>
    <div class="card-grid">
      {% for item in latest_news %}
      <div class="card">
        {% if item.image %}
          <img src="{{ item.image.url }}" alt="{{ item.title }}" class="card__img">
        {% endif %}
        <div class="card__body">
          <h3 class="card__title">{{ item.title }}</h3>
          <p class="card__meta">{{ item.date }}</p>
          <p class="card__text">{{ item.content|striptags|truncatewords:20 }}</p>
          <a href="{% url 'website:news_detail' item.pk %}" class="btn btn--secondary">Read More</a>
        </div>
      </div>
      {% endfor %}
    </div>
    <div class="section__cta">
      <a href="{% url 'website:news' %}" class="btn btn--secondary">View All News</a>
    </div>
  </div>
</section>
{% endif %}
```

---

## Feature 4: Active Navbar Link

**Why:** Shows the user which page they are currently on.

**Files to modify:**
- `templates/base.html`

### Step 1 — Use `request.resolver_match.url_name` to detect current page

```html
<ul class="navbar__links" id="navLinks">
  <li><a href="{% url 'website:sermon_list' %}"
     class="{% if request.resolver_match.url_name == 'sermon_list' %}active{% endif %}">Sermons</a></li>
  <li><a href="{% url 'website:event_list' %}"
     class="{% if request.resolver_match.url_name == 'event_list' %}active{% endif %}">Events</a></li>
  <li><a href="{% url 'website:about' %}"
     class="{% if request.resolver_match.url_name == 'about' %}active{% endif %}">About</a></li>
  <li><a href="{% url 'website:visit' %}"
     class="{% if request.resolver_match.url_name == 'visit' %}active{% endif %}">Visit</a></li>
  <li><a href="{% url 'website:news' %}"
     class="{% if request.resolver_match.url_name == 'news' %}active{% endif %}">News</a></li>
  <li><a href="{% url 'website:liturgi_list' %}"
     class="{% if request.resolver_match.url_name == 'liturgi_list' %}active{% endif %}">Liturgi</a></li>
</ul>
```

### Step 2 — Add active style to `static/css/style.css`

```css
.navbar__links a.active {
  color: var(--color-white);
  border-bottom: 2px solid var(--color-white);
}
```

---

## Feature 5: Sermon Series Page

**Why:** Lets visitors browse sermons by series instead of scrolling through all sermons.

**Files to modify/create:**
- `website/views.py`
- `website/urls.py`
- Create: `website/templates/website/series_list.html`
- Create: `website/templates/website/series_detail.html`

### Step 1 — Add views

```python
def series_list(request):
    series = SermonSeries.objects.all()
    return render(request, 'website/series_list.html', {'series': series})


def series_detail(request, pk):
    series = get_object_or_404(SermonSeries, pk=pk)
    sermons = Sermon.objects.filter(series=series)
    return render(request, 'website/series_detail.html', {
        'series': series,
        'sermons': sermons,
    })
```

### Step 2 — Add URLs

```python
path('series/', views.series_list, name='series_list'),
path('series/<int:pk>/', views.series_detail, name='series_detail'),
```

### Step 3 — Create `series_list.html`

```html
{% extends 'base.html' %}
{% block title %}Sermon Series — GKJ Salatiga{% endblock %}

{% block content %}
<header class="page-header">
  <div class="container">
    <h1 class="page-header__title">Sermon Series</h1>
    <p class="page-header__sub">Browse sermons by series</p>
  </div>
</header>

<section class="section">
  <div class="container">
    <div class="card-grid">
      {% for s in series %}
      <a href="{% url 'website:series_detail' s.pk %}" class="card">
        {% if s.thumbnail %}
          <img src="{{ s.thumbnail.url }}" alt="{{ s.name }}" class="card__img">
        {% endif %}
        <div class="card__body">
          <h3 class="card__title">{{ s.name }}</h3>
          <p class="card__meta">{{ s.sermon_set.count }} sermons</p>
          <p class="card__text">{{ s.description|truncatewords:20 }}</p>
        </div>
      </a>
      {% empty %}
      <p style="color: var(--color-text-muted);">No series yet.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

### Step 4 — Create `series_detail.html`

```html
{% extends 'base.html' %}
{% block title %}{{ series.name }} — GKJ Salatiga{% endblock %}

{% block content %}
<header class="page-header">
  <div class="container">
    <h1 class="page-header__title">{{ series.name }}</h1>
    <p class="page-header__sub">{{ series.description }}</p>
  </div>
</header>

<section class="section">
  <div class="container">
    <div class="card-grid">
      {% for sermon in sermons %}
      <a href="{% url 'website:sermon_detail' sermon.pk %}" class="card">
        {% if sermon.thumbnail %}
          <img src="{{ sermon.thumbnail.url }}" alt="{{ sermon.title }}" class="card__img">
        {% endif %}
        <div class="card__body">
          <h3 class="card__title">{{ sermon.title }}</h3>
          <p class="card__meta">{{ sermon.pastor }} &middot; {{ sermon.date }}</p>
          <p class="card__text">{{ sermon.description|striptags|truncatewords:20 }}</p>
        </div>
      </a>
      {% empty %}
      <p style="color: var(--color-text-muted);">No sermons in this series yet.</p>
      {% endfor %}
    </div>
    <div style="margin-top: 2rem;">
      <a href="{% url 'website:sermon_list' %}" class="btn btn--outline">&larr; All Sermons</a>
    </div>
  </div>
</section>
{% endblock %}
```

---

## Feature 6: Related Sermons on Sermon Detail

**Why:** Keeps visitors engaged by suggesting more content from the same series.

**Files to modify:**
- `website/views.py`
- `website/templates/website/sermon_detail.html`

### Step 1 — Update `sermon_detail` view

```python
def sermon_detail(request, pk):
    sermon = get_object_or_404(Sermon, pk=pk)
    video_id = _extract_youtube_id(sermon.youtube_url)
    related = Sermon.objects.filter(series=sermon.series).exclude(pk=pk)[:3] if sermon.series else []
    return render(request, 'website/sermon_detail.html', {
        'sermon': sermon,
        'video_id': video_id,
        'related': related,
    })
```

### Step 2 — Add related sermons to `sermon_detail.html`

Add before the back button:

```html
{% if related %}
<div style="margin-top: 3rem;">
  <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem;">
    More from this series
  </h3>
  <div class="card-grid">
    {% for s in related %}
    <a href="{% url 'website:sermon_detail' s.pk %}" class="card">
      <div class="card__body">
        <h4 class="card__title">{{ s.title }}</h4>
        <p class="card__meta">{{ s.pastor }} &middot; {{ s.date }}</p>
      </div>
    </a>
    {% endfor %}
  </div>
</div>
{% endif %}
```

---

## Feature 7: Warta Jemaat Page

**Why:** Weekly bulletin keeps the congregation informed between services.

**Files to modify/create:**
- `website/models.py`
- `website/admin.py`
- `website/views.py`
- `website/urls.py`
- Create: `website/templates/website/warta.html`
- Create: `website/templates/website/warta_detail.html`

### Step 1 — Add model to `models.py`

```python
class WartaJemaat(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    content = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='warta/', blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Warta Jemaat'

    def __str__(self):
        return f'Warta {self.date}'
```

### Step 2 — Register in `admin.py`

```python
from django_summernote.admin import SummernoteModelAdmin

@admin.register(WartaJemaat)
class WartaJemaatAdmin(SummernoteModelAdmin):
    list_display = ['title', 'date', 'is_published']
    summernote_fields = ['content']
```

### Step 3 — Add views

```python
def warta_list(request):
    warta_list = WartaJemaat.objects.filter(is_published=True)
    paginator = Paginator(warta_list, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/warta.html', {'page': page})


def warta_detail(request, pk):
    warta = get_object_or_404(WartaJemaat, pk=pk)
    return render(request, 'website/warta_detail.html', {'warta': warta})
```

### Step 4 — Add URLs

```python
path('warta/', views.warta_list, name='warta_list'),
path('warta/<int:pk>/', views.warta_detail, name='warta_detail'),
```

### Step 5 — Run migrations

```powershell
python manage.py makemigrations website
python manage.py migrate
```

---

## Feature 8: Photo Gallery

**Why:** Lets the church share memories from events and activities.

**Files to modify/create:**
- `website/models.py`
- `website/admin.py`
- `website/views.py`
- `website/urls.py`
- Create: `website/templates/website/gallery.html`
- Create: `website/templates/website/album_detail.html`

### Step 1 — Add models

```python
class Album(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    cover_image = models.ImageField(upload_to='gallery/')
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.caption or str(self.album)
```

### Step 2 — Register in `admin.py`

```python
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 3

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'is_published']
    inlines = [PhotoInline]
```

### Step 3 — Add views

```python
def gallery(request):
    albums = Album.objects.filter(is_published=True)
    return render(request, 'website/gallery.html', {'albums': albums})


def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    photos = album.photos.all()
    return render(request, 'website/album_detail.html', {
        'album': album,
        'photos': photos,
    })
```

### Step 4 — Add URLs

```python
path('gallery/', views.gallery, name='gallery'),
path('gallery/<int:pk>/', views.album_detail, name='album_detail'),
```

### Step 5 — Run migrations

```powershell
python manage.py makemigrations website
python manage.py migrate
```

---

## Feature 9: Contact / Prayer Request Form

**Why:** Gives visitors a way to reach the church without needing an email client.

**Files to modify/create:**
- `website/models.py`
- `website/admin.py`
- Create: `website/forms.py`
- `website/views.py`
- `website/urls.py`
- Create: `website/templates/website/contact.html`

### Step 1 — Add model

```python
class ContactMessage(models.Model):
    TYPE_CHOICES = [
        ('contact', 'General Contact'),
        ('prayer', 'Prayer Request'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='contact')
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.name} — {self.message_type}'
```

### Step 2 — Create `website/forms.py`

```python
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message_type', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
```

### Step 3 — Add view

```python
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'website/contact.html', {'form': form, 'sent': True})
    else:
        form = ContactForm()
    return render(request, 'website/contact.html', {'form': form, 'sent': False})
```

### Step 4 — Add URL

```python
path('contact/', views.contact, name='contact'),
```

### Step 5 — Register in `admin.py`

```python
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'message_type', 'submitted_at', 'is_read']
    list_filter = ['message_type', 'is_read']
```

### Step 6 — Run migrations

```powershell
python manage.py makemigrations website
python manage.py migrate
```

---

## Feature 10: Google Maps on Visit Page

**Why:** Helps first-time visitors find the church location easily.

**Files to modify:**
- `website/templates/website/visit.html`

### Step 1 — Get the embed code

1. Go to [maps.google.com](https://maps.google.com)
2. Search for your church address
3. Click **Share** → **Embed a map**
4. Copy the `<iframe>` code

### Step 2 — Add to `visit.html`

Add after the service-grid section:

```html
<section class="section section--light">
  <div class="container">
    <h2 class="section__title">Find Us</h2>
    <div style="border-radius: var(--radius-md); overflow: hidden; box-shadow: var(--shadow-md);">
      <iframe
        src="YOUR_GOOGLE_MAPS_EMBED_URL"
        width="100%" height="450"
        style="border:0;" allowfullscreen loading="lazy">
      </iframe>
    </div>
  </div>
</section>
```

---

## Feature 11: YouTube Live Stream on Home Page

**Why:** Visitors can watch the Sunday service directly from the church website.

**Files to modify:**
- `website/models.py` (add fields to `ServiceTime`)
- `website/templates/website/home.html`

### Step 1 — Add fields to `ServiceTime`

```python
class ServiceTime(models.Model):
    ...
    youtube_live_url = models.URLField(blank=True)
    is_live_now = models.BooleanField(default=False)
```

### Step 2 — Run migration

```powershell
python manage.py makemigrations website
python manage.py migrate
```

### Step 3 — Add to `home.html`

Add before the hero section or at the top of content:

```html
{% for service in service_times %}
{% if service.is_live_now and service.youtube_live_url %}
<section class="section section--dark">
  <div class="container">
    <h2 class="section__title" style="color: white;">
      🔴 Live Now — Sunday Service
    </h2>
    <div class="video-embed">
      <iframe src="{{ service.youtube_live_url }}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media"
        allowfullscreen>
      </iframe>
    </div>
  </div>
</section>
{% endif %}
{% endfor %}
```

**To go live:** In Django Admin, open the ServiceTime record, paste the YouTube live URL, and check `is_live_now`. Uncheck it after the service ends.

---

## Feature 12: 404 Error Page

**Why:** A branded error page looks more professional than Django's default yellow debug page.

**Files to create:**
- `templates/404.html`

### Step 1 — Create `templates/404.html`

```html
{% extends 'base.html' %}
{% block title %}Page Not Found — GKJ Salatiga{% endblock %}

{% block content %}
<div style="text-align: center; padding: 8rem 1rem;">
  <h1 style="font-size: 6rem; font-weight: 800; color: var(--color-primary); line-height: 1;">
    404
  </h1>
  <p style="font-size: 1.25rem; margin-bottom: 0.5rem; font-weight: 600;">
    Page not found
  </p>
  <p style="color: var(--color-text-muted); margin-bottom: 2rem;">
    The page you're looking for doesn't exist or has been moved.
  </p>
  <a href="/" class="btn btn--primary">Go to Home</a>
</div>
{% endblock %}
```

### Step 2 — Test it

Temporarily set in `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['*']
```

Visit any invalid URL like `http://127.0.0.1:8000/doesnotexist/` — you should see your custom 404 page.

Set `DEBUG = True` again after testing.

---

## Feature 13: Back to Top Button

**Why:** On long pages (news, sermons), lets users scroll back to the top quickly.

**Files to modify:**
- `templates/base.html`
- `static/css/style.css`
- `static/js/main.js`

### Step 1 — Add button to `base.html`

Add just before `</body>`:

```html
<button id="backToTop" class="back-to-top" aria-label="Back to top">&#8679;</button>
```

### Step 2 — Add CSS to `style.css`

```css
.back-to-top {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  font-size: 1.4rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--transition);
  z-index: 999;
}

.back-to-top.visible { opacity: 1; }
```

### Step 3 — Add JS to `main.js`

```javascript
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => {
  if (window.scrollY > 300) {
    backToTop.classList.add('visible');
  } else {
    backToTop.classList.remove('visible');
  }
});
backToTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
```

---

## Feature 14: Meta Descriptions for SEO

**Why:** Helps search engines understand each page, improving search rankings.

**Files to modify:**
- `templates/base.html`
- All page templates

### Step 1 — Add meta block to `base.html`

In the `<head>` section, add:

```html
<meta name="description" content="{% block meta_description %}GKJ Salatiga — Gereja Kristen Jawa Salatiga{% endblock %}">
```

### Step 2 — Add to each page template

For example in `sermons.html`:

```html
{% block meta_description %}Watch and listen to sermons from GKJ Salatiga{% endblock %}
```

In `news_detail.html`:

```html
{% block meta_description %}{{ news.content|striptags|truncatewords:25 }}{% endblock %}
```

---

## Commit After Each Feature

```powershell
git add .
git commit -m "feat: add [feature name]"
```
