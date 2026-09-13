from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.session import Session


class SessionRepositoryPort(ABC):
    @abstractmethod
    def save(self, session: Session) -> None: ...

    @abstractmethod
    def find_by_user_id(self, user_id: UUID) -> Session | None: ...

    @abstractmethod
    def update(self, session: Session) -> None: ...
