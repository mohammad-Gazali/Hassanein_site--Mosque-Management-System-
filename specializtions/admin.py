from django.contrib import admin
from . import models


@admin.register(models.Specializtion)
class AdminSpecializtion(admin.ModelAdmin):
    pass


@admin.register(models.Level)
class AdminLevel(admin.ModelAdmin):
    list_select_related = ['specializtion']
    list_filter = ['specializtion']


@admin.register(models.Part)
class AdminPart(admin.ModelAdmin):
    list_display = ['__str__', 'part_start', 'part_end']
    list_filter = ['level__specializtion']
    list_select_related = ['level__specializtion']
    readonly_fields = ['students']