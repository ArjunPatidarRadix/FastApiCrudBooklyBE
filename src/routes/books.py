from fastapi import APIRouter, HTTPException, status, Depends
from ..books import schemas
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..books.service import BookService
from src.auth.dependencies import AccessTokenBearer


router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@router.get("/", response_model=List[schemas.BookModel])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


@router.get("/{book_uid}", response_model=schemas.BookModel)
async def get_book_by_id(book_uid: str, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book_by_id(book_uid, session)
    if book:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.BookModel)
async def create_book(
    book: schemas.BookModelCreate, session: AsyncSession = Depends(get_session)
):
    new_book = await book_service.create_book(book, session)
    return new_book


@router.put("/{book_uid}", response_model=schemas.BookModel)
async def update_book(
    book_uid: str,
    book_data: schemas.BookModelUpdate,
    session: AsyncSession = Depends(get_session),
):
    book_to_update = await book_service.update_book(book_uid, book_data, session)
    if book_to_update:
        return book_to_update
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.delete("/{book_uid}")
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete:
        return {"Deleted book with UID": book_to_delete.uid}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
