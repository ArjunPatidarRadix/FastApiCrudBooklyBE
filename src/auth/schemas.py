from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class UserBaseModel(BaseModel):
    username: str = Field(..., description="Username")
    email: str = Field(..., description="user email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    is_verified: bool = Field(..., description="Is User Verified")
    password_hash: str = Field(..., description="Password Hash", exclude=True)
    created_at: datetime = Field(..., description="Created At")
    updated_at: datetime = Field(..., description="Updated At")


class UserModel(UserBaseModel):
    uid: UUID = Field(..., description="User ID")


class UserCreateModel(BaseModel):
    username: str = Field(..., max_length=8, description="Username")
    email: str = Field(..., max_length=40, description="user email")
    first_name: str = Field(..., max_length=25, description="First Name")
    last_name: str = Field(..., max_length=25, description="Last Name")
    password: str = Field(..., min_length=6, description="password")


class UserLoginModel(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., description="password")
