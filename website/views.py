from django.shortcuts import render, get_object_or_404
from .models import HeroSlide, Sermon, Ministry, ServiceTime, Event, AboutPage, News, Liturgi, SermonSeries
from django.core.paginator import Paginator

def home(request):
    hero = HeroSlide.objects.filter(is_active=True).first()
    featured_sermons = Sermon.objects.filter(is_featured=True)[:3]
    ministries = Ministry.objects.all()[:6]
    service_times = ServiceTime.objects.all()
    upcoming_events = Event.objects.filter(is_published=True)[:3]
    latest_news = News.objects.filter(is_published=True)[:3]
    return render(request, 'website/home.html', {
        'hero': hero,
        'featured_sermons': featured_sermons,
        'ministries': ministries,
        'service_times': service_times,
        'upcoming_events': upcoming_events,
        'latest_news': latest_news,
    })


def sermon_list(request):
    topic = request.GET.get('topic', '')
    sermons = Sermon.objects.all()
    if topic:
        sermons = sermons.filter(topic=topic)
    return render(request, 'website/sermons.html', {'sermons': sermons, 'topic': topic})


def sermon_detail(request, pk):
    sermon = get_object_or_404(Sermon, pk=pk)
    video_id = _extract_youtube_id(sermon.youtube_url)
    return render(request, 'website/sermon_detail.html', {
        'sermon': sermon,
        'video_id': video_id,
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

def news(request):
    query = request.GET.get('q', '')
    news_list = News.objects.filter(is_published=True)
    if query:
        news_list = news_list.filter(title__icontains=query)
    paginator = Paginator(news_list, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/news.html', {'page': page, 'query': query})

def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'website/news_detail.html', {'news': news})


def _extract_youtube_id(url):
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return ''

def liturgi(request):
    query = request.GET.get('q', '')
    liturgi_qs = Liturgi.objects.filter(is_published=True)
    if query:
        liturgi_qs = liturgi_qs.filter(title__icontains=query)
    paginator = Paginator(liturgi_qs, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'website/liturgi.html', {'page': page, 'query': query})


def liturgi_detail(request, pk):
    liturgi = get_object_or_404(Liturgi, pk=pk)
    return render(request, 'website/liturgi_detail.html', {'liturgi': liturgi})


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

