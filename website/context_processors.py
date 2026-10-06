from .models import ServiceTime


def service_times(request):
    return {'footer_service_times': ServiceTime.objects.order_by('id')}
