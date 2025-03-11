import pytest
from passlib.context import CryptContext
from src.auth.utils import verify_password, generate_hash_password


# Define a pytest fixture for setting up the password context
@pytest.fixture
def password_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


# Describe block for all tests related to verify_password
@pytest.mark.describe("verify_password function")
class TestVerifyPassword:

    @pytest.mark.happy_path
    def test_verify_password_correct(self, password_context):
        """
        Test that verify_password returns True for a correct password.
        """
        plain_password = "securepassword123"
        hashed_password = generate_hash_password(plain_password)
        assert verify_password(plain_password, hashed_password) is True

    @pytest.mark.happy_path
    def test_verify_password_incorrect(self, password_context):
        """
        Test that verify_password returns False for an incorrect password.
        """
        plain_password = "securepassword123"
        wrong_password = "wrongpassword"
        hashed_password = generate_hash_password(plain_password)
        assert verify_password(wrong_password, hashed_password) is False

    @pytest.mark.edge_case
    def test_verify_password_empty_string(self, password_context):
        """
        Test that verify_password returns False when the plain password is an empty string.
        """
        plain_password = ""
        hashed_password = generate_hash_password("somepassword")
        assert verify_password(plain_password, hashed_password) is False

    @pytest.mark.edge_case
    def test_verify_password_empty_hashed(self, password_context):
        """
        Test that verify_password returns False when the hashed password is an empty string.
        """
        plain_password = "securepassword123"
        hashed_password = ""
        assert verify_password(plain_password, hashed_password) is False

    @pytest.mark.edge_case
    def test_verify_password_special_characters(self, password_context):
        """
        Test that verify_password correctly handles passwords with special characters.
        """
        plain_password = "p@ssw0rd!#%&"
        hashed_password = generate_hash_password(plain_password)
        assert verify_password(plain_password, hashed_password) is True

    @pytest.mark.edge_case
    def test_verify_password_unicode_characters(self, password_context):
        """
        Test that verify_password correctly handles passwords with unicode characters.
        """
        plain_password = "pässwördÜñîçødé"
        hashed_password = generate_hash_password(plain_password)
        assert verify_password(plain_password, hashed_password) is True

    @pytest.mark.edge_case
    def test_verify_password_long_password(self, password_context):
        """
        Test that verify_password correctly handles very long passwords.
        """
        plain_password = "a" * 1000  # 1000 characters long
        hashed_password = generate_hash_password(plain_password)
        assert verify_password(plain_password, hashed_password) is True

    @pytest.mark.edge_case
    def test_verify_password_none_input(self, password_context):
        """
        Test that verify_password raises an error when None is passed as input.
        """
        with pytest.raises(TypeError):
            verify_password(None, None)


# Note: The generate_hash_password function is assumed to be available in the same module as verify_password.
