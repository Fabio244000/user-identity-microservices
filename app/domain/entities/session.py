from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID


class SessionStatus(StrEnum):
    ACTIVE = 'activa'
    CLOSED = 'cerrada'
    SUSPENDED = 'suspendida'


@dataclass
class Session:
    user_id: UUID
    token_id: str
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    closed_at: datetime | None = None
    id: int | None = None

    @classmethod
    def start(cls, user_id: UUID, token_id: str, duration_minutes: int) -> 'Session':
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(minutes=duration_minutes)
        return cls(
            user_id=user_id,
            token_id=token_id,
            status=SessionStatus.ACTIVE,
            created_at=created_at,
            expires_at=expires_at,
        )

    def refresh(self, token_id: str, duration_minutes: int) -> None:
        created_at = datetime.now(UTC)
        self.token_id = token_id
        self.status = SessionStatus.ACTIVE
        self.created_at = created_at
        self.expires_at = created_at + timedelta(minutes=duration_minutes)
        self.closed_at = None

    def close(self) -> None:
        self.status = SessionStatus.CLOSED
        self.closed_at = datetime.now(UTC)
