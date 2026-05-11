from django.test import TestCase
from datetime import date
from .models import HeroSlide, Sermon, SermonSeries, Ministry, ServiceTime, Event, AboutPage


class HeroSlideModelTest(TestCase):
    def test_str_returns_headline(self):
        slide = HeroSlide(headline='Welcome to GKJ')
        self.assertEqual(str(slide), 'Welcome to GKJ')


class SermonModelTest(TestCase):
    def test_str_returns_title(self):
        sermon = Sermon(title='Walking by Faith')
        self.assertEqual(str(sermon), 'Walking by Faith')

    def test_ordered_newest_first(self):
        s1 = Sermon.objects.create(
            title='Old', pastor='P', date=date(2024, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        s2 = Sermon.objects.create(
            title='New', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz'
        )
        sermons = list(Sermon.objects.all())
        self.assertEqual(sermons[0], s2)
        self.assertEqual(sermons[1], s1)


class MinistryModelTest(TestCase):
    def test_ordered_by_order_field(self):
        m1 = Ministry.objects.create(name='Youth', description='', order=2)
        m2 = Ministry.objects.create(name='Worship', description='', order=1)
        ministries = list(Ministry.objects.all())
        self.assertEqual(ministries[0], m2)
        self.assertEqual(ministries[1], m1)


class AboutPageModelTest(TestCase):
    def test_str(self):
        about = AboutPage(mission_statement='Loving God')
        self.assertEqual(str(about), 'About Page')
