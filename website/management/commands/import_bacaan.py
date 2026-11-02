import csv
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from website.models import BacaanHarian, TemaBulan

READING_FIELDS = ['keterangan', 'warna', 'bacaan_1', 'tanggapan', 'bacaan_2', 'injil', 'tema']


class Command(BaseCommand):
    help = (
        'Import the Sinode GKJ daily Bible reading list from CSV '
        '(see scripts/bacaan/cells_to_csv.py). Replaces existing entries for '
        'the dates in the file, so it is safe to run again.'
    )

    def add_arguments(self, parser):
        parser.add_argument('bacaan_csv', help='e.g. website/data/bacaan_2026.csv')
        parser.add_argument('--tema-bulan', help='e.g. website/data/tema_bulan_2026.csv')

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options['bacaan_csv'], encoding='utf-8') as f:
            entries = [
                BacaanHarian(
                    tanggal=date.fromisoformat(row['tanggal']),
                    urutan=int(row['urutan']),
                    **{field: row[field] for field in READING_FIELDS},
                )
                for row in csv.DictReader(f)
            ]
        dates = {e.tanggal for e in entries}
        deleted, _ = BacaanHarian.objects.filter(tanggal__in=dates).delete()
        BacaanHarian.objects.bulk_create(entries)
        self.stdout.write(self.style.SUCCESS(
            f'{len(entries)} bacaan imported for {len(dates)} days ({deleted} replaced).'
        ))

        if options['tema_bulan']:
            with open(options['tema_bulan'], encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            for row in rows:
                TemaBulan.objects.update_or_create(
                    tahun=int(row['tahun']), bulan=int(row['bulan']),
                    defaults={'tema': row['tema'], 'keterangan': row['keterangan']},
                )
            self.stdout.write(self.style.SUCCESS(f'{len(rows)} tema bulan imported.'))
