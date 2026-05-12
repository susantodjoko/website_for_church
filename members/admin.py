from django.contrib import admin
from .models import (
    Keluarga, Member, Majelis,
    IbadahMingguan, IbadahService,
    Perpuluhan, IuranPralenan, MemberStatusHistory
)


class IbadahServiceInline(admin.TabularInline):
    model = IbadahService
    extra = 1


@admin.register(IbadahMingguan)
class IbadahMingguanAdmin(admin.ModelAdmin):
    list_display = ['tanggal', 'minggu_ke']
    inlines = [IbadahServiceInline]


@admin.register(Keluarga)
class KeluargaAdmin(admin.ModelAdmin):
    list_display = ['nama_keluarga', 'blok', 'no_kk_gereja']
    list_filter = ['blok']
    search_fields = ['nama_keluarga']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['nama_lengkap', 'kewargaan', 'jenis_kelamin', 'tanggal_lahir']
    search_fields = ['nama_lengkap', 'no_sensus']
    list_filter = ['kewargaan', 'jenis_kelamin', 'sudah_baptis', 'sudah_sidi']


@admin.register(Majelis)
class MajelisAdmin(admin.ModelAdmin):
    list_display = ['member', 'jabatan', 'aktif']
    list_filter = ['jabatan', 'aktif']


@admin.register(Perpuluhan)
class PerpuluhanAdmin(admin.ModelAdmin):
    list_display = ['member', 'tanggal', 'jumlah']
    search_fields = ['member__nama_lengkap']


@admin.register(IuranPralenan)
class IuranPralenanAdmin(admin.ModelAdmin):
    list_display = ['member', 'tanggal', 'jumlah']
    search_fields = ['member__nama_lengkap']


@admin.register(MemberStatusHistory)
class MemberStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'status_lama', 'status_baru', 'tanggal']
