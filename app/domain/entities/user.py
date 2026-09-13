from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class UserStatus(StrEnum):
    ACTIVE = 'activo'
    INACTIVE = 'inactivo'
    SUSPENDED = 'suspendido'


@dataclass
class User:
    id: UUID
    username: str
    full_name: str
    email: str
    phone: str | None
    password_hash: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def register(
        cls,
        username: str,
        full_name: str,
        email: str,
        password_hash: str,
        phone: str | None = None,
    ) -> 'User':
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            username=username.lower(),
            full_name=full_name,
            email=email.lower(),
            phone=phone,
            password_hash=password_hash,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
