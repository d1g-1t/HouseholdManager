from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import Schema
from pydantic import EmailStr, Field

class UserCreateSchema(Schema):

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=150)
    last_name: str = Field(..., min_length=1, max_length=150)
    phone: Optional[str] = None
    language: str = Field(default="ru", pattern="^(ru|en)$")

class UserUpdateSchema(Schema):

    first_name: Optional[str] = Field(None, min_length=1, max_length=150)
    last_name: Optional[str] = Field(None, min_length=1, max_length=150)
    phone: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    language: Optional[str] = Field(None, pattern="^(ru|en)$")
    email_notifications_enabled: Optional[bool] = None
    telegram_notifications_enabled: Optional[bool] = None

class UserResponseSchema(Schema):

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None
    telegram_notifications_enabled: bool
    email_notifications_enabled: bool
    currency: str
    language: str
    created_at: datetime
    updated_at: datetime

class TokenSchema(Schema):

    access: str
    refresh: str
    token_type: str = "Bearer"

class LoginSchema(Schema):

    email: EmailStr
    password: str

class RefreshTokenSchema(Schema):

    refresh: str

class PasswordChangeSchema(Schema):

    old_password: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequestSchema(Schema):

    email: EmailStr

class PasswordResetConfirmSchema(Schema):

    token: str
    new_password: str = Field(..., min_length=8)

class TelegramLinkSchema(Schema):

    telegram_id: int
    telegram_username: Optional[str] = None
