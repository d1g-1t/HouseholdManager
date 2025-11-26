from django.contrib import admin

from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ["name", "type", "family", "is_default", "color", "created_at"]
    list_filter = ["type", "is_default", "created_at"]
    search_fields = ["name", "family__name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("name", "type", "family", "is_default")}),
        ("Appearance", {"fields": ("color", "icon")}),
        ("Metadata", {"fields": ("created_by", "created_at", "updated_at")}),
    )
