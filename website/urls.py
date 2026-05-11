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
]
