from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('sermons/', views.sermon_list, name='sermon_list'),
    path('sermons/<int:pk>/', views.sermon_detail, name='sermon_detail'),
    path('events/', views.event_list, name='event_list'),
    path('about/', views.about, name='about'),
    path('visit/', views.visit, name='visit'),
    path('news/', views.news, name='news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('liturgi/', views.liturgi, name='liturgi'),
    path('liturgi/<int:pk>/', views.liturgi_detail, name='liturgi_detail'),
    path('series/', views.series_list, name='series_list'),
    path('series/<int:pk>/', views.series_detail, name='series_detail'),
]
