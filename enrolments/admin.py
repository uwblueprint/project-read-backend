from django.contrib import admin
from .models import Class
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


class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    ordering = ("-id",)
    search_fields = ("name",)


admin.site.register(Class, ClassAdmin)
from .models import Enrolment


class EnrolmentAdmin(admin.ModelAdmin):
    # add class once model is created
    list_display = ("id", "family")

    ordering = ("-id",)

    search_fields = ("family",)


admin.site.register(Enrolment, EnrolmentAdmin)
