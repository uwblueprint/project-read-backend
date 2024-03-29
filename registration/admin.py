from django.contrib import admin

from .models import Family, Student, Field
from safedelete.admin import SafeDeleteAdmin, highlight_deleted


class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "parent",
        "email",
        "home_number",
        "cell_number",
        "work_number",
        "preferred_number",
        "address",
        "created_at",
        "updated_at",
    )
    ordering = ("-id",)
    search_fields = (
        "parent__first_name",
        "parent__last_name",
        "email",
        "home_number",
        "cell_number",
        "work_number",
        "address",
    )
    list_filter = ("preferred_comms",)


class StudentAdmin(SafeDeleteAdmin):
    list_display = (
        highlight_deleted,
        "id",
        "first_name",
        "last_name",
        "family",
        "role",
        "created_at",
        "updated_at",
    ) + SafeDeleteAdmin.list_display
    ordering = (
        "id",
        "last_name",
        "first_name",
    )
    search_fields = (
        "first_name",
        "last_name",
        "family__parent__first_name",
        "family__parent__last_name",
    )
    list_filter = ("role",)


class FieldAdmin(SafeDeleteAdmin):
    list_display = (
        highlight_deleted,
        "id",
        "name",
        "role",
        "question_type",
        "is_default",
        "created_at",
        "updated_at",
    ) + SafeDeleteAdmin.list_display
    ordering = ("id", "order", "name")
    search_fields = ("name",)
    list_filter = (
        "role",
        "question_type",
        "is_default",
    )


admin.site.register(Family, FamilyAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Field, FieldAdmin)
