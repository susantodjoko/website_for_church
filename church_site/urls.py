"""
URL configuration for church_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static as static_url
from django.views.generic import RedirectView
from church_site.admin_sites import content_admin, members_admin
from website.sitemaps import sitemaps
from website.views import robots_txt

urlpatterns = [
    # Superuser admin (users, groups, full access)
    path('admin/', admin.site.urls),
    # Content editors: sermons, warta, gallery, events, about
    path('konten/', content_admin.urls),
    # Member staff: census, families, dashboard
    path('jemaat/', members_admin.urls),
    path('', include('website.urls')),
    path('members/', include('members.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),
    path('favicon.ico', RedirectView.as_view(url=static_url('images/favicon.ico'), permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR_ENABLED:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()

