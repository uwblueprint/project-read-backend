from django.contrib import admin

from .models import Family, FamilyInfo, ChildInfo
from .models import Student


class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "phone_number",
        "address",
    )
    ordering = ("-id",)
    search_fields = (
        "email",
        "phone_number",
        "address",
    )
    list_filter = ("preferred_comms",)


class FamilyInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "question",
    )
    ordering = ("-id",)
    search_fields = (
        "name",
        "question",
    )


class ChildInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "question",
    )
    ordering = ("-id",)
    search_fields = (
        "name",
        "question",
    )


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "family",
    )
    ordering = (
        "id",
        "last_name",
        "first_name",
    )
    search_fields = (
        "first_name",
        "last_name",
        "family",
    )
    list_filter = (
        "family",
        "attendee_type",
    )


admin.site.register(Family, FamilyAdmin)
admin.site.register(FamilyInfo, FamilyInfoAdmin)
admin.site.register(ChildInfo, ChildInfoAdmin)
admin.site.register(Student, StudentAdmin)
