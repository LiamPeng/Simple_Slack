from django.contrib import admin

from .models import AppUser


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "username",
        "email",
        "nickname",
        "is_staff",
        "is_superuser",
        "is_active",
        "created_at",
    )
    search_fields = ("username", "email", "nickname")
    list_filter = ("is_staff", "is_superuser", "is_active", "created_at")
    ordering = ("user_id",)
    readonly_fields = ("user_id", "created_at", "last_login")

