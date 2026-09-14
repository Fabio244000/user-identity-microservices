from app.domain.entities.session import Session, SessionStatus
from app.domain.exceptions.session_exceptions import InvalidSessionTokenError
from app.domain.ports.input.close_session_port import CloseSessionPort
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.domain.ports.output.token_issuer_port import TokenIssuerPort


class CloseSession(CloseSessionPort):
    def __init__(
        self,
        session_repository: SessionRepositoryPort,
        token_issuer: TokenIssuerPort,
    ) -> None:
        self._session_repository = session_repository
        self._token_issuer = token_issuer

    def execute(self, token: str) -> None:
        decoded = self._token_issuer.decode(token)
        if decoded is None:
            raise InvalidSessionTokenError

        session = self._session_repository.find_by_token_id(decoded.jti)
        if session is None:
            raise InvalidSessionTokenError

        if decoded.is_expired:
            self._auto_close_if_active(session)
            raise InvalidSessionTokenError

        self._close_active_session(session)

    def _auto_close_if_active(self, session: Session) -> None:
        if session.status == SessionStatus.ACTIVE:
            session.close()
            self._session_repository.update(session)

    def _close_active_session(self, session: Session) -> None:
        if session.status != SessionStatus.ACTIVE:
            raise InvalidSessionTokenError
        session.close()
        self._session_repository.update(session)
