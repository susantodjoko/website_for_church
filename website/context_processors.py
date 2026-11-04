from .models import ServiceTime


def service_times(request):
    return {'footer_service_times': ServiceTime.objects.order_by('id')}


def seo(request):
    """Site address and default share image for the <head> tags in base.html."""
    from django.conf import settings
    from django.templatetags.static import static
    from .models import HeroSlide

    hero = HeroSlide.objects.filter(is_active=True).exclude(background_image='').first()
    image = hero.background_image.url if hero else static('images/logo.png')
    return {
        'site_url': settings.SITE_URL,
        'canonical_url': settings.SITE_URL + request.path,
        'default_share_image': settings.SITE_URL + image,
    }
