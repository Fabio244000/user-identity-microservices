from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.user import User


@dataclass
class LoginUserResult:
    user: User
    token: str


class LoginUserPort(ABC):
    @abstractmethod
    def execute(self, username: str, password: str) -> LoginUserResult: ...
