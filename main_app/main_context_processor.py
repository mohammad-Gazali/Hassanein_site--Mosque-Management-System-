from django.http import HttpRequest

def hs_website(request: HttpRequest):
    groups = list(map(lambda x: x.name, request.user.groups.all()))

    return {
        "groups": groups,
    }
