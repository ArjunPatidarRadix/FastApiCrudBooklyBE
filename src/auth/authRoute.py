from fastapi import APIRouter, Depends, HTTPException, status, Header, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import (
    UserCreateModel,
    UserBooksModel,
    UserModel,
    TokenModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import (
    create_access_token,
    verify_password,
    decode_token,
    create_url_safe_token,
    decode_url_safe_token,
    generate_hash_password,
)
from datetime import timedelta
from fastapi.responses import JSONResponse
from typing import Annotated
from src.auth.dependencies import AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import (
    InvalidToken,
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    RefreshTokenRequired,
)

from src.mail import create_message, mail
from src.config import Config
from src.celery_tasks import send_email

router = APIRouter()

user_service = UserService()
auth_handler = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


REFRESH_TOKEN_EXPIRY = 2


@router.post("/send_mail")
async def send_mail(emails: EmailModel):
    print("email: %s" % emails)

    try:
        emails = emails.addresses

        html = "<h1>Welcome to Bookly</h1>"

        msg = create_message(emails, "Bookly: Welcome!", html)
        mail.send_message(msg)

        # or

        # Below line will work only when there is redis setup in local systmem
        # send_email.delay(emails, "Bookly: Verify your email", html)

        return {"message": "Email sent"}

    except Exception as e:
        print("Error: %s" % e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email
    is_user_exist = await user_service.user_exists(email, session)
    if is_user_exist:
        raise UserAlreadyExists()
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="User with email already exists",
        # )
    new_user = await user_service.create_user(user_data, session)

    urlSafeToken = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/user/verify/{urlSafeToken}"

    html_message = f"""
    <h1>Verify your email</h1>
    <p>Click the link below to verify your email</p>
    <a href="{link}">Verify Email</a>
    """

    msg = create_message([email], "Bookly: Verify your email", html_message)
    background_tasks.add_task(mail.send_message, msg)

    # Below line will work only when there is redis setup in local systmem
    # send_email.delay([email], "Bookly: Verify your email", html_message)

    return {
        "message": "Account created! Check email to verify your account",
        "user": new_user,
    }


@router.get("/verify/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    if not token_data:
        raise InvalidToken()

    user_email = token_data["email"]

    if user_email:

        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        # user.is_verified = True

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Email verified successfully"},
        )

    raise JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Error occurred while verifying email"},
    )


@router.post("/login", response_model=TokenModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(form_data.username, session)
    if user is None:
        raise UserNotFound()
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail="User not found",
        # )
    if not verify_password(form_data.password, user.password_hash):
        raise InvalidCredentials()
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid credentials",
        # )

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
        raise RefreshTokenRequired()
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Invalid or expired refresh token",
        # )

    # Verify this is actually a refresh token
    if not payload.get("refresh"):
        raise RefreshTokenRequired()

        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Invalid token type. Must use refresh token",
        # )

    # Get user data from the token
    user_data = payload.get("user")
    if not user_data:
        raise InvalidToken()
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token payload"
        # )

    # Verify user still exists
    user = await user_service.get_user_by_email(user_data["email"], session)
    if not user:
        raise UserNotFound()
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        # )

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


@router.get("/me", response_model=UserBooksModel)
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


"""
1. Provide the email -> password reset request
2. Send password reset link to email
3. Reset password -> password reset confirm
"""


@router.post("/password-reset-request")
async def password_reset_request(
    email_data: PasswordResetRequestModel,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(email_data.email, session)
    if not user:
        raise UserNotFound()

    urlSafeToken = create_url_safe_token({"email": email_data.email})
    link = f"http://{Config.DOMAIN}/api/v1/user/password-reset-confirm/{urlSafeToken}"
    html_message = f"""
    <h1>Reset your password</h1>
    <p>Click the link below to reset your password</p>
    <a href="{link}">Reset Password</a>
    """
    msg = create_message(
        [email_data.email], "Bookly: Reset your password", html_message
    )
    await mail.send_message(msg)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Please check your email for instructions to reset your password"
        },
    )


@router.post("/password-reset-confirm/{token}")
async def password_reset_confirm(
    token: str,
    password_data: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    if password_data.new_password != password_data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    token_data = decode_url_safe_token(token)
    if not token_data:
        raise InvalidToken()

    user_email = token_data["email"]
    print("user_email: %s" % user_email)
    if not user_email:
        raise InvalidToken()

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFound()

    await user_service.update_user(
        user,
        {"password_hash": generate_hash_password(password_data.new_password)},
        session,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset successfully"},
    )
