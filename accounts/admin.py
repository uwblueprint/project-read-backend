from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    ordering = ("email",)
    search_fields = ("email",)
    list_filter = (
        "is_staff",
        "is_active",
    )

    # Fields used on the view/edit user page
    fieldsets = (
        ("Personal info", {"fields": ("email", "first_name", "last_name", "password")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    # Fields used on the add user page
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                )
            },
        ),
    )


admin.site.register(User, UserAdmin)
