from django.shortcuts import render, get_object_or_404
from .models import HeroSlide, Sermon, Ministry, ServiceTime, Event, AboutPage, SermonSeries, WartaJemaat, Album
from django.core.paginator import Paginator
from .forms import ContactForm
from datetime import date, timedelta
from members.models import Member


def home(request):
    hero = HeroSlide.objects.filter(is_active=True).first()
    featured_sermons = Sermon.objects.filter(is_featured=True)[:3]
    ministries = Ministry.objects.all()[:6]
    service_times = ServiceTime.objects.all()
    upcoming_events = Event.objects.filter(is_published=True)[:3]
    latest_news = WartaJemaat.objects.filter(is_published=True)[:3]
    
    today = date.today()
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
        'service_times': service_times,
        'upcoming_events': upcoming_events,
        'latest_news': latest_news,
        'birthdays': birthdays,
    })


def sermon_list(request):
    topic = request.GET.get('topic', '')
    sermons = Sermon.objects.all()
    if topic:
        sermons = sermons.filter(topic=topic)
    return render(request, 'website/sermons.html', {'sermons': sermons, 'topic': topic})


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
    events = Event.objects.filter(is_published=True)
    return render(request, 'website/events.html', {'events': events})


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

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'website/contact.html', {'form': form, 'sent': True})
    else:
        form = ContactForm()
    return render(request, 'website/contact.html', {'form': form, 'sent': False})
