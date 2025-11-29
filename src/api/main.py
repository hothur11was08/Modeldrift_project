from fastapi import FastAPI
from src.lib.logging import get_logger
from src.config.settings import settings

log = get_logger("api")

def create_app() -> FastAPI:
    app = FastAPI(title="Credit Risk API", version="1.0.0")

    @app.on_event("startup")
    def startup():
        log.info(f"Starting app env={settings.env}")

    from src.routes.health import router as health_router
    from src.routes.predict import router as predict_router
    from src.routes.monitor import router as monitor_router
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(predict_router, prefix="/v1", tags=["predict"])
    app.include_router(monitor_router, prefix="/v1/monitor", tags=["monitor"])
    return app

app = create_app()

