from argon2 import PasswordHasher

from app.domain.ports.output.password_hasher_port import PasswordHasherPort


class Argon2PasswordHasher(PasswordHasherPort):
    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)
