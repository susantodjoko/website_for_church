# Sermon Image Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sermons without a YouTube link show their thumbnail image on the detail page instead of an empty/broken video embed.

**Architecture:** Make `Sermon.youtube_url` optional at the model level. The existing view logic already turns a missing URL into a falsy `video_id`; the template just needs a new `{% elif %}` branch that renders the thumbnail when there's no video, and new CSS to size that image sensibly.

**Tech Stack:** Django 6.0.5, Django test runner (`manage.py test`), no new dependencies.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-28-sermon-image-fallback-design.md`
- Sermon list page ([sermons.html](../../../website/templates/website/sermons.html)) is out of scope — do not touch it.
- No placeholder graphic for sermons with neither video nor thumbnail — the media block is simply omitted in that case.
- Run tests with: `./venv/Scripts/python.exe manage.py test website`

---

### Task 1: Make `youtube_url` optional on the `Sermon` model

**Files:**
- Modify: `website/models.py:51`
- Create: `website/migrations/0017_alter_sermon_youtube_url.py` (auto-named by `makemigrations`)
- Test: `website/tests.py`

**Interfaces:**
- Produces: `Sermon.youtube_url` becomes an optional field (`blank=True`). No signature changes — `Sermon.objects.create(...)` calls elsewhere in the codebase are unaffected since none of them relied on `youtube_url` being required at the ORM level (only `full_clean()`/forms enforce `blank=False`).

- [ ] **Step 1: Write the failing test**

Add to `website/tests.py`, after the existing `SermonSlugTest` class:

```python
class SermonYoutubeOptionalTest(TestCase):
    def test_youtube_url_can_be_blank(self):
        sermon = Sermon(
            title='No Video Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='', thumbnail='sermons/test.jpg'
        )
        sermon.full_clean()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/Scripts/python.exe manage.py test website.SermonYoutubeOptionalTest -v 2`
Expected: FAIL with `ValidationError: {'youtube_url': ['This field cannot be blank.']}`

- [ ] **Step 3: Update the model field**

In `website/models.py`, change line 51 from:

```python
    youtube_url = models.URLField()
```

to:

```python
    youtube_url = models.URLField(blank=True)
```

- [ ] **Step 4: Generate and apply the migration**

Run: `./venv/Scripts/python.exe manage.py makemigrations website`
Expected: creates `website/migrations/0017_alter_sermon_youtube_url.py` (Django names it automatically) altering the `youtube_url` field. No data migration needed — existing rows already have a URL value.

Run: `./venv/Scripts/python.exe manage.py migrate website`
Expected: `Applying website.0017_...  OK`

- [ ] **Step 5: Run test to verify it passes**

Run: `./venv/Scripts/python.exe manage.py test website.SermonYoutubeOptionalTest -v 2`
Expected: PASS

- [ ] **Step 6: Run the full website test suite to check for regressions**

Run: `./venv/Scripts/python.exe manage.py test website`
Expected: all tests PASS (existing sermon tests all pass a real `youtube_url`, so this change is additive and shouldn't break anything)

- [ ] **Step 7: Commit**

```bash
git add website/models.py website/migrations/ website/tests.py
git commit -m "feat: make sermon youtube_url optional"
```

---

### Task 2: Show thumbnail on the detail page when there's no video

**Files:**
- Modify: `website/templates/website/sermon_detail.html:12-41`
- Test: `website/tests.py`

**Interfaces:**
- Consumes: `video_id` (str, from `website/views.py:63`, already falsy when `youtube_url` is blank — no view change needed), `sermon.thumbnail` (Django `ImageField`, truthy when a file is set regardless of whether the file exists on disk, per Django's `FieldFile.__bool__`).
- Produces: new CSS hook class `sermon-detail__img` on the fallback `<img>`, consumed by Task 3.

- [ ] **Step 1: Write the failing tests**

Add to `website/tests.py`, after `SermonYoutubeOptionalTest`:

```python
class SermonDetailImageFallbackTest(TestCase):
    def test_shows_thumbnail_when_no_youtube_url(self):
        sermon = Sermon.objects.create(
            title='Photo Only Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='', thumbnail='sermons/test.jpg'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertContains(response, 'sermon-detail__img')
        self.assertNotContains(response, 'yt-iframe')

    def test_shows_video_when_youtube_url_present(self):
        sermon = Sermon.objects.create(
            title='Video Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc',
            thumbnail='sermons/test.jpg'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertContains(response, 'yt-iframe')
        self.assertNotContains(response, 'sermon-detail__img')

    def test_shows_neither_when_no_video_and_no_thumbnail(self):
        sermon = Sermon.objects.create(
            title='Text Only Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url=''
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertNotContains(response, 'yt-iframe')
        self.assertNotContains(response, 'sermon-detail__img')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `./venv/Scripts/python.exe manage.py test website.SermonDetailImageFallbackTest -v 2`
Expected: `test_shows_thumbnail_when_no_youtube_url` and `test_shows_video_when_youtube_url_present` FAIL (no `sermon-detail__img` class exists yet — the template has no fallback branch); `test_shows_neither_when_no_video_and_no_thumbnail` PASSes already (nothing to show is already the current behavior for a blank `youtube_url`, though this only became possible after Task 1).

- [ ] **Step 3: Add the fallback branch to the template**

In `website/templates/website/sermon_detail.html`, change:

```django
    {% if video_id %}
    <div class="video-embed" id="video-wrap">
      <iframe
        id="yt-iframe"
        src="https://www.youtube.com/embed/{{ video_id }}?enablejsapi=1"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
      </iframe>
      <!-- Fallback shown if YouTube blocks embedding -->
      <div id="yt-fallback" style="display:none; position:absolute; inset:0; background:#111; display:none; align-items:center; justify-content:center; flex-direction:column; gap:1rem; border-radius:8px;">
        <p style="color:#fff; font-size:1rem; text-align:center; padding:0 1rem;">Video tidak dapat diputar di sini karena setelan YouTube.<br>Tonton langsung di YouTube:</p>
        <a href="{{ sermon.youtube_url }}" target="_blank" rel="noopener"
           style="background:#ff0000; color:#fff; font-weight:700; padding:0.65rem 1.5rem; border-radius:8px; text-decoration:none; font-size:0.95rem;">
          ▶ Tonton di YouTube
        </a>
      </div>
    </div>
    <script>
      // Show fallback if YouTube throws error 150/153 (embedding disabled)
      document.getElementById('yt-iframe').addEventListener('load', function() {
        window.onYTError = function(event) {
          if (event.data === 150 || event.data === 153) {
            document.getElementById('yt-iframe').style.display = 'none';
            var fb = document.getElementById('yt-fallback');
            fb.style.display = 'flex';
          }
        };
      });
    </script>
    {% endif %}
```

to:

```django
    {% if video_id %}
    <div class="video-embed" id="video-wrap">
      <iframe
        id="yt-iframe"
        src="https://www.youtube.com/embed/{{ video_id }}?enablejsapi=1"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
      </iframe>
      <!-- Fallback shown if YouTube blocks embedding -->
      <div id="yt-fallback" style="display:none; position:absolute; inset:0; background:#111; display:none; align-items:center; justify-content:center; flex-direction:column; gap:1rem; border-radius:8px;">
        <p style="color:#fff; font-size:1rem; text-align:center; padding:0 1rem;">Video tidak dapat diputar di sini karena setelan YouTube.<br>Tonton langsung di YouTube:</p>
        <a href="{{ sermon.youtube_url }}" target="_blank" rel="noopener"
           style="background:#ff0000; color:#fff; font-weight:700; padding:0.65rem 1.5rem; border-radius:8px; text-decoration:none; font-size:0.95rem;">
          ▶ Tonton di YouTube
        </a>
      </div>
    </div>
    <script>
      // Show fallback if YouTube throws error 150/153 (embedding disabled)
      document.getElementById('yt-iframe').addEventListener('load', function() {
        window.onYTError = function(event) {
          if (event.data === 150 || event.data === 153) {
            document.getElementById('yt-iframe').style.display = 'none';
            var fb = document.getElementById('yt-fallback');
            fb.style.display = 'flex';
          }
        };
      });
    </script>
    {% elif sermon.thumbnail %}
    <img src="{{ sermon.thumbnail.url }}" alt="{{ sermon.title }}" class="sermon-detail__img">
    {% endif %}
```

(Only the closing `{% endif %}` changes to `{% elif sermon.thumbnail %} ... {% endif %}` with the new `<img>` line — everything inside the existing `{% if video_id %}` branch is unchanged.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `./venv/Scripts/python.exe manage.py test website.SermonDetailImageFallbackTest -v 2`
Expected: all 3 tests PASS

- [ ] **Step 5: Run the full website test suite to check for regressions**

Run: `./venv/Scripts/python.exe manage.py test website`
Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add website/templates/website/sermon_detail.html website/tests.py
git commit -m "feat: show sermon thumbnail when no youtube video is set"
```

---

### Task 3: Style the fallback image

**Files:**
- Modify: `static/css/style.css`

**Interfaces:**
- Consumes: `.sermon-detail__img` class name from Task 2's template change.

- [ ] **Step 1: Add the CSS rule**

Add to `static/css/style.css`, near the other `.sermon-detail` rules (search for `.sermon-detail__meta` and add after it):

```css
.sermon-detail__img {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
}
```

- [ ] **Step 2: Manually verify in the browser**

Run the dev server (`./venv/Scripts/python.exe manage.py runserver`), open a sermon detail page for a sermon with a thumbnail and no YouTube URL (use Django admin to create one, or the Django shell), and confirm the image renders full-width, capped at 420px tall, with rounded corners, above the title.

- [ ] **Step 3: Commit**

```bash
git add static/css/style.css
git commit -m "style: size sermon thumbnail fallback image"
```
