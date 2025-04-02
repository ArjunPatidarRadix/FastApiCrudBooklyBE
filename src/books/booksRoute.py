from fastapi import APIRouter, HTTPException, status, Depends
from . import schemas
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import (
    BookNotFound,
)

router = APIRouter()
book_service = BookService()
auth_handler = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@router.get("/", response_model=List[schemas.BookModel], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(auth_handler),
):
    books = await book_service.get_all_books(session)
    return books


@router.get(
    "/user/{user_uid}",
    response_model=List[schemas.BookModel],
    dependencies=[role_checker],
)
async def get_user_books_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(auth_handler),
):
    books = await book_service.get_user_books(user_uid, session)
    return books


@router.get(
    "/{book_uid}", response_model=schemas.BookDetailModel, dependencies=[role_checker]
)
async def get_book_by_id(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(auth_handler),
):
    book = await book_service.get_book_by_id(book_uid, session)
    if book:
        return book
    raise BookNotFound()
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.BookModel,
    dependencies=[role_checker],
)
async def create_book(
    book: schemas.BookModelCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(auth_handler),
):
    print("current_user:: ", current_user)
    user_uid = current_user["uid"]
    new_book = await book_service.create_book(book, user_uid, session)
    return new_book


@router.put(
    "/{book_uid}", response_model=schemas.BookModel, dependencies=[role_checker]
)
async def update_book(
    book_uid: str,
    book_data: schemas.BookModelUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(auth_handler),
):
    book_to_update = await book_service.update_book(book_uid, book_data, session)
    if book_to_update:
        return book_to_update
    raise BookNotFound()
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.delete("/{book_uid}", dependencies=[role_checker])
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(auth_handler),
):
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete:
        return {"Deleted book with UID": book_to_delete.uid}
    raise BookNotFound()
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
