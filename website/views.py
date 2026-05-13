from django.shortcuts import render, get_object_or_404
from .models import HeroSlide, Sermon, Ministry, ServiceTime, Event, AboutPage, News


def home(request):
    hero = HeroSlide.objects.filter(is_active=True).first()
    featured_sermons = Sermon.objects.filter(is_featured=True)[:3]
    ministries = Ministry.objects.all()[:6]
    service_times = ServiceTime.objects.all()
    upcoming_events = Event.objects.filter(is_published=True)[:3]
    return render(request, 'website/home.html', {
        'hero': hero,
        'featured_sermons': featured_sermons,
        'ministries': ministries,
        'service_times': service_times,
        'upcoming_events': upcoming_events,
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
    news_list = News.objects.filter(is_published=True).order_by('-date')
    return render(request, 'website/news.html', {'news_list': news_list})

def _extract_youtube_id(url):
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return ''
