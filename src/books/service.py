from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Book
from .schemas import BookModelCreate, BookModelUpdate
from sqlmodel import select, desc
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book_by_id(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        return result.first()

    async def create_book(self, book_data: BookModelCreate, session: AsyncSession):
        book = Book(**book_data.model_dump())
        book.published_date = datetime.strptime(book_data.published_date, "%Y-%m-%d")
        session.add(book)
        await session.commit()
        return book if book is not None else None

    async def update_book(
        self, book_uid: str, book_data: BookModelUpdate, session: AsyncSession
    ):

        book_to_update = await self.get_book_by_id(book_uid, session)
        if book_to_update:
            book_data = book_data.model_dump(exclude_unset=True)
            for key, value in book_data.items():
                setattr(book_to_update, key, value)
            await session.commit()
            return book_to_update
        return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book_by_id(book_uid, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        return None
