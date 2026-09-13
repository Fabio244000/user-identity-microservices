from fastapi import APIRouter, Depends, status

from app.domain.ports.input.register_user_port import RegisterUserPort
from app.infrastructure.api.dependencies import get_register_user
from app.infrastructure.api.schemas.api_response import ApiResponse
from app.infrastructure.api.schemas.register_user_schema import (
    RegisterUserRequest,
    RegisterUserResponseData,
)

router = APIRouter(prefix='/api/v1/users', tags=['users'])

CONFLICT_RESPONSE = {
    'description': 'Username, email o phone ya registrados',
    'content': {
        'application/json': {
            'example': {
                'success': False,
                'message': 'El nombre de usuario ya está en uso.',
                'data': None,
                'detail': [
                    {
                        'campo': 'username',
                        'error': 'Ya existe un usuario con este username',
                    }
                ],
            }
        }
    },
}


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    responses={409: CONFLICT_RESPONSE},
)
def register_user(
    body: RegisterUserRequest,
    use_case: RegisterUserPort = Depends(get_register_user),
) -> ApiResponse[RegisterUserResponseData]:
    result = use_case.execute(
        username=body.username,
        full_name=body.full_name,
        email=body.email,
        password=body.password,
        phone=body.phone,
    )
    data = RegisterUserResponseData(
        username=result.user.username,
        full_name=result.user.full_name,
        status=result.user.status.value,
        email=result.user.email,
        phone=result.user.phone,
        token=result.token,
    )
    return ApiResponse(
        success=True,
        message='Usuario registrado correctamente',
        data=data,
        detail=None,
    )
