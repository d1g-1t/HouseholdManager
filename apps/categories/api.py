from typing import List
from uuid import UUID

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.families.models import Family, FamilyMember
from apps.users.api import auth

from .models import Category
from .schemas import CategoryCreateSchema, CategoryResponseSchema, CategoryUpdateSchema

router = Router()

@router.get("/family/{family_id}", response=List[CategoryResponseSchema], auth=auth)
def list_categories(request, family_id: UUID):

    user = request.auth

    get_object_or_404(FamilyMember, family_id=family_id, user=user, is_active=True)

    categories = Category.objects.filter(family_id=family_id).order_by("type", "name")
    return list(categories)

@router.post("/family/{family_id}", response=CategoryResponseSchema, auth=auth)
def create_category(request, family_id: UUID, payload: CategoryCreateSchema):

    user = request.auth

    member = get_object_or_404(FamilyMember, family_id=family_id, user=user, is_active=True)

    if not member.has_permission("add"):
        return router.create_response(
            request,
            {"detail": "You don't have permission to add categories"},
            status=403,
        )

    category = Category.objects.create(
        name=payload.name,
        type=payload.type,
        color=payload.color,
        icon=payload.icon or "",
        family_id=family_id,
        created_by=user,
    )

    return category

@router.get("/defaults", response=List[CategoryResponseSchema], auth=auth)
def list_default_categories(request):

    categories = Category.objects.filter(is_default=True).order_by("type", "name")
    return list(categories)
