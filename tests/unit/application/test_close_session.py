from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.application.use_cases.close_session import CloseSession
from app.domain.entities.session import Session, SessionStatus
from app.domain.exceptions.session_exceptions import InvalidSessionTokenError
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.domain.ports.output.token_issuer_port import DecodedToken, TokenIssuerPort


def _build_session(status: SessionStatus = SessionStatus.ACTIVE) -> Session:
    session = Session.start(user_id=uuid4(), token_id='some-jti', duration_minutes=30)
    session.status = status
    session.id = 1
    return session


def _build_use_case() -> tuple[CloseSession, Mock, Mock]:
    session_repository = Mock(spec=SessionRepositoryPort)
    token_issuer = Mock(spec=TokenIssuerPort)
    token_issuer.decode.return_value = DecodedToken(jti='some-jti', is_expired=False)

    use_case = CloseSession(
        session_repository=session_repository, token_issuer=token_issuer
    )
    return use_case, session_repository, token_issuer


def test_execute_closes_an_active_session_for_a_valid_token() -> None:
    use_case, session_repository, _ = _build_use_case()
    session = _build_session(SessionStatus.ACTIVE)
    session_repository.find_by_token_id.return_value = session

    use_case.execute('valid-token')

    assert session.status == SessionStatus.CLOSED
    assert session.closed_at is not None
    session_repository.update.assert_called_once_with(session)


def test_execute_looks_up_the_session_by_the_decoded_jti() -> None:
    use_case, session_repository, token_issuer = _build_use_case()
    token_issuer.decode.return_value = DecodedToken(jti='the-jti', is_expired=False)
    session_repository.find_by_token_id.return_value = _build_session()

    use_case.execute('valid-token')

    token_issuer.decode.assert_called_once_with('valid-token')
    session_repository.find_by_token_id.assert_called_once_with('the-jti')


def test_execute_raises_when_token_cannot_be_decoded() -> None:
    use_case, session_repository, token_issuer = _build_use_case()
    token_issuer.decode.return_value = None

    with pytest.raises(InvalidSessionTokenError):
        use_case.execute('garbage-token')

    session_repository.find_by_token_id.assert_not_called()
    session_repository.update.assert_not_called()


def test_execute_raises_when_no_session_matches_the_token() -> None:
    use_case, session_repository, _ = _build_use_case()
    session_repository.find_by_token_id.return_value = None

    with pytest.raises(InvalidSessionTokenError):
        use_case.execute('valid-token')

    session_repository.update.assert_not_called()


def test_execute_auto_closes_an_active_session_for_an_expired_token() -> None:
    use_case, session_repository, token_issuer = _build_use_case()
    token_issuer.decode.return_value = DecodedToken(jti='some-jti', is_expired=True)
    session = _build_session(SessionStatus.ACTIVE)
    session_repository.find_by_token_id.return_value = session

    with pytest.raises(InvalidSessionTokenError):
        use_case.execute('expired-token')

    assert session.status == SessionStatus.CLOSED
    session_repository.update.assert_called_once_with(session)


def test_execute_does_not_touch_an_already_closed_session_for_an_expired_token() -> (
    None
):
    use_case, session_repository, token_issuer = _build_use_case()
    token_issuer.decode.return_value = DecodedToken(jti='some-jti', is_expired=True)
    session = _build_session(SessionStatus.CLOSED)
    session_repository.find_by_token_id.return_value = session

    with pytest.raises(InvalidSessionTokenError):
        use_case.execute('expired-token')

    session_repository.update.assert_not_called()


def test_execute_raises_when_session_is_already_closed() -> None:
    use_case, session_repository, _ = _build_use_case()
    session = _build_session(SessionStatus.CLOSED)
    session_repository.find_by_token_id.return_value = session

    with pytest.raises(InvalidSessionTokenError):
        use_case.execute('valid-token')

    session_repository.update.assert_not_called()


def test_execute_raises_when_session_is_suspended() -> None:
    use_case, session_repository, _ = _build_use_case()
    session = _build_session(SessionStatus.SUSPENDED)
    session_repository.find_by_token_id.return_value = session

    with pytest.raises(InvalidSessionTokenError):
        use_case.execute('valid-token')

    session_repository.update.assert_not_called()
