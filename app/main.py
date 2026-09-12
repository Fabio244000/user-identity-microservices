from fastapi import FastAPI
from mangum import Mangum

from app.infrastructure.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title='User Identity Service')
    app.include_router(health_router)
    return app


app = create_app()
handler = Mangum(app)
