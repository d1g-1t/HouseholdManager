from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import Schema

class CategoryCreateSchema(Schema):

    name: str
    type: str
    color: Optional[str] = "#808080"
    icon: Optional[str] = None

class CategoryUpdateSchema(Schema):

    name: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class CategoryResponseSchema(Schema):

    id: UUID
    name: str
    type: str
    color: str
    icon: Optional[str]
    is_default: bool
    created_at: datetime
    updated_at: datetime
