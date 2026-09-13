from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from mangum import Mangum

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.infrastructure.api.exception_handlers import (
    handle_unexpected_error,
    handle_user_already_exists,
    handle_validation_error,
)
from app.infrastructure.api.routes.health import router as health_router
from app.infrastructure.api.routes.users import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title='User Identity Service')
    app.include_router(health_router)
    app.include_router(users_router)
    app.add_exception_handler(UserAlreadyExistsError, handle_user_already_exists)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, handle_unexpected_error)
    return app


app = create_app()
handler = Mangum(app)
