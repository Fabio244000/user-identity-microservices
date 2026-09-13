from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepositoryPort(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def find_by_phone(self, phone: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> None: ...
