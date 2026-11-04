from django.test import TestCase, override_settings
from datetime import date, timedelta
from .models import HeroSlide, Sermon, SermonSeries, Ministry, ServiceTime, Event, AboutPage, WartaJemaat, Album, Topic


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
        faith = Topic.objects.create(name='Faith')
        family = Topic.objects.create(name='Family')
        Sermon.objects.create(
            title='Faith Talk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc', topic=faith
        )
        Sermon.objects.create(
            title='Family Life', pastor='P', date=date(2025, 2, 1),
            description='', youtube_url='https://youtube.com/watch?v=xyz', topic=family
        )
        response = self.client.get(reverse('website:sermon_list') + f'?topic={faith.pk}')
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


class SermonYoutubeOptionalTest(TestCase):
    def test_youtube_url_can_be_blank(self):
        sermon = Sermon(
            title='No Video Sermon', pastor='P', date=date(2025, 1, 1),
            description='A sermon without video', youtube_url='', thumbnail='sermons/test.jpg'
        )
        sermon.full_clean()


class SermonDetailImageFallbackTest(TestCase):
    def test_shows_thumbnail_when_no_youtube_url(self):
        sermon = Sermon.objects.create(
            title='Photo Only Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='', thumbnail='sermons/test.jpg'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertContains(response, 'sermon-detail__img')
        self.assertNotContains(response, 'yt-iframe')

    def test_shows_video_when_youtube_url_present(self):
        sermon = Sermon.objects.create(
            title='Video Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc',
            thumbnail='sermons/test.jpg'
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertContains(response, 'yt-iframe')
        self.assertNotContains(response, 'sermon-detail__img')

    def test_shows_neither_when_no_video_and_no_thumbnail(self):
        sermon = Sermon.objects.create(
            title='Text Only Sermon', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url=''
        )
        response = self.client.get(
            reverse('website:sermon_detail', kwargs={'slug': sermon.slug})
        )
        self.assertNotContains(response, 'yt-iframe')
        self.assertNotContains(response, 'sermon-detail__img')


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

    def test_footer_shows_all_campuses(self):
        for name in ['GKJ Salatiga', 'Pepanthan Gedong', 'Pepanthan Kayu Wangi']:
            ServiceTime.objects.create(
                campus_name=name, address=f'Alamat {name}', times='Minggu 07:00',
                link_label='Info', link_url='/'
            )
        response = self.client.get(reverse('website:home'))
        for name in ['GKJ Salatiga', 'Pepanthan Gedong', 'Pepanthan Kayu Wangi']:
            self.assertContains(response, f'Alamat {name}')


class AboutContactCTATest(TestCase):
    def test_about_page_has_contact_cta(self):
        AboutPage.objects.create(
            mission_statement='Komunitas iman.',
        )
        response = self.client.get(reverse('website:about'))
        self.assertContains(response, 'Jam &amp; Lokasi')
        self.assertContains(response, 'Hubungi Kami')


class EventsMapsLinkTest(TestCase):
    def test_event_location_is_maps_link(self):
        Event.objects.create(
            title='Kebaktian Natal', date=date.today() + timedelta(days=30),
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
        faith = Topic.objects.create(name='Faith')
        family = Topic.objects.create(name='Family')
        Sermon.objects.create(
            title='Family Talk', pastor='P', date=date(2025, 1, 1),
            description='', youtube_url='https://youtube.com/watch?v=abc',
            topic=family
        )
        response = self.client.get(reverse('website:sermon_list') + f'?topic={faith.pk}')
        self.assertContains(response, 'Lihat Semua Khotbah')

    def test_gallery_empty_state_shown(self):
        response = self.client.get(reverse('website:gallery'))
        self.assertContains(response, 'Belum ada foto yang tersedia')


class ParagraphsFilterTest(TestCase):
    def test_plain_text_lines_become_paragraphs(self):
        from website.templatetags.safe_html import paragraphs
        self.assertEqual(
            paragraphs('First line.\r\nSecond line.\r\n\r\nThird.'),
            '<p>First line.</p><p>Second line.</p><p>Third.</p>',
        )

    def test_plain_text_is_escaped(self):
        from website.templatetags.safe_html import paragraphs
        self.assertEqual(paragraphs('a < b & c'), '<p>a &lt; b &amp; c</p>')

    def test_html_is_sanitised_not_rewrapped(self):
        from website.templatetags.safe_html import paragraphs
        self.assertEqual(
            paragraphs('<p>Hi</p><script>x</script>'),
            '<p>Hi</p>x',
        )

    def test_about_page_renders_bio_paragraphs(self):
        from website.models import Pendeta
        page = AboutPage.objects.create(mission_statement='<p>Visi</p>')
        Pendeta.objects.create(page=page, nama='Pdt. A', bio='Para one.\nPara two.')
        response = self.client.get(reverse('website:about'))
        self.assertContains(response, '<p>Para one.</p><p>Para two.</p>', html=False)


class BeritaAndPastEventsTest(TestCase):
    def setUp(self):
        today = date.today()
        self.past = Event.objects.create(
            title='Bazar Lalu', date=today - timedelta(days=10), time='09:00',
            location='Gedung', description='x'
        )
        self.future = Event.objects.create(
            title='Retret Nanti', date=today + timedelta(days=10), time='09:00',
            location='Gedung', description='x'
        )

    def test_home_shows_only_upcoming_events(self):
        response = self.client.get(reverse('website:home'))
        self.assertEqual(list(response.context['upcoming_events']), [self.future])

    def test_events_page_splits_upcoming_and_past(self):
        response = self.client.get(reverse('website:event_list'))
        self.assertEqual(list(response.context['events']), [self.future])
        self.assertEqual(list(response.context['past_events']), [self.past])

    def test_past_event_links_to_its_report(self):
        report = WartaJemaat.objects.create(
            title='Laporan Bazar', date=date.today(), category='berita', event=self.past
        )
        response = self.client.get(reverse('website:event_list'))
        self.assertContains(response, reverse('website:warta_detail', args=[report.slug]))
        self.assertContains(response, 'Baca Laporan')

    def test_home_feed_shows_only_berita(self):
        WartaJemaat.objects.create(title='Cerita Bazar', date=date.today(), category='berita')
        WartaJemaat.objects.create(title='Tata Ibadah', date=date.today(), category='liturgi')
        response = self.client.get(reverse('website:home'))
        self.assertEqual([w.title for w in response.context['latest_news']], ['Cerita Bazar'])
        self.assertEqual([w.title for w in response.context['weekly_docs']], ['Tata Ibadah'])

    def test_report_page_links_to_album(self):
        album = Album.objects.create(title='Foto Bazar', date=date.today(), cover_image='')
        report = WartaJemaat.objects.create(
            title='Laporan', date=date.today(), category='berita', event=self.past, album=album
        )
        response = self.client.get(reverse('website:warta_detail', args=[report.slug]))
        self.assertContains(response, 'Lihat Galeri Foto')
        self.assertContains(response, reverse('website:album_detail', args=[album.slug]))


class HomeMinistriesTest(TestCase):
    def make(self, n, **kwargs):
        return [Ministry.objects.create(name=f'Pelayanan {i}', description='x', order=i, **kwargs)
                for i in range(n)]

    def test_home_falls_back_to_first_six_by_order(self):
        self.make(8)
        response = self.client.get(reverse('website:home'))
        self.assertEqual([m.name for m in response.context['ministries']],
                         [f'Pelayanan {i}' for i in range(6)])
        self.assertContains(response, 'Lihat Semua Komisi (8)')

    def test_home_shows_only_ticked_ministries(self):
        ms = self.make(8)
        for m in (ms[7], ms[3]):
            m.show_on_home = True
            m.save()
        response = self.client.get(reverse('website:home'))
        self.assertEqual([m.name for m in response.context['ministries']], ['Pelayanan 3', 'Pelayanan 7'])

    def test_home_caps_ticked_at_six(self):
        self.make(9, show_on_home=True)
        response = self.client.get(reverse('website:home'))
        self.assertEqual(len(response.context['ministries']), 6)

    def test_no_see_all_button_when_everything_fits(self):
        self.make(4)
        response = self.client.get(reverse('website:home'))
        self.assertNotContains(response, 'Lihat Semua Komisi')

    def test_ministry_page_lists_all(self):
        self.make(9)
        response = self.client.get(reverse('website:ministry_list'))
        self.assertEqual(len(response.context['ministries']), 9)
        self.assertContains(response, 'Pelayanan 8')

    def test_cards_link_to_ministry_page(self):
        m = Ministry.objects.create(name='Diakonia', description='Singkat.')
        response = self.client.get(reverse('website:home'))
        self.assertContains(response, reverse('website:ministry_detail', args=[m.pk]))

    def test_ministry_page_shows_full_description_as_paragraphs(self):
        m = Ministry.objects.create(name='Diakonia', description='Paragraf satu.\nParagraf dua.')
        response = self.client.get(reverse('website:ministry_detail', args=[m.pk]))
        self.assertContains(response, '<p>Paragraf satu.</p><p>Paragraf dua.</p>', html=False)

    def test_unknown_ministry_is_404(self):
        response = self.client.get(reverse('website:ministry_detail', args=[999]))
        self.assertEqual(response.status_code, 404)


class ContactPageTest(TestCase):
    def test_contact_page_has_no_message_form(self):
        response = self.client.get(reverse('website:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<form')
        self.assertContains(response, 'wa.me/')

    def test_posting_does_not_save_a_message(self):
        from website.models import ContactMessage
        self.client.post(reverse('website:contact'), {
            'name': 'A', 'email': 'a@example.com', 'message_type': 'general', 'message': 'Halo',
        })
        self.assertEqual(ContactMessage.objects.count(), 0)


class BacaanHarianTest(TestCase):
    def test_sabda_url_normalises_reference(self):
        from .models import sabda_url
        base = 'https://alkitab.sabda.org/passage.php?passage='
        self.assertEqual(sabda_url('Yohanes 1: (1-9), 10-18'), base + 'Yohanes%201:1-9,10-18')
        self.assertEqual(sabda_url('Kisah Pr. Rasul 2:14a, 22-32'), base + 'Kisah%20Para%20Rasul%202:14,22-32')
        self.assertEqual(sabda_url('Keluaran 3:16-22, 4:18-20'), base + 'Keluaran%203:16-22;4:18-20')
        self.assertEqual(sabda_url('3 Yohanes 9-12'), base + '3%20Yohanes%201:9-12')

    def test_readings_split_alternatives_and_skip_empty(self):
        from .models import BacaanHarian
        b = BacaanHarian(
            tanggal=date(2026, 4, 3), tanggapan='Mazmur 22',
            bacaan_2='Ibrani 10:16-25 atau Ibrani 4:14-16; 5:7-9', injil='Yohanes 18:1-19:42',
        )
        readings = b.readings()
        # Tanggapan is not shown; empty Bacaan I is skipped
        self.assertEqual([label for label, _ in readings], ['Bacaan II', 'Injil'])
        self.assertEqual([ref for ref, _ in readings[0][1]], ['Ibrani 10:16-25', 'Ibrani 4:14-16; 5:7-9'])

    def test_week_page_shows_monday_to_sunday(self):
        from .models import BacaanHarian, TemaBulan
        BacaanHarian.objects.create(tanggal=date(2026, 11, 2), bacaan_1='Yeremia 5:18-31')
        BacaanHarian.objects.create(tanggal=date(2026, 11, 8), keterangan='Minggu Biasa', injil='Matius 25:1-13')
        TemaBulan.objects.create(tahun=2026, bulan=11, tema='Tuhan Tidak Akan Terlambat')
        response = self.client.get('/bacaan/?minggu=2026-11-04')
        self.assertEqual(response.status_code, 200)
        days = response.context['days']
        self.assertEqual([d['hari'] for d in days][0::6], ['Senin', 'Minggu'])
        self.assertEqual(days[0]['date'], date(2026, 11, 2))
        self.assertContains(response, 'Yeremia 5:18-31')
        self.assertContains(response, 'Matius 25:1-13')
        self.assertContains(response, 'Tuhan Tidak Akan Terlambat')

    def test_week_page_without_data_and_bad_param(self):
        response = self.client.get('/bacaan/?minggu=not-a-date')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'belum tersedia')

    def test_import_command_is_repeatable(self):
        import os
        import tempfile
        from io import StringIO
        from django.core.management import call_command
        from .models import BacaanHarian, TemaBulan
        with tempfile.TemporaryDirectory() as tmp:
            bacaan_csv = os.path.join(tmp, 'b.csv')
            tema_csv = os.path.join(tmp, 't.csv')
            with open(bacaan_csv, 'w', encoding='utf-8') as f:
                f.write('tanggal,urutan,keterangan,warna,bacaan_1,tanggapan,bacaan_2,injil,tema\n'
                        '2026-04-05,0,Minggu Paskah,Putih,Yeremia 31:1-6,Mazmur 118,,,\n'
                        '2026-04-05,1,Paskah Sore,Putih,Yesaya 25:6-9,Mazmur 114,,,\n')
            with open(tema_csv, 'w', encoding='utf-8') as f:
                f.write('tahun,bulan,tema,keterangan\n2026,4,Mengikuti Jejak,\n')
            call_command('import_bacaan', bacaan_csv, tema_bulan=tema_csv, stdout=StringIO())
            call_command('import_bacaan', bacaan_csv, tema_bulan=tema_csv, stdout=StringIO())
        self.assertEqual(BacaanHarian.objects.count(), 2)
        self.assertEqual(TemaBulan.objects.count(), 1)
        self.assertEqual(BacaanHarian.objects.last().keterangan, 'Paskah Sore')


class SeoTest(TestCase):
    def test_robots_txt_blocks_staff_areas_and_points_to_sitemap(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'Disallow: /members/')
        self.assertContains(response, 'Sitemap: https://gkjsalatiga.org/sitemap.xml')

    @override_settings(ALLOWED_HOSTS=['www.gkjsalatiga.org'])
    def test_sitemap_lists_published_content_on_site_url(self):
        Sermon.objects.create(title='Iman', pastor='P', date=date(2026, 11, 1), description='x')
        WartaJemaat.objects.create(title='Draft', date=date(2026, 11, 1), is_published=False)
        response = self.client.get('/sitemap.xml', HTTP_HOST='www.gkjsalatiga.org')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<loc>https://gkjsalatiga.org/sermons/iman-2026-11-01/</loc>')
        self.assertContains(response, '<loc>https://gkjsalatiga.org/bacaan/</loc>')
        self.assertNotContains(response, 'draft')
        self.assertNotContains(response, 'www.gkjsalatiga.org')

    def test_home_head_tags(self):
        response = self.client.get('/')
        self.assertContains(response, '<html lang="id">')
        self.assertContains(response, '<link rel="canonical" href="https://gkjsalatiga.org/">')
        self.assertContains(response, '<meta property="og:image" content="https://gkjsalatiga.org/static/images/logo.png">')
        self.assertContains(response, '"@type": "Church"')

    def test_detail_page_uses_its_own_description_fallback(self):
        WartaJemaat.objects.create(title='Warta Minggu', date=date(2026, 11, 1), content='')
        response = self.client.get('/warta/warta-minggu-2026-11-01/')
        self.assertContains(response, '<meta name="description" content="Warta Minggu — GKJ Salatiga.">')
