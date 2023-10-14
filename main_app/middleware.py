from main_app.models import ControlSettings
from django.contrib.auth.models import Group


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # checking the existance of ControlSettings instance
        if not ControlSettings.objects.first():
            ControlSettings.objects.create(point_value=10)

        # check the existance of the groups (حضور, نقاط, اختصاصات)
        if not Group.objects.filter(name="حضور"):
            Group.objects.create(name="حضور")

        if not Group.objects.filter(name="نقاط"):
            Group.objects.create(name="نقاط")

        if not Group.objects.filter(name="اختصاصات"):
            Group.objects.create(name="اختصاصات")

        if not Group.objects.filter(name="حديث"):
            Group.objects.create(name="حديث")

        if not Group.objects.filter(name="تسميع خارج الدورة"):
            Group.objects.create(name="تسميع خارج الدورة")

        response = self.get_response(request)

        return response
