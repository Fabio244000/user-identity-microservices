from fastapi import APIRouter, Depends, status

from app.domain.ports.input.login_user_port import LoginUserPort
from app.infrastructure.api.dependencies import get_login_user
from app.infrastructure.api.schemas.api_response import ApiResponse
from app.infrastructure.api.schemas.login_user_schema import (
    LoginUserRequest,
    LoginUserResponseData,
)

router = APIRouter(prefix='/login', tags=['login'])

LOGIN_FAILED_RESPONSE = {
    'description': 'Credenciales inválidas, o cuenta/sesión no habilitada para login',
    'content': {
        'application/json': {
            'example': {
                'success': False,
                'message': 'El username o la contraseña son incorrectos.',
                'data': None,
                'detail': None,
            }
        }
    },
}


@router.post(
    '',
    status_code=status.HTTP_200_OK,
    responses={400: LOGIN_FAILED_RESPONSE},
)
def login_user(
    body: LoginUserRequest,
    use_case: LoginUserPort = Depends(get_login_user),
) -> ApiResponse[LoginUserResponseData]:
    result = use_case.execute(username=body.username, password=body.password)
    data = LoginUserResponseData(
        username=result.user.username,
        full_name=result.user.full_name,
        status=result.user.status.value,
        email=result.user.email,
        phone=result.user.phone,
        token=result.token,
    )
    return ApiResponse(
        success=True,
        message='Inicio de sesión exitoso.',
        data=data,
        detail=None,
    )
