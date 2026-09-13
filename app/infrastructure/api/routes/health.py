from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.api.schemas.api_response import ApiResponse
from app.infrastructure.database.session import get_db

router = APIRouter(tags=['health'])


@router.get('/health')
def check_health(db: Session = Depends(get_db)) -> ApiResponse[dict[str, str]]:
    db.execute(text('SELECT 1'))
    return ApiResponse(
        success=True,
        message='El servicio está operativo.',
        data={'database': 'ok'},
    )
