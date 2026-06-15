from django.contrib.auth import authenticate
from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from ninja.security import HttpBearer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import User
from .schemas import (
    LoginSchema,
    PasswordChangeSchema,
    RefreshTokenSchema,
    TelegramLinkSchema,
    TokenSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            return User.objects.get(id=access_token["user_id"])
        except (TokenError, User.DoesNotExist, ValueError, KeyError):
            return None


auth = AuthBearer()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@router.post("/register", response=UserResponseSchema, tags=["Authentication"])
def register_user(request, payload: UserCreateSchema):
    with transaction.atomic():
        user = User.objects.create_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
        )
    return user


@router.post("/login", response=TokenSchema, tags=["Authentication"])
def login(request, payload: LoginSchema):
    user = authenticate(username=payload.email, password=payload.password)
    if not user:
        raise HttpError(401, "Invalid credentials")

    tokens = get_tokens_for_user(user)
    return {**tokens, "token_type": "Bearer"}


@router.post("/refresh", response=TokenSchema, tags=["Authentication"])
def refresh_token(request, payload: RefreshTokenSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "token_type": "Bearer",
        }
    except TokenError:
        raise HttpError(401, "Invalid refresh token")


@router.get("/me", response=UserResponseSchema, auth=auth, tags=["Users"])
def get_current_user(request):
    return request.auth


@router.patch("/me", response=UserResponseSchema, auth=auth, tags=["Users"])
def update_current_user(request, payload: UserUpdateSchema):
    user = request.auth

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, attr, value)

    user.save()
    return user


@router.post("/me/change-password", auth=auth, tags=["Users"])
def change_password(request, payload: PasswordChangeSchema):
    user = request.auth

    if not user.check_password(payload.old_password):
        raise HttpError(400, "Invalid old password")

    user.set_password(payload.new_password)
    user.save()

    return {"detail": "Password changed successfully"}


@router.post("/me/link-telegram", auth=auth, tags=["Users"])
def link_telegram(request, payload: TelegramLinkSchema):
    user = request.auth

    if User.objects.filter(telegram_id=payload.telegram_id).exclude(id=user.id).exists():
        raise HttpError(400, "This Telegram account is already linked to another user")

    user.telegram_id = payload.telegram_id
    user.telegram_username = payload.telegram_username
    user.save()

    return {"detail": "Telegram account linked successfully"}


@router.delete("/me/unlink-telegram", auth=auth, tags=["Users"])
def unlink_telegram(request):
    user = request.auth
    user.telegram_id = None
    user.telegram_username = None
    user.save()

    return {"detail": "Telegram account unlinked successfully"}
