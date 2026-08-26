# UI Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the GKJ Salatiga public website with a warm earth-tone palette, Lora serif headlines, and softer corner radii — CSS/visual layer only.

**Architecture:** All changes are confined to two files: `static/css/style.css` (design tokens, component rules) and `templates/base.html` (Google Fonts `<link>`). No HTML structure, JavaScript, Django views, or staff/members portal styles are touched. Each task is a coherent, independently reviewable CSS change with a verification step and its own commit.

**Tech Stack:** Plain CSS custom properties, Google Fonts CDN (Inter + Lora), Django templates (HTML edit only for the font link)

## Global Constraints

- HTML structure of all templates must remain unchanged
- Staff/members portal classes (`.members-layout`, `.data-table`, `.badge--*`, `.stat-card`, `.detail-grid`, `.tab-bar`) must not be modified
- Admin templates untouched
- JavaScript untouched
- Only `static/css/style.css` and `templates/base.html` may change

---

### Task 1: Font system — Lora import + token + headline selectors

**Files:**
- Modify: `templates/base.html` (line 15 — Google Fonts `<link>`)
- Modify: `static/css/style.css` (`:root` block, + 7 selector rules)

**Interfaces:**
- Produces: `--font-serif` CSS custom property; all headline selectors use it

- [ ] **Step 1: Update Google Fonts link in `templates/base.html`**

Find line 15:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```
Replace with:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Lora:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Add `--font-serif` token to `:root` in `static/css/style.css`**

In the `:root` block (after the existing `--font-sans` line, currently line 15), add:
```css
--font-serif: 'Lora', Georgia, serif;
```

- [ ] **Step 3: Apply serif font to `.hero__headline`**

Find the existing rule (currently around line 217):
```css
.hero__headline {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: var(--space-md);
}
```
Add `font-family: var(--font-serif);` inside it:
```css
.hero__headline {
  font-family: var(--font-serif);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: var(--space-md);
}
```

- [ ] **Step 4: Apply serif font to `.section__title`**

Find (currently around line 68):
```css
.section__title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--space-lg);
  text-align: center;
}
```
Add `font-family: var(--font-serif);`:
```css
.section__title {
  font-family: var(--font-serif);
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--space-lg);
  text-align: center;
}
```

- [ ] **Step 5: Apply serif font to `.page-header__title`**

Find (currently around line 335):
```css
.page-header__title { font-size: 2.5rem; font-weight: 800; }
```
Replace with:
```css
.page-header__title { font-family: var(--font-serif); font-size: 2.5rem; font-weight: 800; }
```

- [ ] **Step 6: Apply serif font to `.card__title`**

Find (currently around line 291):
```css
.card__title { font-size: 1.15rem; font-weight: 700; margin-bottom: var(--space-xs); line-height: 1.3; }
```
Replace with:
```css
.card__title { font-family: var(--font-serif); font-size: 1.15rem; font-weight: 700; margin-bottom: var(--space-xs); line-height: 1.3; }
```

- [ ] **Step 7: Apply serif font to `.footer__name`**

Find (currently around line 453):
```css
.footer__name { font-size: 1.4rem; font-weight: 800; margin-bottom: var(--space-xs); }
```
Replace with:
```css
.footer__name { font-family: var(--font-serif); font-size: 1.4rem; font-weight: 800; margin-bottom: var(--space-xs); }
```

- [ ] **Step 8: Apply serif font to `.service-card__name`**

Find (currently around line 321):
```css
.service-card__name { font-size: 1.3rem; font-weight: 700; margin-bottom: var(--space-xs); }
```
Replace with:
```css
.service-card__name { font-family: var(--font-serif); font-size: 1.3rem; font-weight: 700; margin-bottom: var(--space-xs); }
```

- [ ] **Step 9: Apply serif font to `.value-card__title`**

Find (currently around line 401):
```css
.value-card__title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
  color: var(--color-primary);
}
```
Add `font-family: var(--font-serif);`:
```css
.value-card__title {
  font-family: var(--font-serif);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
  color: var(--color-primary);
}
```

- [ ] **Step 10: Verify in browser**

Start the dev server (`python manage.py runserver`) and open `http://localhost:8000/`.

Check:
- Open DevTools → Network → filter by "lora" — confirm Lora font file loads (status 200)
- The home page hero headline renders in a serif font (Lora)
- Section headings ("Khotbah Terbaru", etc.) are in Lora
- Nav links, buttons, body paragraphs, card meta lines remain in Inter (sans-serif)
- Open `/khotbah/` — card titles are in Lora, meta lines are in Inter
- Open `/tentang/` — value card titles are in Lora

- [ ] **Step 11: Commit**

```bash
git add static/css/style.css templates/base.html
git commit -m "feat: add Lora serif font to headlines"
```

---

### Task 2: Color palette — warm earth tokens

**Files:**
- Modify: `static/css/style.css` (`:root` block only — 9 token values + 1 new token)

**Interfaces:**
- Consumes: existing token names (unchanged — only values swap)
- Produces: warm terracotta/linen/sage palette throughout; `--color-accent` available for use

- [ ] **Step 1: Replace color tokens in `:root`**

In `static/css/style.css`, find the `:root` block (lines 4–34). Replace all color custom property values as follows:

```css
:root {
  --color-primary:      #B8704A;
  --color-primary-dark: #9A5A38;
  --color-accent:       #7A8C6A;
  --color-dark:         #2D2419;
  --color-dark-2:       #3D3328;
  --color-light:        #F0E8DC;
  --color-white:        #FFFDF9;
  --color-text:         #2D2419;
  --color-text-muted:   #7D6B5A;
  --color-border:       #DDD3C5;

  /* everything below this line unchanged */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif: 'Lora', Georgia, serif;
  ...
}
```

The exact full replacement for the color block (lines 5–13):

Old:
```css
  --color-primary:      #1B4F8A;
  --color-primary-dark: #153D6B;
  --color-dark:         #1A1A1A;
  --color-dark-2:       #2C2C2C;
  --color-light:        #F7F7F5;
  --color-white:        #FFFFFF;
  --color-text:         #1A1A1A;
  --color-text-muted:   #6B6B6B;
  --color-border:       #E5E5E3;
```

New (insert `--color-accent` after `--color-primary-dark`):
```css
  --color-primary:      #B8704A;
  --color-primary-dark: #9A5A38;
  --color-accent:       #7A8C6A;
  --color-dark:         #2D2419;
  --color-dark-2:       #3D3328;
  --color-light:        #F0E8DC;
  --color-white:        #FFFDF9;
  --color-text:         #2D2419;
  --color-text-muted:   #7D6B5A;
  --color-border:       #DDD3C5;
```

- [ ] **Step 2: Verify in browser**

Reload `http://localhost:8000/`. Check:

- Page background is a very warm near-white (`#FFFDF9`) — not stark white
- Primary buttons (e.g. "Rencanakan Kunjungan Anda") are terracotta, not navy
- Navbar scrolled state (scroll down past hero) shows warm dark brown, not cold black
- Footer background is warm dark brown
- Dark sections ("Pelayanan Kami") use warm dark brown background
- Section alternate background (e.g. "Kegiatan Mendatang") is sandy/linen, not cold grey
- Open `/tentang/` → value card left-border is terracotta
- Open `/kunjungi/` or any inner page → `page-header` dark band is warm brown

- [ ] **Step 3: Commit**

```bash
git add static/css/style.css
git commit -m "feat: apply warm earth color palette"
```

---

### Task 3: Radius, online card accent, rich-content bug fix

**Files:**
- Modify: `static/css/style.css` (`:root` radius tokens, `.service-card--online`, 3 `.rich-content` selectors)

**Interfaces:**
- Consumes: `--color-accent` from Task 2
- Produces: softer corners everywhere; sage online-card accent; working rich-content table styles

- [ ] **Step 1: Update radius tokens in `:root`**

Find in the `:root` block (currently around lines 26–28):
```css
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
```
Replace with:
```css
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
```

- [ ] **Step 2: Fix `.service-card--online` accent color**

Find (currently around line 319):
```css
.service-card--online { border-top-color: #27ae60; }
```
Replace with:
```css
.service-card--online { border-top-color: var(--color-accent); }
```

- [ ] **Step 3: Fix rich-content table bug — `th` background**

Find (currently around line 634):
```css
.rich-content table th {
  background: var(--color-surface);
  font-weight: 600;
  color: var(--color-heading);
}
```
Replace with:
```css
.rich-content table th {
  background: var(--color-light);
  font-weight: 600;
  color: var(--color-text);
}
```

- [ ] **Step 4: Fix rich-content table bug — even-row background**

Find (currently around line 640):
```css
.rich-content table tr:nth-child(even) td {
  background: color-mix(in srgb, var(--color-surface) 50%, transparent);
}
```
Replace with:
```css
.rich-content table tr:nth-child(even) td {
  background: color-mix(in srgb, var(--color-light) 50%, transparent);
}
```

- [ ] **Step 5: Verify in browser**

Reload `http://localhost:8000/`. Check:

- Cards have visibly rounder corners (compare to before — was `8px`, now `12px`)
- Buttons are slightly more pill-like (`6px` instead of `4px`)
- Filter buttons on `/khotbah/` look softer
- Open `/kunjungi/` — if an online service entry exists, its top border should be sage green, not bright green
- If a Warta or Liturgi detail page has a table in its rich-text content, open it and confirm the `th` cells have a linen background and dark-brown text (not a broken/missing style)
- Open the staff member list page — corners slightly rounder on the search input, but no other change to staff styles (colors, badges, tables must look the same as before)

- [ ] **Step 6: Commit**

```bash
git add static/css/style.css
git commit -m "feat: soften radius, sage online card, fix rich-content tokens"
```
