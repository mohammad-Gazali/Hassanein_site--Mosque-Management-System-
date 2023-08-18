from django.contrib.auth.models import AbstractUser

def check_specializations(user: AbstractUser) -> bool:
    groups = map(lambda x: x.name, user.groups.all())
    return user.is_superuser or ("اختصاصات" in groups)