import os
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.core.config import settings
import uvicorn

from .observability import PrometheusMiddleware, metrics, setting_otlp

APP_NAME = settings.SERVICE_NAME
EXPOSE_PORT = settings.METRICS_PORT
OTLP_GRPC_ENDPOINT = settings.OTLP_ENDPOINT

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Setting metrics middleware
# disable otlp if testing
if os.environ.get("ENVIRONMENT") != "test":
    app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
    setting_otlp(app, APP_NAME, OTLP_GRPC_ENDPOINT)
app.add_route("/metrics", metrics)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    # update uvicorn access logger format
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT, log_config=log_config)