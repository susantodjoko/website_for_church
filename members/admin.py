import csv
import io

from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from church_site.admin_sites import members_admin
from .forms import CsvImportForm
from .importers import import_sensus_rows
from .models import (
    Keluarga, Member, Majelis,
    IbadahMingguan, IbadahService,
    Perpuluhan, IuranPralenan, MemberStatusHistory,
)


class IbadahServiceInline(admin.TabularInline):
    model = IbadahService
    extra = 1


class IbadahMingguanAdmin(admin.ModelAdmin):
    list_display = ['tanggal', 'minggu_ke']
    inlines = [IbadahServiceInline]


class KeluargaAdmin(admin.ModelAdmin):
    list_display = ['nama_keluarga', 'blok', 'no_kk_gereja']
    list_filter = ['blok']
    search_fields = ['nama_keluarga']


class MemberAdmin(admin.ModelAdmin):
    list_display = ['nama_lengkap', 'kewargaan', 'jenis_kelamin', 'tanggal_lahir']
    search_fields = ['nama_lengkap', 'no_sensus']
    list_filter = ['kewargaan', 'jenis_kelamin', 'sudah_baptis', 'sudah_sidi']
    change_list_template = 'admin/members/member/changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'import-sensus/',
                self.admin_site.admin_view(self.import_sensus_view),
                name='members_member_import_sensus',
            ),
        ]
        return custom + urls

    def import_sensus_view(self, request):
        if request.method == 'POST':
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                decoded = csv_file.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(decoded))
                result = import_sensus_rows(list(reader))
                return render(
                    request,
                    'admin/members/member/import_result.html',
                    {'result': result, **self.admin_site.each_context(request)},
                )
        else:
            form = CsvImportForm()
        return render(
            request,
            'admin/members/member/import_sensus.html',
            {'form': form, **self.admin_site.each_context(request)},
        )


class MajelisAdmin(admin.ModelAdmin):
    list_display = ['member', 'jabatan', 'aktif']
    list_filter = ['jabatan', 'aktif']


class PerpuluhanAdmin(admin.ModelAdmin):
    list_display = ['member', 'tanggal', 'jumlah']
    search_fields = ['member__nama_lengkap']


class IuranPralenanAdmin(admin.ModelAdmin):
    list_display = ['member', 'tanggal', 'jumlah']
    search_fields = ['member__nama_lengkap']


class MemberStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'status_lama', 'status_baru', 'tanggal']


# ── Default admin site (superusers) ──────────────────────────────────────────
admin.site.register(IbadahMingguan, IbadahMingguanAdmin)
admin.site.register(Keluarga, KeluargaAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Majelis, MajelisAdmin)
admin.site.register(Perpuluhan, PerpuluhanAdmin)
admin.site.register(IuranPralenan, IuranPralenanAdmin)
admin.site.register(MemberStatusHistory, MemberStatusHistoryAdmin)

# ── Members admin site (member staff) ────────────────────────────────────────
members_admin.register(IbadahMingguan, IbadahMingguanAdmin)
members_admin.register(Keluarga, KeluargaAdmin)
members_admin.register(Member, MemberAdmin)
members_admin.register(Majelis, MajelisAdmin)
members_admin.register(Perpuluhan, PerpuluhanAdmin)
members_admin.register(IuranPralenan, IuranPralenanAdmin)
members_admin.register(MemberStatusHistory, MemberStatusHistoryAdmin)
