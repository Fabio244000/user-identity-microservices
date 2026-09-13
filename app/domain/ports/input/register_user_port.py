from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.user import User


@dataclass
class RegisterUserResult:
    user: User
    token: str


class RegisterUserPort(ABC):
    @abstractmethod
    def execute(
        self,
        username: str,
        full_name: str,
        email: str,
        password: str,
        phone: str | None = None,
    ) -> RegisterUserResult: ...
