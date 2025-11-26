import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.families.models import Family

class CategoryType(models.TextChoices):

    FOOD = "food", _("Food & Groceries")
    TRANSPORT = "transport", _("Transport")
    UTILITIES = "utilities", _("Utilities & Bills")
    ENTERTAINMENT = "entertainment", _("Entertainment")
    HEALTHCARE = "healthcare", _("Healthcare")
    EDUCATION = "education", _("Education")
    CLOTHING = "clothing", _("Clothing")
    HOUSING = "housing", _("Housing")
    OTHER = "other", _("Other")

class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("category name"), max_length=100)
    type = models.CharField(
        _("category type"),
        max_length=20,
        choices=CategoryType.choices,
        default=CategoryType.OTHER,
        db_index=True,
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name=_("family"),
        null=True,
        blank=True,
    )
    is_default = models.BooleanField(_("is default category"), default=False)
    color = models.CharField(_("color"), max_length=7, default="#808080")
    icon = models.CharField(_("icon"), max_length=50, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_categories",
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["type", "name"]
        unique_together = [["family", "name"]]
        indexes = [
            models.Index(fields=["family", "type"], name="idx_cat_family_type"),
            models.Index(fields=["type"], name="idx_cat_type"),
            models.Index(fields=["is_default"], name="idx_cat_default"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
