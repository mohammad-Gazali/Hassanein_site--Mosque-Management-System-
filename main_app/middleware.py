# my middleware for make sure that ControlSettings Instance with pk=1 is exist

from .models import ControlSettings

class ControlSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        
        if not ControlSettings.objects.filter(pk=1):
            ControlSettings.objects.create(point_value=10)

        response = self.get_response(request)

        return response