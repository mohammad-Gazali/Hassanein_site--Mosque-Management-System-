from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_specialization, name='specializations_main'),
    path('level/ajax', views.levels_ajax, name='specializations_levels_ajax'),
    path('part/ajax', views.parts_ajax, name='specializations_parts_ajax'),
]
