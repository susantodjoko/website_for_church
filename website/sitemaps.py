from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Album, Ministry, Sermon, SermonSeries, WartaJemaat


class SiteSitemap(Sitemap):
    """Always list URLs on SITE_URL, whichever host the sitemap was requested on."""

    def get_protocol(self, protocol=None):
        return urlsplit(settings.SITE_URL).scheme

    def get_domain(self, site=None):
        return urlsplit(settings.SITE_URL).netloc


class StaticPageSitemap(SiteSitemap):
    changefreq = 'weekly'

    def items(self):
        return [
            'home', 'sermon_list', 'warta_list', 'bacaan', 'event_list', 'gallery',
            'ministry_list', 'series_list', 'visit', 'about', 'giving', 'contact',
        ]

    def location(self, item):
        return reverse(f'website:{item}')

    def priority(self, item):
        return 1.0 if item == 'home' else 0.6


class SermonSitemap(SiteSitemap):

    def items(self):
        return Sermon.objects.all()

    def location(self, obj):
        return reverse('website:sermon_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.date


class WartaSitemap(SiteSitemap):

    def items(self):
        return WartaJemaat.objects.filter(is_published=True)

    def location(self, obj):
        return reverse('website:warta_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.date


class AlbumSitemap(SiteSitemap):

    def items(self):
        return Album.objects.filter(is_published=True)

    def location(self, obj):
        return reverse('website:album_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.date


class MinistrySitemap(SiteSitemap):

    def items(self):
        return Ministry.objects.all()

    def location(self, obj):
        return reverse('website:ministry_detail', args=[obj.pk])


class SeriesSitemap(SiteSitemap):

    def items(self):
        return SermonSeries.objects.order_by('pk')

    def location(self, obj):
        return reverse('website:series_detail', args=[obj.pk])


sitemaps = {
    'halaman': StaticPageSitemap,
    'khotbah': SermonSitemap,
    'publikasi': WartaSitemap,
    'galeri': AlbumSitemap,
    'komisi': MinistrySitemap,
    'seri': SeriesSitemap,
}
