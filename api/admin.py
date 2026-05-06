from django.contrib import admin

from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_active", "last_used_at", "created_at")
    search_fields = ("name", "user__email")
    readonly_fields = ("key", "last_used_at", "created_at")
