"""
LandSense AI - IoT + MCP Service
Application entrypoint. Wires together config, logging, providers,
services, middleware, and routers. This is the ONLY file that performs
this wiring - no other module should construct providers or services.
"""

from fastapi import FastAPI

from config.settings import get_settings
from config.logging_config import setup_logging
from adapters.factory import build_sensor_provider, build_rera_provider
from services.sensor_service import SensorService
from services.rera_service import RERAService
from services.project_service import ProjectService
from services.status_service import StatusService
from middleware.logging_middleware import LoggingMiddleware
from utils.exceptions import register_exception_handlers

from routes import sensor_routes, project_routes, rera_routes, status_routes


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title="LandSense AI - IoT + MCP Service",
        description="IoT sensor and RERA data module for LandSense AI",
        version="1.0.0",
    )

    # --- Build providers once, at startup, via the factory ---
    sensor_provider = build_sensor_provider(settings)
    rera_provider = build_rera_provider(settings)

    # --- Construct services with injected providers ---
    sensor_service = SensorService(provider=sensor_provider)
    rera_service = RERAService(provider=rera_provider)
    project_service = ProjectService(rera_provider=rera_provider)
    status_service = StatusService(
        sensor_provider=sensor_provider,
        rera_provider=rera_provider,
        settings=settings,
    )

    # --- Store singletons on app.state for route-level access ---
    app.state.sensor_service = sensor_service
    app.state.rera_service = rera_service
    app.state.project_service = project_service
    app.state.status_service = status_service

    # --- Middleware ---
    app.add_middleware(LoggingMiddleware)

    # --- Exception handlers (no raw stack traces to clients) ---
    register_exception_handlers(app)

    # --- Routers ---
    app.include_router(sensor_routes.router)
    app.include_router(project_routes.router)
    app.include_router(rera_routes.router)
    app.include_router(status_routes.router)

    return app


app = create_app()