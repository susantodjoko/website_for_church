from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('sermons/', views.sermon_list, name='sermon_list'),
    path('sermons/<slug:slug>/', views.sermon_detail, name='sermon_detail'),
    path('events/', views.event_list, name='event_list'),
    path('about/', views.about, name='about'),
    path('visit/', views.visit, name='visit'),
    path('series/', views.series_list, name='series_list'),
    path('series/<int:pk>/', views.series_detail, name='series_detail'),
    path('warta/', views.warta_list, name='warta_list'),
    path('warta/<slug:slug>/', views.warta_detail, name='warta_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<slug:slug>/', views.album_detail, name='album_detail'),
    path('giving/', views.giving, name='giving'),
    path('contact/', views.contact, name='contact'),

]
