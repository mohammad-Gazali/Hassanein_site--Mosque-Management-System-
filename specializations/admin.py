from django.contrib import admin
from specializations import models


@admin.register(models.Specialization)
class AdminSpecialization(admin.ModelAdmin):
    pass


@admin.register(models.Subject)
class AdminSubject(admin.ModelAdmin):
    list_display = ["name", "specialization"]
    list_select_related = ["specialization"]
    list_filter = ["specialization"]


@admin.register(models.Part)
class AdminPart(admin.ModelAdmin):
    list_display = ["__str__", "part_content", "points"]
    list_filter = ["subject__specialization"]
    list_select_related = ["subject__specialization"]
    ordering = ["subject__specialization", "subject", "part_number"]


@admin.register(models.SpecializationMessage)
class AdminSpecializationMessage(admin.ModelAdmin):
    list_display = ["student", "part", "master", "created_at"]
    list_filter = ["master"]
    list_select_related = ["student", "part", "master__user"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
