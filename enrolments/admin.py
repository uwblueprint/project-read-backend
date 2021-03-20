from django.contrib import admin
from .models import Class, Session, Enrolment


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


class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "attendance",
    )
    ordering = ("-id",)
    search_fields = ("name",)


class EnrolmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "active",
        "family",
        "session",
        "created_at",
        "updated_at",
        "preferred_class",
        "enrolled_class",
    )

    ordering = ("-id",)

    search_fields = ("family__id", "family__email", "enrolled_class__name")


admin.site.register(Session, SessionAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Enrolment, EnrolmentAdmin)
