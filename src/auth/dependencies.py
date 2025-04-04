from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from fastapi import Request, status, Depends, HTTPException
from .utils import decode_token
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import UserLoginModel
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from .service import UserService
from typing import Any, List
from src.db.models import User
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    UserNotFound,
    AccountNotVerified,
)

userService = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


class AccessTokenBearer:
    async def __call__(
        self,
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        if not token:
            raise InvalidToken()

        payload = decode_token(token)

        if not payload:
            raise InvalidToken()

        # Commented because redix serer is not setup
        if await token_in_blocklist(payload["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Token has been revoked",
                    "resolution": "Please get new token",
                },
            )

        if payload.get("refresh"):
            raise AccessTokenRequired()

        user_service = UserService()
        user = await user_service.get_user_by_email(payload["user"]["email"], session)

        if not user:
            raise UserNotFound()

        return payload["user"]


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["email"]

    user = await userService.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermission()
        return True
