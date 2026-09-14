from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class IssuedToken:
    token: str
    jti: str


@dataclass
class DecodedToken:
    jti: str
    is_expired: bool


class TokenIssuerPort(ABC):
    @abstractmethod
    def issue(self, user_id: UUID) -> IssuedToken: ...

    @abstractmethod
    def decode(self, token: str) -> DecodedToken | None: ...
