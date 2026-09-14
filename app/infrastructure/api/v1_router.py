from fastapi import APIRouter

from app.infrastructure.api.routes.login import router as login_router
from app.infrastructure.api.routes.logout import router as logout_router
from app.infrastructure.api.routes.users import router as users_router

API_V1_PREFIX = '/api/v1'

router = APIRouter(prefix=API_V1_PREFIX)
router.include_router(users_router)
router.include_router(login_router)
router.include_router(logout_router)
