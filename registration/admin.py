from django.contrib import admin

from .models import Family, Student


class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "parent",
        "email",
        "phone_number",
        "address",
    )
    ordering = ("-id",)
    search_fields = (
        "parent__first_name",
        "parent__last_name",
        "email",
        "phone_number",
        "address",
    )
    list_filter = ("preferred_comms",)


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
        "role",
    )


admin.site.register(Family, FamilyAdmin)
admin.site.register(Student, StudentAdmin)
