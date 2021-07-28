from django.contrib import admin
from .models import Class, Session, Enrolment


class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "season",
        "start_date",
        "year",
    )
    ordering = (
        "id",
        "year",
    )
    search_fields = (
        "season",
        "year",
        "start_date",
    )
    list_filter = (
        "season",
        "year",
    )


class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
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
        "status",
        "preferred_class",
        "enrolled_class",
        "created_at",
        "updated_at",
    )

    ordering = ("-id",)

    search_fields = (
        "family__id",
        "family__email",
        "family__parent__first_name",
        "family__parent__last_name",
        "enrolled_class__name",
        "preferred_class__name",
    )

    list_filter = (
        "session",
        "status",
    )


admin.site.register(Session, SessionAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Enrolment, EnrolmentAdmin)
