from django.http import HttpRequest
from django.conf import settings

def hs_website(request: HttpRequest):
    groups = list(map(lambda x: x.name, request.user.groups.all()))

    return {
        "groups": groups,
        "masjed_name": settings.MASJED_NAME
    }
