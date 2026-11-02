from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Q
from .models import HeroSlide, Sermon, Topic, Ministry, ServiceTime, Event, AboutPage, SermonSeries, WartaJemaat, Album, BacaanHarian, TemaBulan
from django.core.paginator import Paginator
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from members.models import Member


def home(request):
    hero = HeroSlide.objects.filter(is_active=True).first()
    featured_sermons = Sermon.objects.filter(is_featured=True)[:3]
    all_ministries = Ministry.objects.all()
    # Staff pick up to 6 for the home page; fall back to the first 6 by order
    ministries = all_ministries.filter(show_on_home=True)[:6] or all_ministries[:6]
    service_times = ServiceTime.objects.all()
    today = date.today()
    upcoming_events = Event.objects.filter(is_published=True, date__gte=today)[:3]
    published = WartaJemaat.objects.filter(is_published=True)
    latest_news = published.filter(category='berita')[:3]
    # Newest weekly warta and liturgy, shown as a compact link row
    weekly_docs = [
        doc for doc in (
            published.filter(category='warta').first(),
            published.filter(category='liturgi').first(),
        ) if doc
    ]

    week_dates = [today + timedelta(days=i) for i in range(7)]
    birthdays = []
    for d in week_dates:
        for m in Member.objects.filter(
            tanggal_lahir__month=d.month,
            tanggal_lahir__day=d.day,
        ).exclude(kewargaan='Meninggal'):
            birthdays.append({'member': m, 'date': d, 'is_today': d == today})
    return render(request, 'website/home.html', {
        'hero': hero,
        'featured_sermons': featured_sermons,
        'ministries': ministries,
        'ministry_total': all_ministries.count(),
        'service_times': service_times,
        'upcoming_events': upcoming_events,
        'latest_news': latest_news,
        'weekly_docs': weekly_docs,
        'birthdays': birthdays,
        'bacaan_today': BacaanHarian.objects.filter(tanggal=_jakarta_today()),
    })


def sermon_list(request):
    try:
        topic_id = int(request.GET.get('topic', ''))
    except (ValueError, TypeError):
        topic_id = None
    query = request.GET.get('q', '')
    sermons = Sermon.objects.all()
    if topic_id:
        sermons = sermons.filter(topic_id=topic_id)
    if query:
        sermons = sermons.filter(
            Q(title__icontains=query) | Q(pastor__icontains=query) | Q(description__icontains=query)
        )
    paginator = Paginator(sermons, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/sermons.html', {
        'page': page,
        'topic': topic_id,
        'query': query,
        'topics': Topic.objects.all(),
    })


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


def event_list(request):
    today = date.today()
    events = Event.objects.filter(is_published=True)
    reports = Prefetch(
        'reports',
        queryset=WartaJemaat.objects.filter(is_published=True, category='berita'),
        to_attr='published_reports',
    )
    return render(request, 'website/events.html', {
        'events': events.filter(date__gte=today),
        'past_events': events.filter(date__lt=today).order_by('-date').prefetch_related(reports)[:12],
    })


def ministry_list(request):
    return render(request, 'website/ministries.html', {'ministries': Ministry.objects.all()})


def ministry_detail(request, pk):
    ministry = get_object_or_404(Ministry, pk=pk)
    return render(request, 'website/ministry_detail.html', {'ministry': ministry})


def about(request):
    about_page = AboutPage.objects.first()
    return render(request, 'website/about.html', {'about': about_page})


def visit(request):
    service_times = ServiceTime.objects.all()
    return render(request, 'website/visit.html', {'service_times': service_times})



def _extract_youtube_id(url):
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return ''



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


def warta_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    warta_qs = WartaJemaat.objects.filter(is_published=True)
    if query:
        warta_qs = warta_qs.filter(title__icontains=query)
    if category:
        warta_qs = warta_qs.filter(category=category)
    paginator = Paginator(warta_qs, 9)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/warta.html', {
        'page': page,
        'query': query,
        'category': category,
        'categories': WartaJemaat.CATEGORY_CHOICES,
    })


def warta_detail(request, slug):
    warta = get_object_or_404(WartaJemaat, slug=slug)
    return render(request, 'website/warta_detail.html', {'warta': warta})

def gallery(request):
    albums = Album.objects.filter(is_published=True)
    return render(request, 'website/gallery.html', {'albums': albums})


def album_detail(request, slug):
    album = get_object_or_404(Album, slug=slug)
    photos = album.photos.all()
    return render(request, 'website/album_detail.html', {
        'album': album,
        'photos': photos,
    })

def giving(request):
    return render(request, 'website/giving.html')


def contact(request):
    # The message form is switched off; visitors reach the office via WhatsApp.
    return render(request, 'website/contact.html')


HARI = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
         'Agustus', 'September', 'Oktober', 'November', 'Desember']


def _jakarta_today():
    # The server clock is UTC; the daily reading should turn over at midnight WIB
    return timezone.localdate(timezone=ZoneInfo('Asia/Jakarta'))


def bacaan(request):
    today = _jakarta_today()
    try:
        chosen = date.fromisoformat(request.GET.get('minggu', ''))
    except ValueError:
        chosen = today
    monday = chosen - timedelta(days=chosen.weekday())
    sunday = monday + timedelta(days=6)

    by_date = {}
    for entry in BacaanHarian.objects.filter(tanggal__range=(monday, sunday)):
        by_date.setdefault(entry.tanggal, []).append(entry)
    days = []
    for i in range(7):
        d = monday + timedelta(days=i)
        days.append({
            'date': d,
            'hari': HARI[i],
            'tanggal': f'{d.day} {BULAN[d.month - 1]} {d.year}',
            'entries': by_date.get(d, []),
            'is_today': d == today,
        })

    months = {(monday.year, monday.month), (sunday.year, sunday.month)}
    themes = [
        {'bulan': BULAN[t.bulan - 1], 'tema': t.tema, 'keterangan': t.keterangan}
        for t in TemaBulan.objects.all()
        if (t.tahun, t.bulan) in months
    ]
    if monday.month == sunday.month:
        range_label = f'{monday.day}–{sunday.day} {BULAN[sunday.month - 1]} {sunday.year}'
    else:
        range_label = (f'{monday.day} {BULAN[monday.month - 1]} – '
                       f'{sunday.day} {BULAN[sunday.month - 1]} {sunday.year}')

    return render(request, 'website/bacaan.html', {
        'days': days,
        'has_entries': bool(by_date),
        'themes': themes,
        'range_label': range_label,
        'is_this_week': monday <= today <= sunday,
        'prev_week': monday - timedelta(days=7),
        'next_week': monday + timedelta(days=7),
    })
