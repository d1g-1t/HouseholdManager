from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ["email", "first_name", "last_name", "telegram_id", "is_active", "created_at"]
    list_filter = ["is_active", "is_staff", "is_superuser", "telegram_notifications_enabled", "email_notifications_enabled"]
    search_fields = ["email", "first_name", "last_name", "telegram_username"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone", "avatar")}),
        (_("Telegram"), {"fields": ("telegram_id", "telegram_username", "telegram_notifications_enabled")}),
        (_("Preferences"), {"fields": ("currency", "language", "email_notifications_enabled")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]
