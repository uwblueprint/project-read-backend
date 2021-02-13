from django.contrib import admin

from .models import Class

class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    ordering = ("-id")
    search_fields = (
        "name"
    )

admin.site.register(Family, FamilyAdmin)
