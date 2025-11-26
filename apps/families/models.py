import secrets
import string
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

def generate_invite_code():

    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

class Family(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("family name"), max_length=150)
    description = models.TextField(_("description"), blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_families",
        verbose_name=_("owner"),
    )
    invite_code = models.CharField(
        _("invite code"),
        max_length=8,
        unique=True,
        default=generate_invite_code,
        db_index=True,
    )
    invite_code_expires_at = models.DateTimeField(
        _("invite code expires at"),
        blank=True,
        null=True,
    )
    currency = models.CharField(_("currency"), max_length=3, default="RUB")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "families"
        verbose_name = _("family")
        verbose_name_plural = _("families")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["invite_code"], name="idx_family_invite"),
            models.Index(fields=["created_at"], name="idx_family_created"),
        ]

    def __str__(self):
        return self.name

    def regenerate_invite_code(self):

        self.invite_code = generate_invite_code()
        self.save(update_fields=["invite_code", "updated_at"])

class FamilyRole(models.TextChoices):

    OWNER = "owner", _("Owner")
    MEMBER = "member", _("Member")
    VIEWER = "viewer", _("Viewer")

class FamilyMember(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("family"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_memberships",
        verbose_name=_("user"),
    )
    role = models.CharField(
        _("role"),
        max_length=10,
        choices=FamilyRole.choices,
        default=FamilyRole.MEMBER,
    )
    is_active = models.BooleanField(_("is active"), default=True)

    joined_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "family_members"
        verbose_name = _("family member")
        verbose_name_plural = _("family members")
        unique_together = [["family", "user"]]
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["family", "user"], name="idx_family_user"),
            models.Index(fields=["user", "is_active"], name="idx_user_active"),
            models.Index(fields=["joined_at"], name="idx_member_joined"),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} in {self.family.name} ({self.role})"

    def has_permission(self, permission: str) -> bool:

        permissions_map = {
            FamilyRole.OWNER: ["view", "add", "edit", "delete", "manage"],
            FamilyRole.MEMBER: ["view", "add", "edit"],
            FamilyRole.VIEWER: ["view"],
        }
        return permission in permissions_map.get(self.role, [])
