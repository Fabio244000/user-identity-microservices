from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.register_user import RegisterUser
from app.domain.ports.input.register_user_port import RegisterUserPort
from app.infrastructure.database.repositories.session_repository import (
    SessionRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.session import get_db
from app.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from app.infrastructure.security.jwt_token_issuer import JwtTokenIssuer
from config.settings import settings


def get_register_user(db: Session = Depends(get_db)) -> RegisterUserPort:
    return RegisterUser(
        user_repository=UserRepository(db),
        session_repository=SessionRepository(db),
        password_hasher=Argon2PasswordHasher(),
        token_issuer=JwtTokenIssuer(settings),
        session_duration_minutes=settings.session_duration_minutes,
    )
