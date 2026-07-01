from django.test import TestCase
from datetime import date
from .models import HeroSlide, Sermon, SermonSeries, Ministry, ServiceTime, Event, AboutPage, WartaJemaat, Album


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

from django.urls import reverse


class HomeViewTest(TestCase):
    def test_returns_200(self):
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)

    def test_uses_home_template(self):
        response = self.client.get(reverse('website:home'))
        self.assertTemplateUsed(response, 'website/home.html')


class SermonListViewTest(TestCase):
    def test_returns_200(self):
        response = self.client.get(reverse('website:sermon_list'))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_topic(self):
        from datetime import date
        Sermon.objects.create(
            title='Faith Talk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc', topic='faith'
        )
        Sermon.objects.create(
            title='Family Life', pastor='P', date=date(2025, 2, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz', topic='family'
        )
        response = self.client.get(reverse('website:sermon_list') + '?topic=faith')
        self.assertEqual(len(response.context['page'].object_list), 1)
        self.assertEqual(response.context['page'].object_list[0].title, 'Faith Talk')


class SermonTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        sermon = Sermon.objects.create(
            title='Test Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        self.assertIsNotNone(sermon.created_at)


class WartaTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        warta = WartaJemaat.objects.create(
            title='Test Warta', date=date(2025, 1, 1)
        )
        self.assertIsNotNone(warta.created_at)


class EventTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        event = Event.objects.create(
            title='Test Event', date=date(2025, 1, 1),
            time='09:00', location='Church', description='desc'
        )
        self.assertIsNotNone(event.created_at)


class AlbumTimestampTest(TestCase):
    def test_created_at_is_set_on_create(self):
        album = Album.objects.create(
            title='Test Album', date=date(2025, 1, 1), cover_image=''
        )
        self.assertIsNotNone(album.created_at)


class SermonSlugTest(TestCase):
    def test_slug_auto_generated_on_save(self):
        sermon = Sermon.objects.create(
            title='Walking by Faith', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        self.assertEqual(sermon.slug, 'walking-by-faith-2025-06-01')

    def test_duplicate_slugs_get_numeric_suffix(self):
        Sermon.objects.create(
            title='Same Title', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        s2 = Sermon.objects.create(
            title='Same Title', pastor='P', date=date(2025, 6, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz'
        )
        self.assertEqual(s2.slug, 'same-title-2025-06-01-1')


class WartaSlugTest(TestCase):
    def test_slug_auto_generated_on_save(self):
        warta = WartaJemaat.objects.create(
            title='Warta Minggu Ini', date=date(2025, 6, 1)
        )
        self.assertEqual(warta.slug, 'warta-minggu-ini-2025-06-01')


class AlbumSlugTest(TestCase):
    def test_slug_auto_generated_on_save(self):
        album = Album.objects.create(
            title='Foto Natal', date=date(2025, 12, 25), cover_image=''
        )
        self.assertEqual(album.slug, 'foto-natal-2025-12-25')


class SermonDetailSlugViewTest(TestCase):
    def test_detail_view_accessible_by_slug(self):
        sermon = Sermon.objects.create(
            title='Faith Walk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertEqual(response.status_code, 200)


class WartaDetailSlugViewTest(TestCase):
    def test_detail_view_accessible_by_slug(self):
        warta = WartaJemaat.objects.create(
            title='Warta Test', date=date(2025, 1, 1)
        )
        response = self.client.get(
            reverse('website:warta_detail', kwargs={'slug': warta.slug})
        )
        self.assertEqual(response.status_code, 200)


class AlbumDetailSlugViewTest(TestCase):
    def test_detail_view_accessible_by_slug(self):
        album = Album.objects.create(
            title='Foto Test', date=date(2025, 12, 25), cover_image=''
        )
        response = self.client.get(
            reverse('website:album_detail', kwargs={'slug': album.slug})
        )
        self.assertEqual(response.status_code, 200)


class SermonDetailRelatedTest(TestCase):
    def test_related_sermons_in_context(self):
        series = SermonSeries.objects.create(name='Test Series')
        s1 = Sermon.objects.create(
            title='Sermon One', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc',
            series=series
        )
        s2 = Sermon.objects.create(
            title='Sermon Two', pastor='P', date=date(2025, 2, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz',
            series=series
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': s1.slug})
        )
        self.assertIn(s2, response.context['related'])

    def test_related_excludes_current_sermon(self):
        series = SermonSeries.objects.create(name='Test Series')
        s1 = Sermon.objects.create(
            title='Solo Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc',
            series=series
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': s1.slug})
        )
        self.assertNotIn(s1, response.context['related'])

    def test_share_buttons_present(self):
        sermon = Sermon.objects.create(
            title='Faith Talk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertContains(response, 'wa.me')
        self.assertContains(response, 'Salin Tautan')


class FooterContextProcessorTest(TestCase):
    def test_footer_service_times_in_context(self):
        ServiceTime.objects.create(
            campus_name='Gedung Utama',
            address='Jl. Test No. 1, Salatiga',
            times='Minggu 08:00 & 10:00',
            link_label='Info',
            link_url='/'
        )
        response = self.client.get(reverse('website:home'))
        self.assertIn('footer_service_times', response.context)
        self.assertEqual(len(list(response.context['footer_service_times'])), 1)


class AboutContactCTATest(TestCase):
    def test_about_page_has_contact_cta(self):
        AboutPage.objects.create(
            mission_statement='Komunitas iman.',
            pastor_name='Pdt. Test',
            pastor_bio='Bio pendeta.'
        )
        response = self.client.get(reverse('website:about'))
        self.assertContains(response, 'Jam &amp; Lokasi')
        self.assertContains(response, 'Kirim Pesan')


class EventsMapsLinkTest(TestCase):
    def test_event_location_is_maps_link(self):
        Event.objects.create(
            title='Kebaktian Natal', date=date(2025, 12, 25),
            time='09:00', location='Gedung GKJ Salatiga',
            description='Ibadah natal bersama.'
        )
        response = self.client.get(reverse('website:event_list'))
        self.assertContains(response, 'maps.google.com')
        self.assertContains(response, 'Gedung GKJ Salatiga')


class EmptyStateTest(TestCase):
    def test_events_empty_state_has_contact_link(self):
        response = self.client.get(reverse('website:event_list'))
        self.assertContains(response, 'Hubungi Kami')

    def test_sermons_empty_state_has_back_link(self):
        Sermon.objects.create(
            title='Family Talk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc',
            topic='family'
        )
        response = self.client.get(reverse('website:sermon_list') + '?topic=faith')
        self.assertContains(response, 'Lihat Semua Khotbah')

    def test_gallery_empty_state_shown(self):
        response = self.client.get(reverse('website:gallery'))
        self.assertContains(response, 'Belum ada foto yang tersedia')
