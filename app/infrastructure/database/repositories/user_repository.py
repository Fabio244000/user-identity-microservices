from sqlalchemy import ColumnElement, select
from sqlalchemy.orm import Session as DbSession

from app.domain.entities.user import User
from app.domain.ports.output.user_repository_port import UserRepositoryPort
from app.infrastructure.database.models import UserModel


class UserRepository(UserRepositoryPort):
    def __init__(self, db_session: DbSession) -> None:
        self._db_session = db_session

    def find_by_username(self, username: str) -> User | None:
        return self._find_one(UserModel.username == username)

    def find_by_email(self, email: str) -> User | None:
        return self._find_one(UserModel.email == email)

    def find_by_phone(self, phone: str) -> User | None:
        return self._find_one(UserModel.phone == phone)

    def save(self, user: User) -> None:
        model = UserModel(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            password_hash=user.password_hash,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self._db_session.add(model)
        self._db_session.flush()

    def _find_one(self, condition: ColumnElement[bool]) -> User | None:
        statement = select(UserModel).where(condition)
        model = self._db_session.execute(statement).scalar_one_or_none()
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            full_name=model.full_name,
            email=model.email,
            phone=model.phone,
            password_hash=model.password_hash,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
