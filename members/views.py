from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Member, Keluarga


@login_required
def member_list(request):
    query = request.GET.get('q', '')
    members = Member.objects.select_related('keluarga').all()
    if query:
        members = members.filter(
            Q(nama_lengkap__icontains=query) | Q(no_sensus__icontains=query)
        )
    paginator = Paginator(members, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'members/member_list.html', {'page': page, 'query': query})


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'members/member_detail.html', {'member': member})


@login_required
def family_list(request):
    query = request.GET.get('q', '')
    families = Keluarga.objects.all()
    if query:
        families = families.filter(nama_keluarga__icontains=query)
    paginator = Paginator(families, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'members/family_list.html', {'page': page, 'query': query})
