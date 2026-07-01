# UI Refresh — GKJ Salatiga Public Website

**Date:** 2026-07-01  
**Scope:** CSS/visual layer only — `static/css/style.css` + `templates/base.html` font import  
**Surface:** Public church website only (staff/members portal untouched)  
**Approach:** Option B — Design token swap + warm component polish

---

## Goals

Shift the public site from a clean-but-generic corporate feel to a soft, warm, welcoming aesthetic that reflects a community of faith. No HTML structure changes; only CSS and the Google Fonts import line are modified.

---

## 1. Color Palette

Replace all tokens in `:root`:

| Token | Old value | New value | Notes |
|---|---|---|---|
| `--color-primary` | `#1B4F8A` | `#B8704A` | Terracotta — buttons, links, accents |
| `--color-primary-dark` | `#153D6B` | `#9A5A38` | Hover/pressed state |
| `--color-dark` | `#1A1A1A` | `#2D2419` | Navbar (scrolled), dark sections, footer |
| `--color-dark-2` | `#2C2C2C` | `#3D3328` | Ministry card dark surface |
| `--color-light` | `#F7F7F5` | `#F0E8DC` | Sandy/linen alternate section bg |
| `--color-white` | `#FFFFFF` | `#FFFDF9` | Warm white page background |
| `--color-text` | `#1A1A1A` | `#2D2419` | Body text — warm dark brown |
| `--color-text-muted` | `#6B6B6B` | `#7D6B5A` | Labels, meta — warm mid-tone |
| `--color-border` | `#E5E5E3` | `#DDD3C5` | Warm border/divider |

Add one new token:

```css
--color-accent: #7A8C6A;   /* sage green */
```

---

## 2. Typography

Add `--font-serif` token using Lora from Google Fonts. Inter remains for all body/UI text.

### Google Fonts import (in `templates/base.html`)

Replace:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```
With:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Lora:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
```

### New token in `:root`

```css
--font-serif: 'Lora', Georgia, serif;
```

### Selectors that get `font-family: var(--font-serif)`

| Selector | Page context |
|---|---|
| `.hero__headline` | Home hero title |
| `.section__title` | All section headings |
| `.page-header__title` | Inner page banners |
| `.card__title` | Sermon / event / warta cards |
| `.footer__name` | Footer brand name |
| `.service-card__name` | Campus names in service grid |
| `.value-card__title` | About page value cards |

Everything else (nav, buttons, meta, tables, labels, body) keeps `--font-sans` (Inter).

---

## 3. Component Tweaks

### Border radius — soften corners

| Token | Old | New |
|---|---|---|
| `--radius-sm` | `4px` | `6px` |
| `--radius-md` | `8px` | `12px` |
| `--radius-lg` | `16px` | `20px` |

Affects: cards, buttons, service cards, search input, filter buttons, pagination, badges, back-to-top button.

### Navbar

No explicit changes needed. The scrolled-state background uses `var(--color-dark)`, which now resolves to warm `#2D2419` automatically.

### Hero default gradient

No explicit changes needed. `.hero__bg--default` uses `var(--color-primary)` and `var(--color-dark)`, both of which update via token swap to terracotta → warm brown.

### Online service card accent

Change hard-coded `#27ae60` on `.service-card--online` to `var(--color-accent)` (sage `#7A8C6A`).

### Bug fix — rich content table

`.rich-content table th` currently references `var(--color-surface)` and `var(--color-heading)`, which are undefined tokens. Fix:
- `var(--color-surface)` → `var(--color-light)`
- `var(--color-heading)` → `var(--color-text)`

Also fix `.rich-content table tr:nth-child(even) td` which uses `var(--color-surface)`.

---

## 4. Out of Scope

- All HTML templates — no changes
- Staff/members portal styles (`.members-layout`, `.data-table`, `.badge--*`, `.stat-card`, `.detail-grid`, `.tab-bar`, etc.) — untouched
- Admin templates — untouched
- JavaScript — untouched
- Django views, models, URLs — untouched

---

## 5. Files Changed

| File | Change |
|---|---|
| `static/css/style.css` | Token values, font-family additions, radius values, `service-card--online` color, rich-content bug fix |
| `templates/base.html` | Google Fonts `<link>` updated to include Lora |
