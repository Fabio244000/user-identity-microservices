import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.constants.messages import (
    INVALID_CREDENTIALS_MESSAGE,
    INVALID_SESSION_TOKEN_MESSAGE,
    LOGIN_NOT_ALLOWED_MESSAGE,
    UNEXPECTED_ERROR_MESSAGE,
)
from app.domain.exceptions.session_exceptions import (
    InvalidSessionTokenError,
    SessionNotFoundError,
)
from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    LoginNotAllowedError,
    UserAlreadyExistsError,
)
from app.infrastructure.api.schemas.api_response import ApiResponse

logger = logging.getLogger(__name__)

FIELD_LABELS = {
    'username': 'el nombre de usuario',
    'email': 'el correo',
    'phone': 'el celular',
}
FORMAT_ERROR_DETAILS = {
    'username': 'Debe ser alfanumérico y tener entre 9 y 50 caracteres',
    'full_name': 'Solo se permiten letras y espacios en blanco',
    'email': 'Debe tener un formato de email válido',
    'phone': 'Debe tener el formato +51 987654321',
    'password': 'Debe ser alfanumérico y tener entre 9 y 100 caracteres',
}
MISSING_FIELD_DETAIL = 'Campo obligatorio'


def _join_with_and(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    return f'{", ".join(items[:-1])} y {items[-1]}'


async def handle_user_already_exists(
    _request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    labels = [FIELD_LABELS[conflict.field] for conflict in exc.conflicts]
    verb = 'está' if len(labels) == 1 else 'están'
    message = f'{_join_with_and(labels).capitalize()} ya {verb} en uso.'
    detail = [
        {'campo': conflict.field, 'error': conflict.detail}
        for conflict in exc.conflicts
    ]
    body: ApiResponse[None] = ApiResponse(
        success=False, message=message, data=None, detail=detail
    )
    return JSONResponse(status_code=409, content=body.model_dump())


def _missing_message(fields: list[str]) -> str:
    word = 'El campo' if len(fields) == 1 else 'Los campos'
    verb = 'es obligatorio' if len(fields) == 1 else 'son obligatorios'
    return f'{word} {_join_with_and(fields)} {verb}.'


def _invalid_format_message(fields: list[str]) -> str:
    word = 'El campo' if len(fields) == 1 else 'Los campos'
    verb = (
        'no tiene el formato correcto'
        if len(fields) == 1
        else 'no tienen el formato correcto'
    )
    return f'{word} {_join_with_and(fields)} {verb}.'


def _detail_for(field: str, error_type: str) -> str:
    if error_type == 'missing':
        return MISSING_FIELD_DETAIL
    return FORMAT_ERROR_DETAILS.get(field, 'Formato inválido')


async def handle_validation_error(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    missing_fields = [
        str(error['loc'][-1]) for error in errors if error['type'] == 'missing'
    ]
    invalid_fields = [
        str(error['loc'][-1]) for error in errors if error['type'] != 'missing'
    ]

    message_parts = []
    if missing_fields:
        message_parts.append(_missing_message(missing_fields))
    if invalid_fields:
        message_parts.append(_invalid_format_message(invalid_fields))

    detail = [
        {
            'campo': str(error['loc'][-1]),
            'error': _detail_for(str(error['loc'][-1]), error['type']),
        }
        for error in errors
    ]
    body: ApiResponse[None] = ApiResponse(
        success=False, message=' '.join(message_parts), data=None, detail=detail
    )
    return JSONResponse(status_code=422, content=body.model_dump())


async def handle_invalid_credentials(
    _request: Request, _exc: InvalidCredentialsError
) -> JSONResponse:
    body: ApiResponse[None] = ApiResponse(
        success=False, message=INVALID_CREDENTIALS_MESSAGE, data=None, detail=None
    )
    return JSONResponse(status_code=400, content=body.model_dump())


async def handle_login_not_allowed(
    _request: Request, _exc: LoginNotAllowedError
) -> JSONResponse:
    body: ApiResponse[None] = ApiResponse(
        success=False, message=LOGIN_NOT_ALLOWED_MESSAGE, data=None, detail=None
    )
    return JSONResponse(status_code=400, content=body.model_dump())


async def handle_session_not_found(
    _request: Request, exc: SessionNotFoundError
) -> JSONResponse:
    logger.error('No session found for user %s', exc.user_id)
    body: ApiResponse[None] = ApiResponse(
        success=False, message=UNEXPECTED_ERROR_MESSAGE, data=None, detail=None
    )
    return JSONResponse(status_code=500, content=body.model_dump())


async def handle_invalid_session_token(
    _request: Request, _exc: InvalidSessionTokenError
) -> JSONResponse:
    body: ApiResponse[None] = ApiResponse(
        success=False, message=INVALID_SESSION_TOKEN_MESSAGE, data=None, detail=None
    )
    return JSONResponse(status_code=401, content=body.model_dump())


async def handle_unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
    body: ApiResponse[None] = ApiResponse(
        success=False,
        message=UNEXPECTED_ERROR_MESSAGE,
        data=None,
        detail=None,
    )
    return JSONResponse(status_code=500, content=body.model_dump())
