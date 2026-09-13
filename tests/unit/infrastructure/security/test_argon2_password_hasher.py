from argon2 import PasswordHasher

from app.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher


def test_hash_produces_a_value_different_from_the_plain_password() -> None:
    hasher = Argon2PasswordHasher()

    hashed = hasher.hash('plain-password123')

    assert hashed != 'plain-password123'


def test_hash_produces_a_value_that_verifies_against_the_original_password() -> None:
    hasher = Argon2PasswordHasher()

    hashed = hasher.hash('plain-password123')

    PasswordHasher().verify(hashed, 'plain-password123')
