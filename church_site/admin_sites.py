from django.contrib.admin import AdminSite

CONTENT_GROUP = 'Pengelola Konten'
MEMBERS_GROUP = 'Staf Jemaat'


class ContentAdminSite(AdminSite):
    site_header = 'GKJ Salatiga — Manajemen Konten'
    site_title = 'Konten Admin'
    index_title = 'Manajemen Konten'

    def has_permission(self, request):
        if not request.user.is_active or not request.user.is_staff:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name=CONTENT_GROUP).exists()


class MembersAdminSite(AdminSite):
    site_header = 'GKJ Salatiga — Manajemen Jemaat'
    site_title = 'Jemaat Admin'
    index_title = 'Manajemen Jemaat'

    def has_permission(self, request):
        if not request.user.is_active or not request.user.is_staff:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name=MEMBERS_GROUP).exists()


content_admin = ContentAdminSite(name='content_admin')
members_admin = MembersAdminSite(name='members_admin')
