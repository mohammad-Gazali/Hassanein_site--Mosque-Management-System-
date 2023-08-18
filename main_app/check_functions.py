from django.contrib.auth.models import AbstractUser

def check_admin(user: AbstractUser) -> bool:
    return user.is_superuser

def check_coming(user: AbstractUser) -> bool:
    groups = map(lambda x: x.name, user.groups.all())
    return user.is_superuser or ("حضور" in groups)

def check_adding_points(user: AbstractUser) -> bool:
    groups = map(lambda x: x.name, user.groups.all())
    return user.is_superuser or ("نقاط" in groups)