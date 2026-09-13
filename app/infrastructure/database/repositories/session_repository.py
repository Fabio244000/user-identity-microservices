from sqlalchemy.orm import Session as DbSession

from app.domain.entities.session import Session
from app.domain.ports.output.session_repository_port import SessionRepositoryPort
from app.infrastructure.database.models import SessionModel


class SessionRepository(SessionRepositoryPort):
    def __init__(self, db_session: DbSession) -> None:
        self._db_session = db_session

    def save(self, session: Session) -> None:
        model = SessionModel(
            user_id=session.user_id,
            token_id=session.token_id,
            status=session.status,
            created_at=session.created_at,
            expires_at=session.expires_at,
            invalidated_at=session.invalidated_at,
        )
        self._db_session.add(model)
        self._db_session.flush()
