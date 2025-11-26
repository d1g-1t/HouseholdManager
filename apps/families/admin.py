from django.contrib import admin

from .models import Family, FamilyMember

class FamilyMemberInline(admin.TabularInline):

    model = FamilyMember
    extra = 0
    readonly_fields = ["joined_at"]
    fields = ["user", "role", "is_active", "joined_at"]

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):

    list_display = ["name", "owner", "invite_code", "currency", "created_at"]
    list_filter = ["currency", "created_at"]
    search_fields = ["name", "owner__email", "invite_code"]
    readonly_fields = ["invite_code", "created_at", "updated_at"]
    inlines = [FamilyMemberInline]

    fieldsets = (
        (None, {"fields": ("name", "description", "owner", "currency")}),
        ("Invitation", {"fields": ("invite_code", "invite_code_expires_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):

    list_display = ["user", "family", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active", "joined_at"]
    search_fields = ["user__email", "family__name"]
    readonly_fields = ["joined_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("family", "user", "role", "is_active")}),
        ("Timestamps", {"fields": ("joined_at", "updated_at")}),
    )
