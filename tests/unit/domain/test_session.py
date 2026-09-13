from uuid import uuid4

from app.domain.entities.session import Session, SessionStatus

DURATION_MINUTES = 30


def test_start_sets_initial_status_to_active() -> None:
    session = Session.start(
        user_id=uuid4(), token_id='some-jti', duration_minutes=DURATION_MINUTES
    )

    assert session.status == SessionStatus.ACTIVE


def test_start_computes_expiration_from_duration_minutes() -> None:
    session = Session.start(
        user_id=uuid4(), token_id='some-jti', duration_minutes=DURATION_MINUTES
    )

    delta = session.expires_at - session.created_at
    assert delta.total_seconds() == DURATION_MINUTES * 60


def test_start_leaves_id_and_invalidated_at_unset() -> None:
    session = Session.start(
        user_id=uuid4(), token_id='some-jti', duration_minutes=DURATION_MINUTES
    )

    assert session.id is None
    assert session.invalidated_at is None
