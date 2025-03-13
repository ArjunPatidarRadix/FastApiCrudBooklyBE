from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ReviewBaseModel(BaseModel):
    book_uid: Optional[UUID]
    user_uid: Optional[UUID]
    rating: int
    review_text: str
    created_at: datetime
    updated_at: datetime


class ReviewModel(ReviewBaseModel):
    uid: UUID


class ReviewModelCreate(BaseModel):
    rating: int = Field(..., description="Rating")
    review_text: str = Field(..., description="Review Text")
