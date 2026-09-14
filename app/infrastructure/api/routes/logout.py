from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.domain.constants.messages import (
    CLOSE_SESSION_SUCCESS_MESSAGE,
    INVALID_SESSION_TOKEN_MESSAGE,
)
from app.domain.ports.input.close_session_port import CloseSessionPort
from app.infrastructure.api.dependencies import get_close_session
from app.infrastructure.api.schemas.api_response import ApiResponse

router = APIRouter(prefix='/logout', tags=['logout'])

security = HTTPBearer()

INVALID_TOKEN_RESPONSE = {
    'description': 'Token de sesión inválido, expirado o inexistente',
    'content': {
        'application/json': {
            'example': {
                'success': False,
                'message': INVALID_SESSION_TOKEN_MESSAGE,
                'data': None,
                'detail': None,
            }
        }
    },
}


@router.post(
    '',
    status_code=status.HTTP_200_OK,
    responses={401: INVALID_TOKEN_RESPONSE},
)
def close_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    use_case: CloseSessionPort = Depends(get_close_session),
) -> ApiResponse[None]:
    use_case.execute(credentials.credentials)
    return ApiResponse(
        success=True,
        message=CLOSE_SESSION_SUCCESS_MESSAGE,
        data=None,
        detail=None,
    )
