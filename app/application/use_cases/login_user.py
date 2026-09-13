from uuid import UUID

from app.domain.entities.session import Session, SessionStatus
from app.domain.entities.user import User, UserStatus
from app.domain.exceptions.session_exceptions import SessionNotFoundError
from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    LoginNotAllowedError,
)
from app.domain.ports.input.login_user_port import LoginUserPort, LoginUserResult
from app.domain.ports.output.password_hasher_port import PasswordHasherPort
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.domain.ports.output.token_issuer_port import TokenIssuerPort
from app.domain.ports.output.user_repository_port import UserRepositoryPort


class LoginUser(LoginUserPort):
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        session_repository: SessionRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_issuer: TokenIssuerPort,
        session_duration_minutes: int,
    ) -> None:
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._password_hasher = password_hasher
        self._token_issuer = token_issuer
        self._session_duration_minutes = session_duration_minutes

    def execute(self, username: str, password: str) -> LoginUserResult:
        user = self._authenticate(username, password)
        self._ensure_user_can_login(user)
        session = self._find_session(user.id)
        self._ensure_session_can_login(session)
        issued_token = self._token_issuer.issue(user.id)
        session.refresh(issued_token.jti, self._session_duration_minutes)
        self._session_repository.update(session)
        return LoginUserResult(user=user, token=issued_token.token)

    def _authenticate(self, username: str, password: str) -> User:
        user = self._user_repository.find_by_username(username.lower())
        if user is None or not self._password_hasher.verify(
            password, user.password_hash
        ):
            raise InvalidCredentialsError
        return user

    def _ensure_user_can_login(self, user: User) -> None:
        if user.status != UserStatus.ACTIVE:
            raise LoginNotAllowedError

    def _find_session(self, user_id: UUID) -> Session:
        session = self._session_repository.find_by_user_id(user_id)
        if session is None:
            raise SessionNotFoundError(user_id)
        return session

    def _ensure_session_can_login(self, session: Session) -> None:
        if session.status == SessionStatus.SUSPENDED:
            raise LoginNotAllowedError
