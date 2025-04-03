books_prefix = f"/api/v1/books"


def test_get_all_books(fake_session, fake_book_service, test_client):
    response = test_client.get(url=f"{books_prefix}")
    assert fake_book_service.get_all_books_called_once()
    assert fake_book_service.get_all_books_called_once_with(fake_session)
    # assert response.status_code == 200
    # assert response.json() == []
