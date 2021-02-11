from django.contrib import admin

from .models import Session

# Register your models here.


class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "season",
        "year",
    )
    ordering = (
        "id",
        "year",
    )
    search_fields = (
        "season",
        "year",
    )
    list_filter = (
        "season",
        "year",
    )


admin.site.register(Session, SessionAdmin)
