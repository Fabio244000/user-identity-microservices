from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class IssuedToken:
    token: str
    jti: str


class TokenIssuerPort(ABC):
    @abstractmethod
    def issue(self, user_id: UUID) -> IssuedToken: ...
