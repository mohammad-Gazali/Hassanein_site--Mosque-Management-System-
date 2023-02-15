from django.contrib import admin
from . import models


@admin.register(models.Specialization)
class AdminSpecialization(admin.ModelAdmin):
    pass


@admin.register(models.Level)
class AdminLevel(admin.ModelAdmin):
    list_display = ['__str__', 'content']
    list_select_related = ['specialization']
    list_filter = ['specialization']


@admin.register(models.Part)
class AdminPart(admin.ModelAdmin):
    list_display = ['__str__', 'part_start', 'part_end']
    list_filter = ['level__specialization']
    list_select_related = ['level__specialization']
    readonly_fields = ['students']


@admin.register(models.SpecializationMessage)
class AdminSpecializationMessage(admin.ModelAdmin):
    list_display = ['student', 'part', 'master_name', 'created_at']
    list_filter = ['master_name']
    list_select_related = ['student', 'part', 'master_name__user']


    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False