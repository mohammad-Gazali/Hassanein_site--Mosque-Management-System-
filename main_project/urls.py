from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main_app.urls")),
    path("accounts/", include("accounts.urls")),
    path("specializtions/", include("specializations.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
