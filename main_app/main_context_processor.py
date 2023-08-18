def hs_website(request):
    groups = list(map(lambda x: x.name, request.user.groups.all()))

    return {
        "groups": groups,
    }
