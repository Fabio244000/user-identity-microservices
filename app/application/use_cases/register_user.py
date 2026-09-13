from uuid import UUID

from app.domain.constants.messages import (
    EMAIL_ALREADY_EXISTS_DETAIL,
    PHONE_ALREADY_EXISTS_DETAIL,
    USERNAME_ALREADY_EXISTS_DETAIL,
)
from app.domain.entities.session import Session
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import FieldConflict, UserAlreadyExistsError
from app.domain.ports.input.register_user_port import (
    RegisterUserPort,
    RegisterUserResult,
)
from app.domain.ports.output.password_hasher_port import PasswordHasherPort
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.domain.ports.output.token_issuer_port import TokenIssuerPort
from app.domain.ports.output.user_repository_port import UserRepositoryPort


class RegisterUser(RegisterUserPort):
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

    def execute(
        self,
        username: str,
        full_name: str,
        email: str,
        password: str,
        phone: str | None = None,
    ) -> RegisterUserResult:
        self._ensure_unique(username, email, phone)
        user = self._create_user(username, full_name, email, password, phone)
        issued_token = self._token_issuer.issue(user.id)
        self._create_session(user.id, issued_token.jti)
        return RegisterUserResult(user=user, token=issued_token.token)

    def _ensure_unique(self, username: str, email: str, phone: str | None) -> None:
        conflicts: list[FieldConflict] = []
        if self._user_repository.find_by_username(username.lower()):
            conflicts.append(FieldConflict('username', USERNAME_ALREADY_EXISTS_DETAIL))
        if self._user_repository.find_by_email(email.lower()):
            conflicts.append(FieldConflict('email', EMAIL_ALREADY_EXISTS_DETAIL))
        if phone and self._user_repository.find_by_phone(phone):
            conflicts.append(FieldConflict('phone', PHONE_ALREADY_EXISTS_DETAIL))
        if conflicts:
            raise UserAlreadyExistsError(conflicts)

    def _create_user(
        self,
        username: str,
        full_name: str,
        email: str,
        password: str,
        phone: str | None,
    ) -> User:
        user = User.register(
            username=username,
            full_name=full_name,
            email=email,
            password_hash=self._password_hasher.hash(password),
            phone=phone,
        )
        self._user_repository.save(user)
        return user

    def _create_session(self, user_id: UUID, token_id: str) -> None:
        session = Session.start(
            user_id=user_id,
            token_id=token_id,
            duration_minutes=self._session_duration_minutes,
        )
        self._session_repository.save(session)
