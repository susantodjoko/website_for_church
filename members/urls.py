from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'members'

#def placeholder(request):
 #   return HttpResponse('Members area coming soon.')

urlpatterns = [
    path('hub/', views.staff_hub, name='staff_hub'),
    path('', views.member_list, name='member_list'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('families/', views.family_list, name='family_list'),
    path('families/<int:pk>/', views.family_detail, name='family_detail'),
    path('export/csv/', views.export_members_csv, name='export_members_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('import/csv/', views.import_members_csv, name='import_members_csv'),
    path('<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('print/blok/', views.print_blok, name='print_blok'),
]
