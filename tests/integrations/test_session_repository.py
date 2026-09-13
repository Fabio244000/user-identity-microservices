from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.domain.entities.session import Session, SessionStatus
from app.domain.entities.user import User
from app.infrastructure.database.models import SessionModel
from app.infrastructure.database.repositories.session_repository import (
    SessionRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


def _build_persisted_user(db_session: DbSession) -> User:
    unique = uuid4().hex[:10]
    user = User.register(
        username=f'user{unique}',
        full_name='Test User',
        email=f'{unique}@example.com',
        password_hash='hashed-password',
    )
    UserRepository(db_session).save(user)
    return user


def test_save_persists_a_new_active_session(db_session: DbSession) -> None:
    user = _build_persisted_user(db_session)
    repository = SessionRepository(db_session)
    token_id = uuid4().hex
    session = Session.start(user_id=user.id, token_id=token_id, duration_minutes=30)

    repository.save(session)

    persisted = db_session.execute(
        select(SessionModel).where(SessionModel.token_id == token_id)
    ).scalar_one_or_none()
    assert persisted is not None
    assert persisted.user_id == user.id
    assert persisted.status == SessionStatus.ACTIVE
    assert persisted.invalidated_at is None
