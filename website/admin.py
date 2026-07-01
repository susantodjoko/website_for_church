from django.contrib import admin
from django.db import models as db_models
from django.forms.widgets import ClearableFileInput
from django_summernote.admin import SummernoteModelAdmin
from church_site.admin_sites import content_admin
from .models import HeroSlide, SermonSeries, Sermon, Topic, Ministry, ServiceTime, Event, AboutPage, AboutValue, Pendeta, WartaJemaat, Album, Photo, ContactMessage


class FileInputNoAccept(ClearableFileInput):
    """ClearableFileInput without accept="image/*" to prevent Windows file dialog freeze."""
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.pop('accept', None)
        return attrs


class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['headline', 'is_active']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, db_models.ImageField):
            kwargs['widget'] = FileInputNoAccept
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']


class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ['name']


class SermonAdmin(SummernoteModelAdmin):
    list_display = ['title', 'series', 'pastor', 'date', 'is_featured']
    list_filter = ['series', 'topic']
    search_fields = ['title', 'pastor']
    summernote_fields = ['description']


class MinistryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = ['campus_name', 'is_online']


class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'is_published']
    list_filter = ['is_published', 'date']


class AboutValueInline(admin.TabularInline):
    model = AboutValue
    extra = 1
    fields = ['title', 'body', 'order']


class PendetaInline(admin.StackedInline):
    model = Pendeta
    extra = 1
    fields = ['nama', 'jabatan', 'bio', 'foto', 'order']


class AboutPageAdmin(SummernoteModelAdmin):
    summernote_fields = ['mission_statement', 'pastor_bio']
    inlines = [PendetaInline, AboutValueInline]

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()


class WartaJemaatAdmin(SummernoteModelAdmin):
    list_display = ['title', 'category', 'date', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['title']
    summernote_fields = ['content']


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 3


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'is_published']
    list_filter = ['is_published']
    inlines = [PhotoInline]


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'message_type', 'submitted_at', 'is_read']
    list_filter = ['message_type', 'is_read']
    readonly_fields = ['name', 'email', 'message_type', 'message', 'submitted_at']


# ── Default admin site (superusers) ──────────────────────────────────────────
admin.site.register(HeroSlide, HeroSlideAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(SermonSeries, SermonSeriesAdmin)
admin.site.register(Sermon, SermonAdmin)
admin.site.register(Ministry, MinistryAdmin)
admin.site.register(ServiceTime, ServiceTimeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(AboutPage, AboutPageAdmin)
admin.site.register(WartaJemaat, WartaJemaatAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)

# ── Content admin site (content editors) ─────────────────────────────────────
content_admin.register(HeroSlide, HeroSlideAdmin)
content_admin.register(Topic, TopicAdmin)
content_admin.register(SermonSeries, SermonSeriesAdmin)
content_admin.register(Sermon, SermonAdmin)
content_admin.register(Ministry, MinistryAdmin)
content_admin.register(ServiceTime, ServiceTimeAdmin)
content_admin.register(Event, EventAdmin)
content_admin.register(AboutPage, AboutPageAdmin)
content_admin.register(WartaJemaat, WartaJemaatAdmin)
content_admin.register(Album, AlbumAdmin)
content_admin.register(ContactMessage, ContactMessageAdmin)
