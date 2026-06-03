from django.db import models
from django.utils import timezone

# Create your models here.
class HeroSlide(models.Model):
    headline = models.CharField(max_length=200)
    subheadline = models.CharField(max_length=300)
    cta_primary_text = models.CharField(max_length=100)
    cta_primary_url = models.CharField(max_length=200)
    cta_secondary_text = models.CharField(max_length=100, blank=True)
    cta_secondary_url = models.CharField(max_length=200, blank=True)
    background_image = models.ImageField(upload_to='hero/', blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.headline


class SermonSeries(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='series/', blank=True)

    class Meta:
        verbose_name_plural = 'Sermon Series'

    def __str__(self):
        return self.name


class Sermon(models.Model):
    TOPIC_CHOICES = [
        ('faith', 'Faith'),
        ('family', 'Family'),
        ('purpose', 'Purpose'),
        ('prayer', 'Prayer'),
    ]

    title = models.CharField(max_length=200)
    series = models.ForeignKey(
        SermonSeries, null=True, blank=True, on_delete=models.SET_NULL
    )
    pastor = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    youtube_url = models.URLField()
    thumbnail = models.ImageField(upload_to='sermons/', blank=True)
    is_featured = models.BooleanField(default=False)
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Ministry(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='ministry/', blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Ministries'

    def __str__(self):
        return self.name


class ServiceTime(models.Model):
    campus_name = models.CharField(max_length=100)
    address = models.TextField()
    times = models.TextField()
    is_online = models.BooleanField(default=False)
    link_label = models.CharField(max_length=100)
    link_url = models.CharField(max_length=200)
    youtube_live_url = models.URLField(blank=True)
    is_live_now = models.BooleanField(default=False)

    def __str__(self):
        return self.campus_name


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True)
    registration_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title


class AboutPage(models.Model):
    mission_statement = models.TextField()
    pastor_name = models.CharField(max_length=100)
    pastor_bio = models.TextField()
    pastor_photo = models.ImageField(upload_to='about/', blank=True)

    def __str__(self):
        return 'About Page'


class AboutValue(models.Model):
    page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='values')
    title = models.CharField(max_length=100)
    body = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    

class WartaJemaat(models.Model):
    CATEGORY_CHOICES = [
        ('warta', 'Warta Mingguan'),
        ('pengumuman', 'Pengumuman'),
        ('liturgi', 'Liturgi'),
    ]

    title = models.CharField(max_length=200)
    date = models.DateField()
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='warta/', blank=True)
    pdf_file = models.FileField(upload_to='warta_pdf/', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='warta', db_index=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Warta Jemaat'

    def __str__(self):
        return f'{self.get_category_display()} — {self.title}'


class Album(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    cover_image = models.ImageField(upload_to='gallery/')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.caption or str(self.album)

class ContactMessage(models.Model):
    TYPE_CHOICES = [
        ('contact', 'Kontak Umum'),
        ('prayer', 'Permintaan Doa'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='contact')
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.name} — {self.get_message_type_display()}'
