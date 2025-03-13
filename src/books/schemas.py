from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from src.reviews.schemas import ReviewModel

# from src.auth.schemas import UserModel


class BookBaseModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookModel(BookBaseModel):
    uid: UUID


class BookDetailModel(BookModel):
    # pass
    reviews: List[ReviewModel]


class BookModelUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Book Title")
    author: Optional[str] = Field(None, description="Book Author")
    publisher: Optional[str] = Field(None, description="Book Publisher")
    page_count: Optional[int] = Field(None, description="Book Page Count")
    language: Optional[str] = Field(None, description="Book Language")


class BookModelCreate(BaseModel):
    title: str = Field(..., description="Book Title")
    author: str = Field(..., description="Book Author")
    publisher: str = Field(..., description="Book Publisher")
    published_date: str = Field(description="Book Published Date", default="2020-02-03")
    page_count: int = Field(..., description="Book Page Count")
    language: str = Field(..., description="Book Language")
