from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import UserCreateModel, UserLoginModel, UserModel, TokenModel
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import create_access_token, verify_password, decode_token
from datetime import timedelta
from fastapi.responses import JSONResponse
from typing import Annotated
from src.auth.dependencies import AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist


router = APIRouter()

user_service = UserService()
auth_handler = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


REFRESH_TOKEN_EXPIRY = 2


@router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    is_user_exist = await user_service.user_exists(email, session)
    if is_user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with email already exists",
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(form_data.username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        user_data={
            "uid": str(user.uid),
            "email": user.email,
            "role": user.role,
        }
    )

    refresh_token = create_access_token(
        user_data={
            "uid": str(user.uid),
            "email": user.email,
            "role": user.role,
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "uid": str(user.uid),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
        },
    }


@router.get("/refresh", response_model=TokenModel)
async def refresh_token(
    athorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_session),
):
    # Decode and validate the refresh token
    print(athorization)
    payload = decode_token(athorization)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired refresh token",
        )

    # Verify this is actually a refresh token
    if not payload.get("refresh"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type. Must use refresh token",
        )

    # Get user data from the token
    user_data = payload.get("user")
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token payload"
        )

    # Verify user still exists
    user = await user_service.get_user_by_email(user_data["email"], session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Generate new tokens
    new_access_token = create_access_token(
        user_data={
            "uid": str(user.uid),
            "email": user.email,
            "role": user.role,
        }
    )

    new_refresh_token = create_access_token(
        user_data={
            "uid": str(user.uid),
            "email": user.email,
            "role": user.role,
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "uid": str(user.uid),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
        },
    }


@router.get("/me", response_model=UserModel)
async def get_current_user(
    current_user: dict = Depends(get_current_user), role: bool = Depends(role_checker)
):
    return current_user


@router.get("/logout")
async def logout(
    current_user: dict = Depends(auth_handler),
):
    print("Current user: %s" % current_user)
    jti = current_user["jti"]

    # await add_jti_to_blocklist(jti)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successfully logged out"},
    )
