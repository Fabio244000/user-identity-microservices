from unittest.mock import Mock

import pytest

from app.application.use_cases.register_user import RegisterUser
from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.domain.ports.output.password_hasher_port import PasswordHasherPort
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.domain.ports.output.token_issuer_port import IssuedToken, TokenIssuerPort
from app.domain.ports.output.user_repository_port import UserRepositoryPort

DURATION_MINUTES = 30


def _build_use_case() -> tuple[RegisterUser, Mock, Mock, Mock, Mock]:
    user_repository = Mock(spec=UserRepositoryPort)
    session_repository = Mock(spec=SessionRepositoryPort)
    password_hasher = Mock(spec=PasswordHasherPort)
    token_issuer = Mock(spec=TokenIssuerPort)

    user_repository.find_by_username.return_value = None
    user_repository.find_by_email.return_value = None
    user_repository.find_by_phone.return_value = None
    password_hasher.hash.return_value = 'hashed-password'
    token_issuer.issue.return_value = IssuedToken(token='jwt-token', jti='jti-value')

    use_case = RegisterUser(
        user_repository=user_repository,
        session_repository=session_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
        session_duration_minutes=DURATION_MINUTES,
    )
    return use_case, user_repository, session_repository, password_hasher, token_issuer


def test_execute_saves_a_user_with_hashed_password_and_normalized_fields() -> None:
    use_case, user_repository, _, password_hasher, _ = _build_use_case()

    use_case.execute(
        username='JohnDoe123',
        full_name='John Doe',
        email='John@Example.com',
        password='plain-password',
        phone='+51 987654321',
    )

    password_hasher.hash.assert_called_once_with('plain-password')
    saved_user = user_repository.save.call_args.args[0]
    assert saved_user.username == 'johndoe123'
    assert saved_user.email == 'john@example.com'
    assert saved_user.password_hash == 'hashed-password'
    assert saved_user.phone == '+51 987654321'


def test_execute_creates_an_active_session_for_the_issued_token() -> None:
    use_case, _, session_repository, _, _ = _build_use_case()

    use_case.execute(
        username='janedoe456',
        full_name='Jane Doe',
        email='jane@example.com',
        password='plain-password',
    )

    saved_session = session_repository.save.call_args.args[0]
    assert saved_session.token_id == 'jti-value'
    delta = saved_session.expires_at - saved_session.created_at
    assert delta.total_seconds() == DURATION_MINUTES * 60


def test_execute_returns_the_created_user_and_the_issued_token() -> None:
    use_case, *_ = _build_use_case()

    result = use_case.execute(
        username='someuser1',
        full_name='Some User',
        email='some@example.com',
        password='plain-password',
    )

    assert result.user.username == 'someuser1'
    assert result.token == 'jwt-token'


def test_execute_raises_when_username_is_already_taken() -> None:
    use_case, user_repository, _, _, _ = _build_use_case()
    user_repository.find_by_username.return_value = Mock()

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        use_case.execute(
            username='takenuser',
            full_name='Taken User',
            email='new@example.com',
            password='plain-password',
        )

    conflicts = exc_info.value.conflicts
    assert [c.field for c in conflicts] == ['username']


def test_execute_accumulates_all_conflicts_instead_of_failing_on_the_first() -> None:
    use_case, user_repository, _, _, _ = _build_use_case()
    user_repository.find_by_username.return_value = Mock()
    user_repository.find_by_email.return_value = Mock()
    user_repository.find_by_phone.return_value = Mock()

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        use_case.execute(
            username='takenuser',
            full_name='Taken User',
            email='taken@example.com',
            password='plain-password',
            phone='+51 987654321',
        )

    conflicts = exc_info.value.conflicts
    assert [c.field for c in conflicts] == ['username', 'email', 'phone']


def test_execute_does_not_create_the_user_when_there_is_a_conflict() -> None:
    use_case, user_repository, session_repository, password_hasher, token_issuer = (
        _build_use_case()
    )
    user_repository.find_by_username.return_value = Mock()

    with pytest.raises(UserAlreadyExistsError):
        use_case.execute(
            username='takenuser',
            full_name='Taken User',
            email='new@example.com',
            password='plain-password',
        )

    password_hasher.hash.assert_not_called()
    user_repository.save.assert_not_called()
    token_issuer.issue.assert_not_called()
    session_repository.save.assert_not_called()
