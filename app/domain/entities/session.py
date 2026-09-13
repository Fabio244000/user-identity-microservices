from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID


class SessionStatus(StrEnum):
    ACTIVE = 'activa'
    INVALIDATED = 'invalidada'


@dataclass
class Session:
    user_id: UUID
    token_id: str
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    invalidated_at: datetime | None = None
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
