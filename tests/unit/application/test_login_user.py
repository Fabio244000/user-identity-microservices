from unittest.mock import Mock

import pytest

from app.application.use_cases.login_user import LoginUser
from app.domain.entities.session import Session, SessionStatus
from app.domain.entities.user import User, UserStatus
from app.domain.exceptions.session_exceptions import SessionNotFoundError
from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    LoginNotAllowedError,
)
from app.domain.ports.output.password_hasher_port import PasswordHasherPort
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.domain.ports.output.token_issuer_port import IssuedToken, TokenIssuerPort
from app.domain.ports.output.user_repository_port import UserRepositoryPort

DURATION_MINUTES = 30


def _build_user(status: UserStatus = UserStatus.ACTIVE) -> User:
    user = User.register(
        username='johndoe123',
        full_name='John Doe',
        email='john@example.com',
        password_hash='hashed-password',
    )
    user.status = status
    return user


def _build_session(user: User, status: SessionStatus = SessionStatus.ACTIVE) -> Session:
    session = Session.start(
        user_id=user.id, token_id='old-jti', duration_minutes=DURATION_MINUTES
    )
    session.status = status
    session.id = 1
    return session


def _build_use_case() -> tuple[LoginUser, Mock, Mock, Mock, Mock]:
    user_repository = Mock(spec=UserRepositoryPort)
    session_repository = Mock(spec=SessionRepositoryPort)
    password_hasher = Mock(spec=PasswordHasherPort)
    token_issuer = Mock(spec=TokenIssuerPort)

    password_hasher.verify.return_value = True
    token_issuer.issue.return_value = IssuedToken(token='jwt-token', jti='new-jti')

    use_case = LoginUser(
        user_repository=user_repository,
        session_repository=session_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
        session_duration_minutes=DURATION_MINUTES,
    )
    return use_case, user_repository, session_repository, password_hasher, token_issuer


def test_execute_returns_user_and_token_for_an_active_session() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user = _build_user()
    user_repository.find_by_username.return_value = user
    session_repository.find_by_user_id.return_value = _build_session(
        user, SessionStatus.ACTIVE
    )

    result = use_case.execute(username='johndoe123', password='plain-password')

    assert result.user is user
    assert result.token == 'jwt-token'


def test_execute_succeeds_and_reactivates_a_closed_session() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user = _build_user()
    user_repository.find_by_username.return_value = user
    session = _build_session(user, SessionStatus.CLOSED)
    session_repository.find_by_user_id.return_value = session

    use_case.execute(username='johndoe123', password='plain-password')

    assert session.status == SessionStatus.ACTIVE


def test_execute_refreshes_the_session_with_the_newly_issued_token() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user = _build_user()
    user_repository.find_by_username.return_value = user
    session = _build_session(user)
    session_repository.find_by_user_id.return_value = session

    use_case.execute(username='johndoe123', password='plain-password')

    assert session.token_id == 'new-jti'
    session_repository.update.assert_called_once_with(session)


def test_execute_raises_invalid_credentials_when_username_not_found() -> None:
    use_case, user_repository, _, _, _ = _build_use_case()
    user_repository.find_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(username='doesnotexist', password='whatever')


def test_execute_raises_invalid_credentials_when_password_does_not_match() -> None:
    use_case, user_repository, _, password_hasher, _ = _build_use_case()
    user_repository.find_by_username.return_value = _build_user()
    password_hasher.verify.return_value = False

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(username='johndoe123', password='wrong-password')


def test_execute_raises_login_not_allowed_when_user_is_inactive() -> None:
    use_case, user_repository, _, _, _ = _build_use_case()
    user_repository.find_by_username.return_value = _build_user(
        status=UserStatus.INACTIVE
    )

    with pytest.raises(LoginNotAllowedError):
        use_case.execute(username='johndoe123', password='plain-password')


def test_execute_raises_login_not_allowed_when_user_is_suspended() -> None:
    use_case, user_repository, _, _, _ = _build_use_case()
    user_repository.find_by_username.return_value = _build_user(
        status=UserStatus.SUSPENDED
    )

    with pytest.raises(LoginNotAllowedError):
        use_case.execute(username='johndoe123', password='plain-password')


def test_execute_raises_login_not_allowed_when_session_is_suspended() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user = _build_user()
    user_repository.find_by_username.return_value = user
    session_repository.find_by_user_id.return_value = _build_session(
        user, SessionStatus.SUSPENDED
    )

    with pytest.raises(LoginNotAllowedError):
        use_case.execute(username='johndoe123', password='plain-password')


def test_execute_raises_session_not_found_when_no_session_exists_for_user() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user = _build_user()
    user_repository.find_by_username.return_value = user
    session_repository.find_by_user_id.return_value = None

    with pytest.raises(SessionNotFoundError) as exc_info:
        use_case.execute(username='johndoe123', password='plain-password')

    assert exc_info.value.user_id == user.id


def test_execute_checks_user_status_before_session_existence() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user_repository.find_by_username.return_value = _build_user(
        status=UserStatus.SUSPENDED
    )

    with pytest.raises(LoginNotAllowedError):
        use_case.execute(username='johndoe123', password='plain-password')

    session_repository.find_by_user_id.assert_not_called()


def test_execute_normalizes_username_before_lookup() -> None:
    use_case, user_repository, session_repository, _, _ = _build_use_case()
    user = _build_user()
    user_repository.find_by_username.return_value = user
    session_repository.find_by_user_id.return_value = _build_session(user)

    use_case.execute(username='JohnDoe123', password='plain-password')

    user_repository.find_by_username.assert_called_once_with('johndoe123')


def test_execute_does_not_touch_session_when_credentials_are_invalid() -> None:
    use_case, user_repository, session_repository, _, token_issuer = _build_use_case()
    user_repository.find_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(username='nouser', password='whatever')

    session_repository.find_by_user_id.assert_not_called()
    token_issuer.issue.assert_not_called()
    session_repository.update.assert_not_called()
