from fastapi import APIRouter, HTTPException, status, Depends
from src.db.models import User
from src.db.main import get_session
from .schemas import ReviewModelCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import ReviewService
from src.auth.dependencies import AccessTokenBearer, get_current_user

router = APIRouter()

review_service = ReviewService()


@router.post("/book/{book_id}")
async def add_review_to_book(
    book_id: str,
    review_data: ReviewModelCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        book_uid=book_id,
        review_data=review_data,
        session=session,
    )
    return new_review
