from uuid import UUID

from sqlalchemy import select
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
            closed_at=session.closed_at,
        )
        self._db_session.add(model)
        self._db_session.flush()

    def find_by_user_id(self, user_id: UUID) -> Session | None:
        statement = select(SessionModel).where(SessionModel.user_id == user_id)
        model = self._db_session.execute(statement).scalar_one_or_none()
        return self._to_entity(model) if model else None

    def update(self, session: Session) -> None:
        model = self._db_session.get(SessionModel, session.id)
        if model is None:
            raise ValueError(f'Session {session.id} not found')
        model.token_id = session.token_id
        model.status = session.status
        model.created_at = session.created_at
        model.expires_at = session.expires_at
        model.closed_at = session.closed_at
        self._db_session.flush()

    @staticmethod
    def _to_entity(model: SessionModel) -> Session:
        return Session(
            id=model.id,
            user_id=model.user_id,
            token_id=model.token_id,
            status=model.status,
            created_at=model.created_at,
            expires_at=model.expires_at,
            closed_at=model.closed_at,
        )
