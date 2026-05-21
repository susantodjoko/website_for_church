from django.contrib import admin
from .models import HeroSlide, SermonSeries, Sermon, Ministry, ServiceTime, Event, AboutPage, News, Liturgi, WartaJemaat
from django_summernote.admin import SummernoteModelAdmin


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['headline', 'is_active']


@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Sermon)
class SermonAdmin(SummernoteModelAdmin):
    list_display = ['title', 'series', 'pastor', 'date', 'is_featured']
    list_filter = ['series', 'topic']
    search_fields = ['title', 'pastor']
    summernote_fields = ['description']

@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = ['campus_name', 'is_online']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'is_published']
    list_filter = ['is_published', 'date']


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

@admin.register(News)
class NewsAdmin(SummernoteModelAdmin):
    list_display = ['title', 'date', 'is_published']
    list_filter = ['is_published']
    summernote_fields = ['content']

@admin.register(Liturgi)
class LiturgiAdmin(SummernoteModelAdmin):
    list_display = ['title', 'date', 'is_published']
    list_filter = ['is_published']
    summernote_fields = ['content']


@admin.register(WartaJemaat)
class WartaJemaatAdmin(SummernoteModelAdmin):
    list_display = ['title', 'category', 'date', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['title']
    summernote_fields = ['content']


