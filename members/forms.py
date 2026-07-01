from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            # Data Pribadi
            'nama_lengkap', 'jenis_kelamin', 'tempat_lahir', 'tanggal_lahir',
            'gol_darah', 'status', 'status_perkawinan', 'pendidikan', 'pekerjaan',
            'nomor_telepon',
            # Alamat & Keluarga
            'alamat_domisili', 'alamat_ktp', 'blok', 'keluarga',
            'ket_status', 'status_rumah_tinggal',
            # Iman
            'kewargaan', 'tempat_kebaktian', 'nama_gereja_lain',
            'sudah_baptis', 'baptis_oleh', 'tanggal_baptis', 'tempat_baptis',
            'sudah_sidi', 'sidi_oleh', 'tanggal_sidi', 'tempat_sidi',
            'nikah_oleh', 'tanggal_nikah', 'tempat_nikah',
            # Pelayanan
            'minat_pelayanan_gerejawi', 'minat_pelayanan_umum',
            'pelayanan_diikuti', 'ibadah_sering_diikuti',
            # Lainnya
            'tanggal_wafat',
        ]
        widgets = {
            'tanggal_lahir':            forms.DateInput(attrs={'type': 'date'}),
            'tanggal_baptis':           forms.DateInput(attrs={'type': 'date'}),
            'tanggal_sidi':             forms.DateInput(attrs={'type': 'date'}),
            'tanggal_nikah':            forms.DateInput(attrs={'type': 'date'}),
            'tanggal_wafat':            forms.DateInput(attrs={'type': 'date'}),
            'alamat_domisili':          forms.Textarea(attrs={'rows': 2}),
            'alamat_ktp':               forms.Textarea(attrs={'rows': 2}),
            'minat_pelayanan_gerejawi': forms.Textarea(attrs={'rows': 3}),
            'minat_pelayanan_umum':     forms.Textarea(attrs={'rows': 3}),
            'pelayanan_diikuti':        forms.Textarea(attrs={'rows': 3}),
            'ibadah_sering_diikuti':    forms.Textarea(attrs={'rows': 3}),
        }


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='File CSV Sensus',
        help_text='File .csv dari Google Form Sensus Warga GKJ Salatiga',
    )
