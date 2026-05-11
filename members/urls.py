from django.urls import path
from django.http import HttpResponse

app_name = 'members'

def placeholder(request):
    return HttpResponse('Members area coming soon.')

urlpatterns = [
    path('', placeholder, name='member_list'),
]
