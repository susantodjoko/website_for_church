# Sermon Detail: Image Fallback When No YouTube Link

## Problem

Not every sermon has a YouTube video. Today, `Sermon.youtube_url` (`website/models.py:51`) is a required field, and the detail page ([sermon_detail.html:12](../../../website/templates/website/sermon_detail.html#L12)) always tries to embed a YouTube player. Staff need a way to publish a sermon with just a photo, no video.

## Approach

Infer what to display from the data that's already there — no new admin field to remember to fill in.

- If the sermon has a usable YouTube URL → show the video player (existing behavior, unchanged).
- Else if the sermon has a `thumbnail` → show that image, large, in place of the video block.
- Else (neither) → skip the media block entirely; the page just starts at the title. No placeholder graphic, since none exists to show.

## Changes

**1. Model** (`website/models.py:51`)
```python
youtube_url = models.URLField(blank=True)
```
Migration: alter field, no data changes needed (existing rows already have a URL).

**2. View** (`website/views.py:63`, `_extract_youtube_id` at `views.py:93`)
No change needed — `_extract_youtube_id('')` already returns `''`, which is falsy, so `video_id` is already `None`/`''` for sermons without a link.

**3. Template** (`website/templates/website/sermon_detail.html:12-41`)
```django
{% if video_id %}
  <div class="video-embed" id="video-wrap">
    ... existing iframe + fallback script, unchanged ...
  </div>
{% elif sermon.thumbnail %}
  <img src="{{ sermon.thumbnail.url }}" alt="{{ sermon.title }}" class="sermon-detail__img">
{% endif %}
```
New CSS class `.sermon-detail__img` added to `static/css/style.css` — full-width, rounded corners consistent with `.card__img`, capped max-height so a tall photo doesn't dominate the page.

**4. Admin** (`website/admin.py`)
No change required — `blank=True` alone makes the field optional in the admin form.

## Out of scope

- Sermon list page ([sermons.html](../../../website/templates/website/sermons.html)) — already shows the thumbnail as a static card image regardless of video presence; unaffected.
- No placeholder graphic for sermons with neither video nor thumbnail — can be added later if it comes up.
