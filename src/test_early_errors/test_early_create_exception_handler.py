import pytest
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from src.errors import (
    create_exception_handler,
    BooklyException,
    InvalidToken,
    UserNotFound,
)


# Mock Request object for testing
class MockRequest:
    pass


@pytest.mark.describe("Tests for create_exception_handler function")
class TestCreateExceptionHandler:

    @pytest.mark.happy_path
    def test_happy_path_valid_exception(self):
        """
        Test that the exception handler returns the correct JSONResponse
        with the given status code and initial detail for a valid BooklyException.
        """
        status_code = 400
        initial_detail = {"error": "Invalid token"}
        handler = create_exception_handler(status_code, initial_detail)

        request = MockRequest()
        exc = InvalidToken("Invalid token provided")

        response = handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status_code
        assert response.body == b'{"error":"Invalid token"}'

    @pytest.mark.happy_path
    def test_happy_path_different_exception(self):
        """
        Test that the exception handler returns the correct JSONResponse
        for a different type of BooklyException.
        """
        status_code = 404
        initial_detail = {"error": "User not found"}
        handler = create_exception_handler(status_code, initial_detail)

        request = MockRequest()
        exc = UserNotFound("User does not exist")

        response = handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status_code
        assert response.body == b'{"error":"User not found"}'

    @pytest.mark.edge_case
    def test_edge_case_non_bookly_exception(self):
        """
        Test that the exception handler can handle a non-BooklyException gracefully.
        """
        status_code = 500
        initial_detail = {"error": "Internal server error"}
        handler = create_exception_handler(status_code, initial_detail)

        request = MockRequest()
        exc = Exception("General exception")

        response = handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status_code
        assert response.body == b'{"error":"Internal server error"}'

    @pytest.mark.edge_case
    def test_edge_case_empty_initial_detail(self):
        """
        Test that the exception handler can handle an empty initial detail.
        """
        status_code = 400
        initial_detail = {}
        handler = create_exception_handler(status_code, initial_detail)

        request = MockRequest()
        exc = InvalidToken("Invalid token provided")

        response = handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status_code
        assert response.body == b"{}"

    @pytest.mark.edge_case
    def test_edge_case_none_initial_detail(self):
        """
        Test that the exception handler can handle a None initial detail.
        """
        status_code = 400
        initial_detail = None
        handler = create_exception_handler(status_code, initial_detail)

        request = MockRequest()
        exc = InvalidToken("Invalid token provided")

        response = handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status_code
        assert response.body == b"null"
