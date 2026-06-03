from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

BLOK_CHOICES = [
    ('CK1', 'CK1'), ('CK2', 'CK2'), ('CK3', 'CK3'),
    ('GD1', 'GD1'), 
    ('JT1', 'JT1'), ('JT2', 'JT2'), ('JT3', 'JT3'),('JT4', 'JT4'),
    ('JB1', 'JB1'), ('JB2', 'JB2'),('JB3', 'JB3'),('JB4', 'JB4'),('JB5', 'JB5'),
    ('KM1', 'KM1'), ('KM2', 'KM2'),
    ('KM3', 'KM3'), ('KM4', 'KM4'),('KM5', 'KM5'),
    ('KY1', 'KY1'), ('KY2', 'KY2'), ('KY3', 'KY3'), ('KY4', 'KY4'), ('KY5', 'KY5'),
]


class Keluarga(models.Model):
    no_kk_gereja = models.CharField(max_length=20, unique=True)
    nama_keluarga = models.CharField(max_length=200)
    blok = models.CharField(max_length=10, choices=BLOK_CHOICES)
    alamat = models.TextField()

    class Meta:
        verbose_name_plural = 'Keluarga'
        ordering = ['nama_keluarga']

    def __str__(self):
        return f'{self.nama_keluarga} ({self.no_kk_gereja})'


class Member(models.Model):
    JENIS_KELAMIN = [('L', 'Laki-laki'), ('P', 'Perempuan')]
    STATUS_CHOICES = [('Dewasa', 'Dewasa'), ('Anak', 'Anak')]
    KEWARGAAN_CHOICES = [
        ('Warga', 'Warga'),
        ('Simpatisan', 'Simpatisan'),
        ('Titipan', 'Titipan'),
        ('Luar Kota', 'Luar Kota'),
        ('Meninggal', 'Meninggal'),
    ]
    GOL_DARAH = [('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ('-', 'Tidak Diketahui')]
    KET_STATUS = [
        ('KK', 'Kepala Keluarga'),
        ('Istri', 'Istri'),
        ('Anak', 'Anak'),
        ('Lainnya', 'Lainnya'),
    ]
    PENDIDIKAN_CHOICES = [
        ('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA'), ('D3', 'D3'),
        ('S1', 'S1'), ('S2', 'S2'), ('S3', 'S3'), ('Lainnya', 'Lainnya'),
    ]

    no_sensus = models.CharField(max_length=20, unique=True)
    nama_lengkap = models.CharField(max_length=200)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN)
    tempat_lahir = models.CharField(max_length=100, blank=True)
    tanggal_lahir = models.DateField(null=True, blank=True)
    nomor_telepon = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Dewasa')
    kewargaan = models.CharField(max_length=20, choices=KEWARGAAN_CHOICES, default='Warga')
    gol_darah = models.CharField(max_length=5, choices=GOL_DARAH, blank=True)
    pendidikan = models.CharField(max_length=10, choices=PENDIDIKAN_CHOICES, blank=True)
    pekerjaan = models.CharField(max_length=100, blank=True)
    ket_status = models.CharField(max_length=10, choices=KET_STATUS, blank=True)
    sudah_baptis = models.BooleanField(default=False)
    sudah_sidi = models.BooleanField(default=False)
    tanggal_wafat = models.DateField(null=True, blank=True)
    pelayanan_diikuti = models.TextField(blank=True)
    ibadah_sering_diikuti = models.TextField(blank=True)
    keluarga = models.ForeignKey(
        Keluarga, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='members'
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ['nama_lengkap']

    def __str__(self):
        return self.nama_lengkap


class Majelis(models.Model):
    JABATAN_CHOICES = [
        ('Pendeta', 'Pendeta'),
        ('Penatua', 'Penatua'),
        ('Diaken', 'Diaken'),
        ('Wiyata', 'Wiyata'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='majelis_records')
    jabatan = models.CharField(max_length=20, choices=JABATAN_CHOICES)
    periode_mulai = models.DateField()
    periode_selesai = models.DateField(null=True, blank=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Majelis'

    def __str__(self):
        return f'{self.member} — {self.jabatan}'


class IbadahMingguan(models.Model):
    tanggal = models.DateField(unique=True)
    minggu_ke = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Ibadah Mingguan'
        verbose_name_plural = 'Ibadah Mingguan'
        ordering = ['-tanggal']

    def __str__(self):
        return str(self.tanggal)


class IbadahService(models.Model):
    ibadah = models.ForeignKey(IbadahMingguan, on_delete=models.CASCADE, related_name='services')
    nama_service = models.CharField(max_length=100)
    jumlah_hadir = models.PositiveIntegerField(default=0)
    jumlah_persembahan = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.ibadah} — {self.nama_service}'


class Perpuluhan(models.Model):
    METODE = [('Tunai', 'Tunai'), ('Transfer', 'Transfer'), ('Lainnya', 'Lainnya')]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='perpuluhan')
    tanggal = models.DateField()
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=20, choices=METODE)
    keterangan = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Perpuluhan'
        ordering = ['-tanggal']

    def __str__(self):
        return f'{self.member} — {self.tanggal}'


class IuranPralenan(models.Model):
    METODE = [('Tunai', 'Tunai'), ('Transfer', 'Transfer'), ('Lainnya', 'Lainnya')]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='iuran_pralenan')
    tanggal = models.DateField()
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=20, choices=METODE)
    keterangan = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Iuran Pralenan'
        ordering = ['-tanggal']

    def __str__(self):
        return f'{self.member} — {self.tanggal}'


class MemberStatusHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='status_history')
    status_lama = models.CharField(max_length=20)
    status_baru = models.CharField(max_length=20)
    keterangan = models.TextField(blank=True)
    tanggal = models.DateField(auto_now_add=True)
    dicatat_oleh = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = 'Member Status History'
        ordering = ['-tanggal']

    def __str__(self):
        return f'{self.member} — {self.tanggal}'
