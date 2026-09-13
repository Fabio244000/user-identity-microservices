from abc import ABC, abstractmethod

from app.domain.entities.session import Session


class SessionRepositoryPort(ABC):
    @abstractmethod
    def save(self, session: Session) -> None: ...
