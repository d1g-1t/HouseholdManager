from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from apps.users.api import auth

from .models import Family, FamilyMember, FamilyRole
from .schemas import (
    FamilyCreateSchema,
    FamilyDetailSchema,
    FamilyResponseSchema,
    FamilyUpdateSchema,
    JoinFamilySchema,
    UpdateMemberRoleSchema,
)

router = Router()


def _serialize_family(family, include_members: bool = True):
    data = {
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

    if include_members:
        data["members"] = [
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
        ]

    return data


def _get_family_queryset():
    return Family.objects.annotate(
        members_count=Count("members", filter=Q(members__is_active=True))
    ).select_related("owner").prefetch_related("members__user")


@router.get("/", response=list[FamilyResponseSchema], auth=auth)
def list_families(request):
    user = request.auth

    families = Family.objects.filter(
        Q(owner=user) | Q(members__user=user, members__is_active=True)
    ).annotate(
        members_count=Count("members", filter=Q(members__is_active=True))
    ).distinct().select_related("owner")

    return [_serialize_family(f, include_members=False) for f in families]


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

    family = _get_family_queryset().get(id=family.id)
    return _serialize_family(family)


@router.get("/{family_id}", response=FamilyDetailSchema, auth=auth)
def get_family(request, family_id: UUID):
    user = request.auth

    family = get_object_or_404(
        _get_family_queryset(),
        Q(id=family_id) & (Q(owner=user) | Q(members__user=user, members__is_active=True))
    )

    return _serialize_family(family)


@router.patch("/{family_id}", response=FamilyDetailSchema, auth=auth)
def update_family(request, family_id: UUID, payload: FamilyUpdateSchema):
    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(family, attr, value)

    family.save()

    family = _get_family_queryset().get(id=family.id)
    return _serialize_family(family)


@router.post("/join", response=FamilyDetailSchema, auth=auth)
def join_family(request, payload: JoinFamilySchema):
    user = request.auth

    family = get_object_or_404(Family, invite_code=payload.invite_code)

    if FamilyMember.objects.filter(family=family, user=user).exists():
        raise HttpError(400, "You are already a member of this family")

    with transaction.atomic():
        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyRole.MEMBER,
        )

    family = _get_family_queryset().get(id=family.id)
    return _serialize_family(family)


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
        raise HttpError(400, "Cannot change owner role")

    member.role = payload.role
    member.save()

    return {"detail": "Member role updated successfully"}


@router.delete("/{family_id}/members/{member_id}", auth=auth)
def remove_member(request, family_id: UUID, member_id: UUID):
    user = request.auth

    family = get_object_or_404(Family, id=family_id, owner=user)
    member = get_object_or_404(FamilyMember, id=member_id, family=family)

    if member.user == family.owner:
        raise HttpError(400, "Cannot remove owner")

    member.is_active = False
    member.save()

    return {"detail": "Member removed successfully"}


@router.post("/{family_id}/leave", auth=auth)
def leave_family(request, family_id: UUID):
    user = request.auth

    family = get_object_or_404(Family, id=family_id)

    if family.owner == user:
        raise HttpError(400, "Owner cannot leave family. Transfer ownership or delete the family.")

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
