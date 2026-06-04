# UI Improvements — Option 1: Targeted Polish

**Date:** 2026-06-04
**Scope:** Additive changes only — no layout restructuring, no new models
**Audience:** Both first-time visitors and regular congregation members
**Files affected:** 6 templates, 1 view, 1 settings file, 1 new context processor, 1 CSS file

---

## 1. Sermon Detail Enhancements

**File:** `website/templates/website/sermon_detail.html`
**File:** `website/views.py` (`sermon_detail` function)

### A) Share Buttons

Add below `rich-content` div, above the "Back to Sermons" link:

```html
<div class="share-row">
  <a href="https://wa.me/?text={{ sermon.title|urlencode }}%20{{ request.build_absolute_uri }}"
     target="_blank" rel="noopener" class="btn btn--outline">Bagikan via WhatsApp</a>
  <button onclick="navigator.clipboard.writeText(window.location.href)"
          class="btn btn--outline">Salin Tautan</button>
</div>
```

### B) Related Sermons Row

Add below share buttons, before the "Back" link. Shows up to 3 related sermons — same series first, fall back to same topic, always excludes the current sermon.

**View change** in `website/views.py`:
```python
def sermon_detail(request, slug):
    sermon = get_object_or_404(Sermon, slug=slug)
    video_id = _extract_youtube_id(sermon.youtube_url)
    related = Sermon.objects.exclude(pk=sermon.pk)
    if sermon.series:
        related = related.filter(series=sermon.series)
    elif sermon.topic:
        related = related.filter(topic=sermon.topic)
    related = related[:3]
    return render(request, 'website/sermon_detail.html', {
        'sermon': sermon,
        'video_id': video_id,
        'related': related,
    })
```

**Template addition:**
```html
{% if related %}
<div style="margin-top: 3rem; border-top: 1px solid var(--color-border); padding-top: 2rem;">
  <h2 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem;">Khotbah Terkait</h2>
  <div class="card-grid" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));">
    {% for s in related %}
    <a href="{% url 'website:sermon_detail' s.slug %}" class="card">
      {% if s.thumbnail %}
        <img src="{{ s.thumbnail.url }}" alt="{{ s.title }}" class="card__img">
      {% endif %}
      <div class="card__body">
        <p class="card__tag">{{ s.pastor }}</p>
        <h3 class="card__title">{{ s.title }}</h3>
        <p class="card__meta">{{ s.date }}</p>
      </div>
    </a>
    {% endfor %}
  </div>
</div>
{% endif %}
```

---

## 2. Empty States with CTAs

**CSS:** `static/css/style.css` — add:
```css
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-muted);
}
.empty-state p { margin-bottom: 1rem; }
```

### Events (`website/templates/website/events.html`)

Replace line 32:
```html
{% empty %}
<div class="empty-state">
  <p>Belum ada kegiatan yang akan datang.</p>
  <a href="{% url 'website:contact' %}" class="btn btn--outline">Hubungi Kami</a>
</div>
```

### Sermons (`website/templates/website/sermons.html`)

Replace existing `{% empty %}` block:
```html
{% empty %}
<div class="empty-state">
  <p>Belum ada khotbah untuk topik ini.</p>
  <a href="{% url 'website:sermon_list' %}" class="btn btn--outline">Lihat Semua Khotbah</a>
</div>
```

### Gallery (`website/templates/website/gallery.html`)

Replace existing `{% empty %}` block:
```html
{% empty %}
<div class="empty-state">
  <p>Belum ada foto yang tersedia.</p>
</div>
```

---

## 3. Footer Contact Column

**New file:** `website/context_processors.py`
```python
from .models import ServiceTime

def service_times(request):
    return {'footer_service_times': ServiceTime.objects.all()[:2]}
```

**`church_site/settings.py`** — add to `TEMPLATES[0]['OPTIONS']['context_processors']`:
```python
'website.context_processors.service_times',
```

**`templates/base.html`** — add third column inside `footer__inner` div, after `footer__links`:
```html
<div class="footer__contact">
  {% for st in footer_service_times %}
    <p><strong>{{ st.campus_name }}</strong></p>
    <p style="color: var(--color-text-muted); font-size: 0.875rem;">{{ st.address }}</p>
    <p style="color: var(--color-text-muted); font-size: 0.875rem; margin-bottom: 1rem;">{{ st.times }}</p>
  {% endfor %}
  <a href="{% url 'website:contact' %}" class="btn btn--outline" style="font-size: 0.875rem;">Hubungi Kami →</a>
</div>
```

**`static/css/style.css`** — change the existing `.footer__inner` rule (currently `1fr 1fr`) to support three columns. The mobile override at line 610 (`grid-template-columns: 1fr`) already exists and needs no change.
```css
/* Change existing rule from: grid-template-columns: 1fr 1fr */
.footer__inner {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 2rem;
}
```

---

## 4. About Page — Contact CTA

**File:** `website/templates/website/about.html`

Add after the `{% if about.values.exists %}` block, before closing `</section>`:

```html
<div class="about-contact" style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--color-border);">
  <h2 class="section__title">Kunjungi Kami</h2>
  <p style="color: var(--color-text-muted); margin-bottom: 1.5rem;">
    Kami terbuka untuk Anda. Jangan ragu untuk menghubungi atau datang langsung.
  </p>
  <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
    <a href="{% url 'website:contact' %}" class="btn btn--primary">Kirim Pesan</a>
    <a href="{% url 'website:visit' %}" class="btn btn--outline">Jam &amp; Lokasi</a>
  </div>
</div>
```

---

## 5. Events — Google Maps Link

**File:** `website/templates/website/events.html` line 23

Change location display to a clickable Maps link:

```html
<!-- Before -->
{{ event.date }} &middot; {{ event.time|time:"H:i" }} &middot; {{ event.location }}

<!-- After -->
{{ event.date }} &middot; {{ event.time|time:"H:i" }} &middot;
<a href="https://maps.google.com/?q={{ event.location|urlencode }}"
   target="_blank" rel="noopener">{{ event.location }}</a>
```

---

## Files Changed Summary

| File | Change |
|---|---|
| `website/templates/website/sermon_detail.html` | Share buttons + related sermons row |
| `website/views.py` | Pass `related` queryset in `sermon_detail` |
| `website/templates/website/events.html` | Empty state CTA + Maps link on location |
| `website/templates/website/sermons.html` | Empty state with "Lihat Semua" CTA |
| `website/templates/website/gallery.html` | Empty state message |
| `website/templates/website/about.html` | Contact CTA block |
| `templates/base.html` | Footer third column |
| `website/context_processors.py` | New file — injects `footer_service_times` |
| `church_site/settings.py` | Register context processor |
| `static/css/style.css` | `.empty-state` class + footer grid update |

## Testing Checklist

- [ ] Sermon detail — share buttons appear; WhatsApp link opens correctly; copy button works in browser
- [ ] Sermon detail — related sermons show when series or topic matches; section hidden when no matches
- [ ] Events page — empty state shows with Hubungi Kami button when no events
- [ ] Sermons page — empty state shows with link when topic filter returns nothing
- [ ] Gallery page — empty state shows when no albums
- [ ] Footer — contact column appears on all pages with campus name, address, hours
- [ ] Footer — responsive: single column on mobile
- [ ] About page — "Kunjungi Kami" section visible at bottom; both buttons link correctly
- [ ] Events — location text is a clickable Maps link
