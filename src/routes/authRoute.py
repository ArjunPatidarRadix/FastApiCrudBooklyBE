from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.schemas import UserCreateModel, UserLoginModel, UserModel
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import create_access_token, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse

router = APIRouter()

user_service = UserService()

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


@router.post("/login", response_model=UserModel)
async def login(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    user = await user_service.get_user_by_email(login_data.email, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        user_data={
            "uid": str(user.uid),
            "email": user.email,
        }
    )

    refresh_token = create_access_token(
        user_data={
            "uid": str(user.uid),
            "email": user.email,
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )
    return JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "message": "Login successful",
            "user": {
                "uid": str(user.uid),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
            },
        }
    )

    # {"access_token": access_token, "token_type": "bearer"}
