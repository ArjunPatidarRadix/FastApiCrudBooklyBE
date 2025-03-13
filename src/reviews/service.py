from src.db.models import Review
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .schemas import ReviewModelCreate
from datetime import datetime
from src.books.service import BookService
from src.auth.service import UserService
from src.auth.dependencies import AccessTokenBearer
from fastapi import Depends, HTTPException, status
from uuid import UUID
import logging

user_service = UserService()
book_service = BookService()


class ReviewService:
    async def get_all_reviews(self, session: AsyncSession):
        try:
            statement = select(Review).order_by(Review.created_at.desc())
            result = await session.exec(statement)
            return result.all()
        except Exception as e:
            print("Error: ", e)

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewModelCreate,
        session: AsyncSession,
    ):
        try:
            user = await user_service.get_user_by_email(user_email, session)
            book = await book_service.get_book_by_id(book_uid, session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found",
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            review = Review(**review_data.model_dump())
            # review.user_uid = user.uid
            # review.book_uid = book.uid
            review.user = user
            review.book = book
            session.add(review)
            await session.commit()
            return review
        except Exception as e:
            logging.exception(f"Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong, please try again",
            )
