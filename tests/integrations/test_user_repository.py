from uuid import uuid4

from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository


def _build_user(phone: str | None = None) -> User:
    unique = uuid4().hex[:10]
    return User.register(
        username=f'user{unique}',
        full_name='Test User',
        email=f'{unique}@example.com',
        password_hash='hashed-password',
        phone=phone,
    )


def test_save_persists_a_new_user(db_session: Session) -> None:
    repository = UserRepository(db_session)
    user = _build_user()

    repository.save(user)

    found = repository.find_by_username(user.username)
    assert found is not None
    assert found.id == user.id
    assert found.email == user.email
    assert found.status == user.status


def test_find_by_username_returns_none_when_not_found(db_session: Session) -> None:
    repository = UserRepository(db_session)

    assert repository.find_by_username('doesnotexist123') is None


def test_find_by_email_returns_the_matching_user(db_session: Session) -> None:
    repository = UserRepository(db_session)
    user = _build_user()
    repository.save(user)

    found = repository.find_by_email(user.email)

    assert found is not None
    assert found.username == user.username


def test_find_by_phone_returns_the_matching_user(db_session: Session) -> None:
    repository = UserRepository(db_session)
    phone = f'+51 9{uuid4().int % 100000000:08d}'
    user = _build_user(phone=phone)
    repository.save(user)

    found = repository.find_by_phone(phone)

    assert found is not None
    assert found.id == user.id
