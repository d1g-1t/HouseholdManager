from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ninja import Schema
from pydantic import Field

class FamilyCreateSchema(Schema):

    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    currency: str = Field(default="RUB", min_length=3, max_length=3)

class FamilyUpdateSchema(Schema):

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)

class FamilyMemberSchema(Schema):

    id: UUID
    user_id: UUID
    user_email: str
    user_full_name: str
    role: str
    is_active: bool
    joined_at: datetime

class FamilyResponseSchema(Schema):

    id: UUID
    name: str
    description: str
    owner_id: UUID
    owner_email: str
    invite_code: str
    invite_code_expires_at: Optional[datetime]
    currency: str
    members_count: int
    created_at: datetime
    updated_at: datetime

class FamilyDetailSchema(FamilyResponseSchema):

    members: List[FamilyMemberSchema]

class JoinFamilySchema(Schema):

    invite_code: str = Field(..., min_length=8, max_length=8)

class UpdateMemberRoleSchema(Schema):

    role: str = Field(..., pattern="^(owner|member|viewer)$")

class RemoveMemberSchema(Schema):

    user_id: UUID
