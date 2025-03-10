from .schemas import BookModel
from datetime import datetime
from uuid import UUID, uuid4

books = [
    BookModel(
        uid=uuid4(),
        title="Harry Potter",
        author="J.K. Rowling",
        publisher="Bloomsbury",
        published_date="1997-06-26",
        page_count=223,
        language="English",
        created_at= datetime.now(),
        updated_at= datetime.now()
    ),
    BookModel(
        uid=uuid4(),
        title="To Kill a Mockingbird",
        author="Harper Lee",
        publisher="HarperCollins",
        published_date="1960-07-11",
        page_count=288,
        language="English",
        created_at= datetime.now(),
        updated_at= datetime.now()
    ),
    BookModel(
        uid=uuid4(),
        title="1984",
        author="George Orwell",
        publisher="Secker & Warburg",
        published_date="1949-06-03",
        page_count=328,
        language="English",
        created_at= datetime.now(),
        updated_at= datetime.now()
    ),
    BookModel(
        uid=uuid4(),
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        publisher="J.B. Lippincott & Co.",
        published_date="1925-04-10",
        page_count=253,
        language="English",
        created_at= datetime.now(),
        updated_at= datetime.now()
    )
]
        

# books = [
#     {
#         "uid": 1,
#         "title": "Harry Potter",
#         "author": "J.K. Rowling",
#         "publisher": "Bloomsbury",
#         "published_date": "1997-06-26",
#         "page_count": 223,
#         "language": "English"
#     },
#     {
#         "uid": 2,
#         "title": "To Kill a Mockingbird",
#         "author": "Harper Lee",
#         "publisher": "HarperCollins",
#         "published_date": "1960-07-11",
#         "page_count": 288,
#         "language": "English"
#     },
#     {
#         "uid": 3,
#         "title": "1984",
#         "author": "George Orwell",
#         "publisher": "Secker & Warburg",
#         "published_date": "1949-06-03",
#         "page_count": 328,
#         "language": "English"
#     },
#     {
#         "uid": "4",
#         "title": "The Great Gatsby",
#         "author": "F. Scott Fitzgerald",
#         "publisher": "J.B. Lippincott & Co.",
#         "published_date": "1925-04-10",
#         "page_count": 253,
#         "language": "English"
#     },
#     {
#         "uid": 5,
#         "title": "The Catcher in the Rye",
#         "author": "J.D. Salinger",
#         "publisher": "Little, Brown and Company",
#         "published_date": "1951-07-16",
#         "page_count": 277,
#         "language": "English"
#     }
# ]