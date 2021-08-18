from django.contrib import admin
from .models import Class, Session, Enrolment


class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "start_date",
        "created_at",
        "updated_at",
    )
    ordering = ("id",)
    search_fields = (
        "name",
        "start_date",
    )


class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "name",
        "attendance",
        "created_at",
        "updated_at",
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
