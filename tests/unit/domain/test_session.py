from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.session import Session, SessionStatus

DURATION_MINUTES = 30


def _build_active_session() -> Session:
    return Session.start(
        user_id=uuid4(), token_id='old-jti', duration_minutes=DURATION_MINUTES
    )


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


def test_start_leaves_id_and_closed_at_unset() -> None:
    session = Session.start(
        user_id=uuid4(), token_id='some-jti', duration_minutes=DURATION_MINUTES
    )

    assert session.id is None
    assert session.closed_at is None


def test_refresh_replaces_token_id() -> None:
    session = _build_active_session()

    session.refresh(token_id='new-jti', duration_minutes=DURATION_MINUTES)

    assert session.token_id == 'new-jti'


def test_refresh_sets_status_to_active() -> None:
    session = _build_active_session()
    session.status = SessionStatus.CLOSED

    session.refresh(token_id='new-jti', duration_minutes=DURATION_MINUTES)

    assert session.status == SessionStatus.ACTIVE


def test_refresh_recomputes_expiration_from_now() -> None:
    session = _build_active_session()

    session.refresh(token_id='new-jti', duration_minutes=DURATION_MINUTES)

    delta = session.expires_at - session.created_at
    assert delta.total_seconds() == DURATION_MINUTES * 60


def test_refresh_clears_closed_at() -> None:
    session = _build_active_session()
    session.closed_at = datetime.now(UTC)

    session.refresh(token_id='new-jti', duration_minutes=DURATION_MINUTES)

    assert session.closed_at is None


def test_close_sets_status_to_closed() -> None:
    session = _build_active_session()

    session.close()

    assert session.status == SessionStatus.CLOSED


def test_close_sets_closed_at() -> None:
    session = _build_active_session()

    session.close()

    assert session.closed_at is not None
