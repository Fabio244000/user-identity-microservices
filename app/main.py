from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from mangum import Mangum

from app.domain.exceptions.session_exceptions import (
    InvalidSessionTokenError,
    SessionNotFoundError,
)
from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    LoginNotAllowedError,
    UserAlreadyExistsError,
)
from app.infrastructure.api.exception_handlers import (
    handle_invalid_credentials,
    handle_invalid_session_token,
    handle_login_not_allowed,
    handle_session_not_found,
    handle_unexpected_error,
    handle_user_already_exists,
    handle_validation_error,
)
from app.infrastructure.api.routes.health import router as health_router
from app.infrastructure.api.v1_router import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(title='User Identity Service')
    app.include_router(health_router)
    app.include_router(v1_router)
    app.add_exception_handler(UserAlreadyExistsError, handle_user_already_exists)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidCredentialsError, handle_invalid_credentials)  # type: ignore[arg-type]
    app.add_exception_handler(LoginNotAllowedError, handle_login_not_allowed)  # type: ignore[arg-type]
    app.add_exception_handler(SessionNotFoundError, handle_session_not_found)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidSessionTokenError, handle_invalid_session_token)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, handle_unexpected_error)
    return app


app = create_app()
handler = Mangum(app)
