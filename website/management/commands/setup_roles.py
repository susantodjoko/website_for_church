from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from church_site.admin_sites import CONTENT_GROUP, MEMBERS_GROUP

CONTENT_MODELS = [
    'heroslide', 'sermonseries', 'sermon', 'ministry',
    'servicetime', 'event', 'aboutpage', 'aboutvalue', 'pendeta',
    'wartajemaat', 'album', 'photo', 'contactmessage',
]

MEMBERS_MODELS = [
    'keluarga', 'member', 'majelis',
    'ibadahmingguan', 'ibadahservice',
    'perpuluhan', 'iuranpralenan', 'memberstatushistory',
]


class Command(BaseCommand):
    help = 'Create Pengelola Konten and Staf Jemaat groups with correct permissions'

    def handle(self, *args, **options):
        self._setup_group(
            CONTENT_GROUP,
            app_label='website',
            models=CONTENT_MODELS,
        )
        self._setup_group(
            MEMBERS_GROUP,
            app_label='members',
            models=MEMBERS_MODELS,
        )
        self.stdout.write(self.style.SUCCESS('Groups and permissions configured.'))

    def _setup_group(self, group_name, app_label, models):
        group, created = Group.objects.get_or_create(name=group_name)
        perms = Permission.objects.filter(
            content_type__app_label=app_label,
            content_type__model__in=models,
        )
        group.permissions.set(perms)
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  {action} group "{group_name}" with {perms.count()} permissions.')
