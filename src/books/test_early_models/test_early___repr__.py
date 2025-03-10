import pytest
from datetime import datetime
from uuid import uuid4
from src.books.models import Book

@pytest.mark.describe("Tests for __repr__ method of Book class")
class TestBookRepr:
    
    @pytest.mark.happy_path
    def test_repr_with_valid_title(self):
        """Test __repr__ with a valid title."""
        book = Book(
            id=uuid4(),
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            publisher="Scribner",
            published_date="1925-04-10",
            page_count=218,
            language="English",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert repr(book) == "<Book The Great Gatsby>"

    @pytest.mark.happy_path
    def test_repr_with_different_title(self):
        """Test __repr__ with a different valid title."""
        book = Book(
            id=uuid4(),
            title="1984",
            author="George Orwell",
            publisher="Secker & Warburg",
            published_date="1949-06-08",
            page_count=328,
            language="English",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert repr(book) == "<Book 1984>"

    @pytest.mark.edge_case
    def test_repr_with_empty_title(self):
        """Test __repr__ with an empty title."""
        book = Book(
            id=uuid4(),
            title="",
            author="Unknown",
            publisher="Unknown",
            published_date="2023-01-01",
            page_count=0,
            language="Unknown",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert repr(book) == "<Book >"

    @pytest.mark.edge_case
    def test_repr_with_special_characters_in_title(self):
        """Test __repr__ with special characters in the title."""
        book = Book(
            id=uuid4(),
            title="!@#$%^&*()_+",
            author="Special Author",
            publisher="Special Publisher",
            published_date="2023-01-01",
            page_count=100,
            language="English",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert repr(book) == "<Book !@#$%^&*()_+>"

    @pytest.mark.edge_case
    def test_repr_with_long_title(self):
        """Test __repr__ with a very long title."""
        long_title = "A" * 1000
        book = Book(
            id=uuid4(),
            title=long_title,
            author="Long Author",
            publisher="Long Publisher",
            published_date="2023-01-01",
            page_count=1000,
            language="English",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert repr(book) == f"<Book {long_title}>"