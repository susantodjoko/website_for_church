from django.db import models

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
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, blank=True)

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

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title


class AboutPage(models.Model):
    mission_statement = models.TextField()
    pastor_name = models.CharField(max_length=100)
    pastor_bio = models.TextField()
    pastor_photo = models.ImageField(upload_to='about/', blank=True)
    value_1_title = models.CharField(max_length=100)
    value_1_body = models.TextField()
    value_2_title = models.CharField(max_length=100)
    value_2_body = models.TextField()
    value_3_title = models.CharField(max_length=100)
    value_3_body = models.TextField()
    value_4_title = models.CharField(max_length=100)
    value_4_body = models.TextField()

    def __str__(self):
        return 'About Page'
    
class News(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title
