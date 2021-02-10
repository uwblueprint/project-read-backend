from django.contrib import admin

from .models import Family


class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "phone_number",
        "address",
    )
    ordering = (
        "id",
        "-created_at",
    )
    search_fields = (
        "email",
        "phone_number",
        "address",
    )
    list_filter = ("preferred_comms",)


admin.site.register(Family, FamilyAdmin)
