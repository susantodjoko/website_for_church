from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'nama_lengkap', 'jenis_kelamin', 'tempat_lahir', 'tanggal_lahir',
            'nomor_telepon', 'status', 'kewargaan', 'ket_status',
            'gol_darah', 'pendidikan', 'pekerjaan', 'keluarga',
            'sudah_baptis', 'sudah_sidi', 'tanggal_wafat',
            'pelayanan_diikuti', 'ibadah_sering_diikuti',
        ]
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_wafat': forms.DateInput(attrs={'type': 'date'}),
            'pelayanan_diikuti': forms.Textarea(attrs={'rows': 3}),
            'ibadah_sering_diikuti': forms.Textarea(attrs={'rows': 3}),
        }


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='File CSV Sensus',
        help_text='File .csv dari Google Form Sensus Warga GKJ Salatiga',
    )
