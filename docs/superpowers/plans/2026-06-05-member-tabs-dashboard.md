# Member Detail Tabs + Dashboard Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganise the member detail page into 4 selectable tabs (Data Pribadi, Iman, Pelayanan, Riwayat) and add age distribution + birthday widget to the staff dashboard.

**Architecture:** Tab switching is pure vanilla JS (~15 lines) with no framework. Dashboard additions are two new context variables in `dashboard()` and two new HTML sections. Member detail gains a history-diff helper in the view. All changes are additive — no existing functionality is removed.

**Tech Stack:** Django 5, vanilla JS, existing CSS custom properties (`var(--color-primary)` etc.).

---

## File Map

| File | Change |
|---|---|
| `static/css/style.css` | Append tab bar CSS |
| `members/views.py` | Add `by_status` + `birthdays` to `dashboard()`; add `history_changes` to `member_detail()` |
| `templates/members/dashboard.html` | Add Sebaran Usia table + Ulang Tahun Pekan Ini section |
| `templates/members/member_detail.html` | Rewrite with 4 tab panels + JS |
| `members/test.py` | Tests for dashboard context and detail tab rendering |

---

### Task 1: Tab Bar CSS

**Files:**
- Modify: `static/css/style.css` (append at end)

No unit tests for CSS — verified visually and by Task 3 integration tests.

- [ ] **Step 1: Append tab CSS to `static/css/style.css`**

Add at the very end of the file:

```css
/* ===========================
   TABS
   =========================== */
.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.6rem 1.25rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--color-text-muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
}

.tab-btn:hover { color: var(--color-text); }

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.tab-panel--hidden { display: none; }
```

- [ ] **Step 4: Commit CSS only**

```
git add static/css/style.css
git commit -m "feat: add tab bar CSS"
```

---

### Task 2: Dashboard — View + Template

**Files:**
- Modify: `members/views.py` (lines 102–123, `dashboard` function)
- Modify: `templates/members/dashboard.html`
- Test: `members/test.py`

- [ ] **Step 1: Add failing tests to `members/test.py`**

Add this class at the bottom of the file:

```python
class DashboardContextTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='dash_staff', password='pass', is_staff=True
        )
        self.client.login(username='dash_staff', password='pass')

    def test_by_status_in_context(self):
        Member.objects.create(
            no_sensus='D001', nama_lengkap='Anak Test',
            jenis_kelamin='L', kewargaan='Warga', status='Anak'
        )
        response = self.client.get(reverse('members:dashboard'))
        self.assertIn('by_status', response.context)

    def test_birthdays_in_context(self):
        response = self.client.get(reverse('members:dashboard'))
        self.assertIn('birthdays', response.context)

    def test_dashboard_contains_sebaran_usia(self):
        response = self.client.get(reverse('members:dashboard'))
        self.assertContains(response, 'Sebaran Kategori Usia')

    def test_dashboard_contains_ulang_tahun(self):
        response = self.client.get(reverse('members:dashboard'))
        self.assertContains(response, 'Ulang Tahun')
```

- [ ] **Step 2: Run tests — confirm they fail**

```
venv\Scripts\python manage.py test members.test.DashboardContextTest
```

Expected: FAIL — `KeyError: 'by_status'`

- [ ] **Step 3: Update `dashboard()` in `members/views.py`**

Replace the entire `dashboard` function (currently lines 102–123) with:

```python
@login_required
def dashboard(request):
    from datetime import date, timedelta

    total = Member.objects.count()
    by_kewargaan = Member.objects.values('kewargaan').annotate(total=Count('id')).order_by('kewargaan')
    by_blok = Member.objects.exclude(blok='').values('blok').annotate(
        total_keluarga=Count('id')
    ).order_by('blok')
    by_status = Member.objects.values('status').annotate(total=Count('id')).order_by('status')
    baptized = Member.objects.filter(sudah_baptis=True).count()
    sidi = Member.objects.filter(sudah_sidi=True).count()
    dewasa = Member.objects.filter(status='Dewasa').count()
    anak = Member.objects.filter(status='Anak').count()
    total_keluarga = Keluarga.objects.count()

    today = date.today()
    week_dates = [today + timedelta(days=i) for i in range(7)]
    birthdays = []
    for d in week_dates:
        for m in Member.objects.filter(
            tanggal_lahir__isnull=False,
            tanggal_lahir__month=d.month,
            tanggal_lahir__day=d.day,
        ).exclude(kewargaan='Meninggal'):
            birthdays.append({'member': m, 'date': d, 'is_today': d == today})

    return render(request, 'members/dashboard.html', {
        'total': total,
        'by_kewargaan': by_kewargaan,
        'by_blok': by_blok,
        'by_status': by_status,
        'baptized': baptized,
        'sidi': sidi,
        'dewasa': dewasa,
        'anak': anak,
        'total_keluarga': total_keluarga,
        'birthdays': birthdays,
    })
```

- [ ] **Step 4: Run context tests — confirm they pass**

```
venv\Scripts\python manage.py test members.test.DashboardContextTest.test_by_status_in_context members.test.DashboardContextTest.test_birthdays_in_context
```

Expected: PASS

- [ ] **Step 5: Replace `templates/members/dashboard.html` with the updated version**

```html
{% extends 'base.html' %}
{% block title %}Dashboard — GKJ Salatiga{% endblock %}

{% block content %}
<div class="members-layout">
  <div class="container">

    <div class="members-header">
      <h1>Dashboard</h1>
      <a href="{% url 'members:member_list' %}" class="btn btn--outline">&larr; Members</a>
    </div>

    <!-- Stat cards -->
    <div class="detail-grid" style="margin-bottom: 2rem;">
      <div class="stat-card">
        <p class="stat-card__number">{{ total }}</p>
        <p class="stat-card__label">Total Anggota</p>
      </div>
      <div class="stat-card">
        <p class="stat-card__number">{{ total_keluarga }}</p>
        <p class="stat-card__label">Total Keluarga</p>
      </div>
      <div class="stat-card">
        <p class="stat-card__number">{{ dewasa }}</p>
        <p class="stat-card__label">Dewasa</p>
      </div>
      <div class="stat-card">
        <p class="stat-card__number">{{ anak }}</p>
        <p class="stat-card__label">Anak</p>
      </div>
      <div class="stat-card">
        <p class="stat-card__number">{{ baptized }}</p>
        <p class="stat-card__label">Sudah Baptis</p>
      </div>
      <div class="stat-card">
        <p class="stat-card__number">{{ sidi }}</p>
        <p class="stat-card__label">Sudah Sidi</p>
      </div>
    </div>

    <!-- Tables row -->
    <div class="detail-grid" style="margin-bottom: 2rem;">
      <div class="detail-section" style="flex: 1;">
        <h3>Anggota per Kewargaan</h3>
        <table class="data-table">
          <thead><tr><th>Kewargaan</th><th>Jumlah</th></tr></thead>
          <tbody>
            {% for row in by_kewargaan %}
            <tr><td>{{ row.kewargaan }}</td><td>{{ row.total }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      <div class="detail-section" style="flex: 1;">
        <h3>Anggota per Blok</h3>
        <table class="data-table">
          <thead><tr><th>Blok</th><th>Anggota</th></tr></thead>
          <tbody>
            {% for row in by_blok %}
            <tr><td>{{ row.blok }}</td><td>{{ row.total_keluarga }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      <div class="detail-section" style="flex: 1;">
        <h3>Sebaran Kategori Usia</h3>
        <table class="data-table">
          <thead><tr><th>Kategori</th><th>Jumlah</th></tr></thead>
          <tbody>
            {% for row in by_status %}
            <tr><td>{{ row.status }}</td><td>{{ row.total }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Birthdays this week -->
    {% if birthdays %}
    <div class="detail-section">
      <h3>Ulang Tahun Pekan Ini</h3>
      <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
        {% for item in birthdays %}
        <div class="birthday-card {% if item.is_today %}birthday-card--today{% endif %}">
          <p class="birthday-card__name">{{ item.member.nama_lengkap }}</p>
          <p class="birthday-card__date">
            {{ item.date|date:"j F" }}
            {% if item.member.blok %} &middot; {{ item.member.blok }}{% endif %}
            {% if item.is_today %} 🎂{% endif %}
          </p>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endif %}

  </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Run all dashboard tests**

```
venv\Scripts\python manage.py test members.test.DashboardContextTest
```

Expected: all 4 pass.

- [ ] **Step 7: Commit**

```
git add members/views.py templates/members/dashboard.html members/test.py
git commit -m "feat: add sebaran usia and birthday widget to staff dashboard"
```

---

### Task 3: Member Detail — View + Tabs Template

**Files:**
- Modify: `members/views.py` (`member_detail` function, lines 42–44)
- Modify: `templates/members/member_detail.html`
- Test: `members/test.py`

- [ ] **Step 1: Add failing tests to `members/test.py`**

Add this full test class at the bottom:

```python
class MemberDetailTabsTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff2', password='pass', is_staff=True
        )
        self.client.login(username='staff2', password='pass')
        self.member = Member.objects.create(
            no_sensus='TAB001', nama_lengkap='Tab Tester',
            jenis_kelamin='L', kewargaan='Warga', status='Dewasa'
        )

    def test_detail_page_contains_tab_buttons(self):
        response = self.client.get(reverse('members:member_detail', args=[self.member.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tab-btn')
        self.assertContains(response, 'Data Pribadi')
        self.assertContains(response, 'Iman')
        self.assertContains(response, 'Pelayanan')
        self.assertContains(response, 'Riwayat')

    def test_detail_shows_alamat_domisili(self):
        self.member.alamat_domisili = 'Jl. Test No. 1'
        self.member.save()
        response = self.client.get(reverse('members:member_detail', args=[self.member.pk]))
        self.assertContains(response, 'Jl. Test No. 1')

    def test_detail_shows_baptis_oleh(self):
        self.member.baptis_oleh = 'Pdt. Test'
        self.member.save()
        response = self.client.get(reverse('members:member_detail', args=[self.member.pk]))
        self.assertContains(response, 'Pdt. Test')

    def test_history_changes_in_context(self):
        response = self.client.get(reverse('members:member_detail', args=[self.member.pk]))
        self.assertIn('history_changes', response.context)
```

- [ ] **Step 2: Run new tests — confirm they fail**

```
venv\Scripts\python manage.py test members.test.MemberDetailTabsTest
```

Expected: `test_detail_page_contains_tab_buttons` FAIL, others FAIL.

- [ ] **Step 3: Update `member_detail()` in `members/views.py`**

Replace the existing `member_detail` function (lines 42–44):

```python
@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)

    history_records = list(member.history.all())
    history_changes = []
    for i, record in enumerate(history_records):
        entry = {
            'type': record.history_type,
            'fields': [],
        }
        if record.history_type == '~' and i + 1 < len(history_records):
            delta = record.diff_against(history_records[i + 1])
            for change in delta.changes:
                entry['fields'].append({
                    'field': change.field,
                    'old': change.old,
                    'new': change.new,
                })
        history_changes.append(entry)

    return render(request, 'members/member_detail.html', {
        'member': member,
        'history_changes': history_changes,
    })
```

- [ ] **Step 4: Replace `templates/members/member_detail.html` entirely**

```html
{% extends 'base.html' %}
{% block title %}{{ member.nama_lengkap }} — GKJ Salatiga{% endblock %}

{% block content %}
<div class="members-layout">
  <div class="container" style="max-width: 900px;">

    <div style="margin-bottom: 1.5rem;">
      <a href="{% url 'members:member_list' %}" class="btn btn--outline">&larr; Back to Members</a>
    </div>

    <h1 style="font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
      {{ member.nama_lengkap }}
    </h1>
    <p style="color: var(--color-text-muted); margin-bottom: 1.5rem;">
      No. Sensus: {{ member.no_sensus }}
      {% if member.blok %} &middot; Blok {{ member.blok }}{% endif %}
    </p>

    <!-- Tab bar -->
    <div class="tab-bar">
      <button class="tab-btn active" data-tab="pribadi">Data Pribadi</button>
      <button class="tab-btn" data-tab="iman">Iman</button>
      <button class="tab-btn" data-tab="pelayanan">Pelayanan</button>
      <button class="tab-btn" data-tab="riwayat">Riwayat</button>
    </div>

    <!-- Tab 1: Data Pribadi -->
    <div id="tab-pribadi" class="tab-panel">
      <div class="detail-section">
        <h3>Data Pribadi</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Jenis Kelamin</p>
            <p class="detail-item__value">{{ member.get_jenis_kelamin_display }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tempat, Tanggal Lahir</p>
            <p class="detail-item__value">
              {{ member.tempat_lahir|default:"—" }}{% if member.tanggal_lahir %}, {{ member.tanggal_lahir }}{% endif %}
            </p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Kategori Usia</p>
            <p class="detail-item__value">{{ member.status|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Status Perkawinan</p>
            <p class="detail-item__value">{{ member.status_perkawinan|default:"—" }}</p>
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
          <div class="detail-item">
            <p class="detail-item__label">Nomor Telepon</p>
            <p class="detail-item__value">{{ member.nomor_telepon|default:"—" }}</p>
          </div>
        </div>
      </div>

      <div class="detail-section">
        <h3>Alamat & Keluarga</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Alamat Domisili</p>
            <p class="detail-item__value">{{ member.alamat_domisili|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Alamat KTP</p>
            <p class="detail-item__value">{{ member.alamat_ktp|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Blok</p>
            <p class="detail-item__value">{{ member.blok|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Keluarga</p>
            <p class="detail-item__value">
              {% if member.keluarga %}{{ member.keluarga.nama_keluarga }}{% else %}—{% endif %}
            </p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Status dalam Keluarga</p>
            <p class="detail-item__value">{{ member.ket_status|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Status Rumah Tinggal</p>
            <p class="detail-item__value">{{ member.status_rumah_tinggal|default:"—" }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 2: Iman -->
    <div id="tab-iman" class="tab-panel tab-panel--hidden">
      <div class="detail-section">
        <h3>Kewargaan & Ibadah</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Kewargaan</p>
            <p class="detail-item__value">
              <span class="badge badge--{{ member.kewargaan|lower|cut:' ' }}">
                {{ member.kewargaan }}
              </span>
            </p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tempat Kebaktian</p>
            <p class="detail-item__value">{{ member.tempat_kebaktian|default:"—" }}</p>
          </div>
          {% if member.nama_gereja_lain %}
          <div class="detail-item">
            <p class="detail-item__label">Nama Gereja</p>
            <p class="detail-item__value">{{ member.nama_gereja_lain }}</p>
          </div>
          {% endif %}
        </div>
      </div>

      <div class="detail-section">
        <h3>Baptis</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Status</p>
            <p class="detail-item__value">{% if member.sudah_baptis %}Sudah Baptis{% else %}Belum Baptis{% endif %}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Dibaptis oleh</p>
            <p class="detail-item__value">{{ member.baptis_oleh|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tanggal Baptis</p>
            <p class="detail-item__value">{{ member.tanggal_baptis|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tempat Baptis</p>
            <p class="detail-item__value">{{ member.tempat_baptis|default:"—" }}</p>
          </div>
        </div>
      </div>

      <div class="detail-section">
        <h3>Sidi</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Status</p>
            <p class="detail-item__value">{% if member.sudah_sidi %}Sudah Sidi{% else %}Belum Sidi{% endif %}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Disidi oleh</p>
            <p class="detail-item__value">{{ member.sidi_oleh|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tanggal Sidi</p>
            <p class="detail-item__value">{{ member.tanggal_sidi|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tempat Sidi</p>
            <p class="detail-item__value">{{ member.tempat_sidi|default:"—" }}</p>
          </div>
        </div>
      </div>

      {% if member.nikah_oleh or member.tanggal_nikah %}
      <div class="detail-section">
        <h3>Nikah</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Dinikahkan oleh</p>
            <p class="detail-item__value">{{ member.nikah_oleh|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tanggal Nikah</p>
            <p class="detail-item__value">{{ member.tanggal_nikah|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Tempat Nikah</p>
            <p class="detail-item__value">{{ member.tempat_nikah|default:"—" }}</p>
          </div>
        </div>
      </div>
      {% endif %}
    </div>

    <!-- Tab 3: Pelayanan -->
    <div id="tab-pelayanan" class="tab-panel tab-panel--hidden">
      <div class="detail-section">
        <h3>Minat Pelayanan</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <p class="detail-item__label">Minat Pelayanan Gerejawi</p>
            <p class="detail-item__value">{{ member.minat_pelayanan_gerejawi|default:"—" }}</p>
          </div>
          <div class="detail-item">
            <p class="detail-item__label">Minat Pelayanan Umum</p>
            <p class="detail-item__value">{{ member.minat_pelayanan_umum|default:"—" }}</p>
          </div>
        </div>
      </div>

      {% if member.pelayanan_diikuti %}
      <div class="detail-section">
        <h3>Pelayanan Diikuti</h3>
        <p>{{ member.pelayanan_diikuti }}</p>
      </div>
      {% endif %}

      {% if member.ibadah_sering_diikuti %}
      <div class="detail-section">
        <h3>Ibadah Sering Diikuti</h3>
        <p>{{ member.ibadah_sering_diikuti }}</p>
      </div>
      {% endif %}
    </div>

    <!-- Tab 4: Riwayat -->
    <div id="tab-riwayat" class="tab-panel tab-panel--hidden">
      <div class="detail-section">
        <h3>Riwayat Perubahan</h3>
        {% if history_changes %}
        <table class="data-table">
          <thead>
            <tr>
              <th>Jenis</th>
              <th>Perubahan</th>
            </tr>
          </thead>
          <tbody>
            {% for entry in history_changes %}
            <tr>
              <td>
                {% if entry.type == '+' %}Ditambah
                {% elif entry.type == '~' %}Diubah
                {% else %}Dihapus{% endif %}
              </td>
              <td>
                {% if entry.fields %}
                  {% for f in entry.fields %}
                    <div style="font-size: 0.875rem;">
                      <strong>{{ f.field }}</strong>: {{ f.old|default:"—" }} → {{ f.new|default:"—" }}
                    </div>
                  {% endfor %}
                {% else %}
                  <span style="color: var(--color-text-muted);">—</span>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% else %}
        <p style="color: var(--color-text-muted);">Belum ada riwayat perubahan.</p>
        {% endif %}
      </div>
    </div>

    <!-- Actions -->
    <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
      <a href="{% url 'members:member_edit' member.pk %}" class="btn btn--primary">Edit</a>
      <a href="{% url 'members:member_list' %}" class="btn btn--outline">Back to List</a>
    </div>

  </div>
</div>

<script>
  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
      document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.add('tab-panel--hidden'); });
      btn.classList.add('active');
      document.getElementById('tab-' + btn.dataset.tab).classList.remove('tab-panel--hidden');
    });
  });
</script>
{% endblock %}
```

- [ ] **Step 5: Run all member detail tests**

```
venv\Scripts\python manage.py test members.test.MemberDetailTabsTest
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Run full test suite**

```
venv\Scripts\python manage.py test members website
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```
git add members/views.py templates/members/member_detail.html members/test.py
git commit -m "feat: reorganise member detail into 4 selectable tabs"
```

---

## Summary

| Task | Files | Tests |
|---|---|---|
| 1 | `style.css` | 1 (CSS class present) |
| 2 | `views.py`, `dashboard.html` | 4 |
| 3 | `views.py`, `member_detail.html` | 4 |
