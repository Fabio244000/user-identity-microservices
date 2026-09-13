from uuid import uuid4

from app.domain.exceptions.session_exceptions import SessionNotFoundError


def test_carries_the_user_id() -> None:
    user_id = uuid4()

    error = SessionNotFoundError(user_id)

    assert error.user_id == user_id
