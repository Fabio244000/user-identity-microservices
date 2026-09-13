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
    assert persisted.closed_at is None


def test_find_by_user_id_returns_the_matching_session(db_session: DbSession) -> None:
    user = _build_persisted_user(db_session)
    repository = SessionRepository(db_session)
    session = Session.start(user_id=user.id, token_id=uuid4().hex, duration_minutes=30)
    repository.save(session)

    found = repository.find_by_user_id(user.id)

    assert found is not None
    assert found.user_id == user.id
    assert found.token_id == session.token_id


def test_find_by_user_id_returns_none_when_not_found(db_session: DbSession) -> None:
    repository = SessionRepository(db_session)

    assert repository.find_by_user_id(uuid4()) is None


def test_update_persists_the_refreshed_token_and_expiration(
    db_session: DbSession,
) -> None:
    user = _build_persisted_user(db_session)
    repository = SessionRepository(db_session)
    session = Session.start(user_id=user.id, token_id=uuid4().hex, duration_minutes=30)
    repository.save(session)
    found = repository.find_by_user_id(user.id)
    assert found is not None

    found.refresh(token_id='refreshed-jti', duration_minutes=30)
    repository.update(found)

    updated = repository.find_by_user_id(user.id)
    assert updated is not None
    assert updated.token_id == 'refreshed-jti'
    assert updated.status == SessionStatus.ACTIVE
