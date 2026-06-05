from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count 
import csv
from .models import Member, Keluarga
from datetime import datetime
from django.http import HttpResponse 
from .forms import MemberForm
from django.shortcuts import render, get_object_or_404, redirect

@login_required
def member_list(request):
    query = request.GET.get('q', '')
    blok = request.GET.get('blok', '')
    kewargaan = request.GET.get('kewargaan', '')

    members = Member.objects.select_related('keluarga').all()
    if query:
        members = members.filter(
            Q(nama_lengkap__icontains=query) | Q(no_sensus__icontains=query)
        )
    if blok:
        members = members.filter(blok=blok)
    if kewargaan:
        members = members.filter(kewargaan=kewargaan)

    paginator = Paginator(members, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'members/member_list.html', {
        'page': page,
        'query': query,
        'blok': blok,
        'kewargaan': kewargaan,
        'blok_choices': Member.objects.exclude(blok='').values_list('blok', flat=True).distinct().order_by('blok'),
        'kewargaan_choices': Member.KEWARGAAN_CHOICES,
    })



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

@login_required
def family_detail(request, pk):
    family = get_object_or_404(Keluarga, pk=pk)
    members = family.members.all().order_by('ket_status', 'nama_lengkap')
    return render(request, 'members/family_detail.html', {
        'family': family,
        'members': members,
    })

@login_required
def export_members_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No. Sensus', 'Nama Lengkap', 'Jenis Kelamin', 'Tempat Lahir',
        'Tanggal Lahir', 'Nomor Telepon', 'Status', 'Kewargaan',
        'Ket. Status', 'Sudah Baptis', 'Sudah Sidi', 'Pendidikan',
        'Pekerjaan', 'Keluarga', 'Blok',
    ])

    members = Member.objects.select_related('keluarga').all()
    for m in members:
        writer.writerow([
            m.no_sensus,
            m.nama_lengkap,
            m.get_jenis_kelamin_display(),
            m.tempat_lahir,
            m.tanggal_lahir,
            m.nomor_telepon,
            m.status,
            m.kewargaan,
            m.ket_status,
            'Ya' if m.sudah_baptis else 'Tidak',
            'Ya' if m.sudah_sidi else 'Tidak',
            m.pendidikan,
            m.pekerjaan,
            m.keluarga.nama_keluarga if m.keluarga else '',
            m.keluarga.blok if m.keluarga else '',
        ])

    return response

@login_required
def dashboard(request):
    total = Member.objects.count()
    by_kewargaan = Member.objects.values('kewargaan').annotate(total=Count('id')).order_by('kewargaan')
    by_blok = Member.objects.exclude(blok='').values('blok').annotate(
        total_keluarga=Count('id')
    ).order_by('blok')
    baptized = Member.objects.filter(sudah_baptis=True).count()
    sidi = Member.objects.filter(sudah_sidi=True).count()
    dewasa = Member.objects.filter(status='Dewasa').count()
    anak = Member.objects.filter(status='Anak').count()
    total_keluarga = Keluarga.objects.count()

    return render(request, 'members/dashboard.html', {
        'total': total,
        'by_kewargaan': by_kewargaan,
        'by_blok': by_blok,
        'baptized': baptized,
        'sidi': sidi,
        'dewasa': dewasa,
        'anak': anak,
        'total_keluarga': total_keluarga,
    })

@login_required
def import_members_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)

        created = updated = errors = 0
        error_rows = []

        for i, row in enumerate(reader, start=2):
            try:
                no_sensus = row['No. Sensus'].strip()
                if not no_sensus:
                    continue

                # resolve keluarga by name
                keluarga = None
                if row.get('Keluarga', '').strip():
                    keluarga = Keluarga.objects.filter(
                        nama_keluarga=row['Keluarga'].strip()
                    ).first()

                # parse date
                tanggal_lahir = None
                if row.get('Tanggal Lahir', '').strip():
                    try:
                        tanggal_lahir = datetime.strptime(
                            row['Tanggal Lahir'].strip(), '%Y-%m-%d'
                        ).date()
                    except ValueError:
                        pass

                jk_map = {'Laki-laki': 'L', 'Perempuan': 'P'}
                defaults = {
                    'nama_lengkap': row.get('Nama Lengkap', '').strip(),
                    'jenis_kelamin': jk_map.get(row.get('Jenis Kelamin', '').strip(), 'L'),
                    'tempat_lahir': row.get('Tempat Lahir', '').strip(),
                    'tanggal_lahir': tanggal_lahir,
                    'nomor_telepon': row.get('Nomor Telepon', '').strip(),
                    'status': row.get('Status', 'Dewasa').strip(),
                    'kewargaan': row.get('Kewargaan', 'Warga').strip(),
                    'ket_status': row.get('Ket. Status', '').strip(),
                    'sudah_baptis': row.get('Sudah Baptis', '').strip() == 'Ya',
                    'sudah_sidi': row.get('Sudah Sidi', '').strip() == 'Ya',
                    'pendidikan': row.get('Pendidikan', '').strip(),
                    'pekerjaan': row.get('Pekerjaan', '').strip(),
                    'keluarga': keluarga,
                }

                _, is_created = Member.objects.update_or_create(
                    no_sensus=no_sensus, defaults=defaults
                )
                if is_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                errors += 1
                error_rows.append(f'Baris {i}: {e}')

        return render(request, 'members/import_csv.html', {
            'done': True,
            'created': created,
            'updated': updated,
            'errors': errors,
            'error_rows': error_rows,
        })

    return render(request, 'members/import_csv.html', {'done': False})

@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('members:member_detail', pk=pk)
    else:
        form = MemberForm(instance=member)
    return render(request, 'members/member_edit.html', {
        'form': form,
        'member': member,
    })
