from django.urls import path
from specializations import views


urlpatterns = [
    path("", views.main_specialization, name="specializations_main"),
    path("subject/ajax", views.subjects_ajax, name="specializations_subjects_ajax"),
    path("part/ajax", views.parts_ajax, name="specializations_parts_ajax"),
]
