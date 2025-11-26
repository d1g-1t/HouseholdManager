from typing import List
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.users.api import auth

from .models import Family, FamilyMember, FamilyRole
from .schemas import (
    FamilyCreateSchema,
    FamilyDetailSchema,
    FamilyResponseSchema,
    FamilyUpdateSchema,
    JoinFamilySchema,
    RemoveMemberSchema,
    UpdateMemberRoleSchema,
)

router = Router()

@router.get("/", response=List[FamilyResponseSchema], auth=auth)
def list_families(request):

    user = request.auth

    families = Family.objects.filter(
        Q(owner=user) | Q(members__user=user, members__is_active=True)
    ).annotate(
        members_count=Count("members", filter=Q(members__is_active=True))
    ).distinct().select_related("owner")

    return [
        {
            "id": family.id,
            "name": family.name,
            "description": family.description,
            "owner_id": family.owner.id,
            "owner_email": family.owner.email,
            "invite_code": family.invite_code,
            "invite_code_expires_at": family.invite_code_expires_at,
            "currency": family.currency,
            "members_count": family.members_count,
            "created_at": family.created_at,
            "updated_at": family.updated_at,
        }
        for family in families
    ]

@router.post("/", response=FamilyDetailSchema, auth=auth)
def create_family(request, payload: FamilyCreateSchema):

    user = request.auth

    with transaction.atomic():
        family = Family.objects.create(
            name=payload.name,
            description=payload.description or "",
            owner=user,
            currency=payload.currency,
        )

        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyRole.OWNER,
        )

    family = Family.objects.annotate(
        members_count=Count("members", filter=Q(members__is_active=True))
    ).select_related("owner").prefetch_related("members__user").get(id=family.id)

    return {
        "id": family.id,
        "name": family.name,
        "description": family.description,
        "owner_id": family.owner.id,
        "owner_email": family.owner.email,
        "invite_code": family.invite_code,
        "invite_code_expires_at": family.invite_code_expires_at,
        "currency": family.currency,
        "members_count": family.members_count,
        "created_at": family.created_at,
        "updated_at": family.updated_at,
        "members": [
            {
                "id": member.id,
                "user_id": member.user.id,
                "user_email": member.user.email,
                "user_full_name": member.user.get_full_name(),
                "role": member.role,
                "is_active": member.is_active,
                "joined_at": member.joined_at,
            }
            for member in family.members.all()
        ],
    }

@router.get("/{family_id}", response=FamilyDetailSchema, auth=auth)
def get_family(request, family_id: UUID):

    user = request.auth

    family = get_object_or_404(
        Family.objects.annotate(
            members_count=Count("members", filter=Q(members__is_active=True))
        ).select_related("owner").prefetch_related("members__user"),
        Q(id=family_id) & (Q(owner=user) | Q(members__user=user, members__is_active=True))
    )

    return {
        "id": family.id,
        "name": family.name,
        "description": family.description,
        "owner_id": family.owner.id,
        "owner_email": family.owner.email,
        "invite_code": family.invite_code,
        "invite_code_expires_at": family.invite_code_expires_at,
        "currency": family.currency,
        "members_count": family.members_count,
        "created_at": family.created_at,
        "updated_at": family.updated_at,
        "members": [
            {
                "id": member.id,
                "user_id": member.user.id,
                "user_email": member.user.email,
                "user_full_name": member.user.get_full_name(),
                "role": member.role,
                "is_active": member.is_active,
                "joined_at": member.joined_at,
            }
            for member in family.members.filter(is_active=True)
        ],
    }

@router.patch("/{family_id}", response=FamilyDetailSchema, auth=auth)
def update_family(request, family_id: UUID, payload: FamilyUpdateSchema):

    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(family, attr, value)

    family.save()

    family = Family.objects.annotate(
        members_count=Count("members", filter=Q(members__is_active=True))
    ).select_related("owner").prefetch_related("members__user").get(id=family.id)

    return {
        "id": family.id,
        "name": family.name,
        "description": family.description,
        "owner_id": family.owner.id,
        "owner_email": family.owner.email,
        "invite_code": family.invite_code,
        "invite_code_expires_at": family.invite_code_expires_at,
        "currency": family.currency,
        "members_count": family.members_count,
        "created_at": family.created_at,
        "updated_at": family.updated_at,
        "members": [
            {
                "id": member.id,
                "user_id": member.user.id,
                "user_email": member.user.email,
                "user_full_name": member.user.get_full_name(),
                "role": member.role,
                "is_active": member.is_active,
                "joined_at": member.joined_at,
            }
            for member in family.members.filter(is_active=True)
        ],
    }

@router.post("/join", response=FamilyDetailSchema, auth=auth)
def join_family(request, payload: JoinFamilySchema):

    user = request.auth

    family = get_object_or_404(Family, invite_code=payload.invite_code)

    if FamilyMember.objects.filter(family=family, user=user).exists():
        return router.create_response(
            request,
            {"detail": "You are already a member of this family"},
            status=400,
        )

    with transaction.atomic():
        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyRole.MEMBER,
        )

    family = Family.objects.annotate(
        members_count=Count("members", filter=Q(members__is_active=True))
    ).select_related("owner").prefetch_related("members__user").get(id=family.id)

    return {
        "id": family.id,
        "name": family.name,
        "description": family.description,
        "owner_id": family.owner.id,
        "owner_email": family.owner.email,
        "invite_code": family.invite_code,
        "invite_code_expires_at": family.invite_code_expires_at,
        "currency": family.currency,
        "members_count": family.members_count,
        "created_at": family.created_at,
        "updated_at": family.updated_at,
        "members": [
            {
                "id": member.id,
                "user_id": member.user.id,
                "user_email": member.user.email,
                "user_full_name": member.user.get_full_name(),
                "role": member.role,
                "is_active": member.is_active,
                "joined_at": member.joined_at,
            }
            for member in family.members.filter(is_active=True)
        ],
    }

@router.post("/{family_id}/regenerate-invite", auth=auth)
def regenerate_invite_code(request, family_id: UUID):

    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)
    family.regenerate_invite_code()

    return {"invite_code": family.invite_code}

@router.patch("/{family_id}/members/{member_id}/role", auth=auth)
def update_member_role(request, family_id: UUID, member_id: UUID, payload: UpdateMemberRoleSchema):

    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)
    member = get_object_or_404(FamilyMember, id=member_id, family=family)

    if member.user == family.owner:
        return router.create_response(
            request,
            {"detail": "Cannot change owner role"},
            status=400,
        )

    member.role = payload.role
    member.save()

    return {"detail": "Member role updated successfully"}

@router.delete("/{family_id}/members/{member_id}", auth=auth)
def remove_member(request, family_id: UUID, member_id: UUID):

    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)
    member = get_object_or_404(FamilyMember, id=member_id, family=family)

    if member.user == family.owner:
        return router.create_response(
            request,
            {"detail": "Cannot remove owner"},
            status=400,
        )

    member.is_active = False
    member.save()

    return {"detail": "Member removed successfully"}

@router.post("/{family_id}/leave", auth=auth)
def leave_family(request, family_id: UUID):

    user = request.auth

    family = get_object_or_404(Family, id=family_id)

    if family.owner == user:
        return router.create_response(
            request,
            {"detail": "Owner cannot leave family. Transfer ownership or delete the family."},
            status=400,
        )

    member = get_object_or_404(FamilyMember, family=family, user=user, is_active=True)
    member.is_active = False
    member.save()

    return {"detail": "Successfully left the family"}

@router.delete("/{family_id}", auth=auth)
def delete_family(request, family_id: UUID):

    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)
    family.delete()

    return {"detail": "Family deleted successfully"}
