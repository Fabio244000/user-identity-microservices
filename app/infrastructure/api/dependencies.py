from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.close_session import CloseSession
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.domain.ports.input.close_session_port import CloseSessionPort
from app.domain.ports.input.login_user_port import LoginUserPort
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


def get_login_user(db: Session = Depends(get_db)) -> LoginUserPort:
    return LoginUser(
        user_repository=UserRepository(db),
        session_repository=SessionRepository(db),
        password_hasher=Argon2PasswordHasher(),
        token_issuer=JwtTokenIssuer(settings),
        session_duration_minutes=settings.session_duration_minutes,
    )


def get_close_session(db: Session = Depends(get_db)) -> CloseSessionPort:
    return CloseSession(
        session_repository=SessionRepository(db),
        token_issuer=JwtTokenIssuer(settings),
    )
