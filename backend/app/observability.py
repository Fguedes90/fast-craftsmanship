import time
import random
from dataclasses import dataclass

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from prometheus_client.openmetrics.exposition import generate_latest
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.types import ASGIApp

@dataclass
class MetricsConfig:
    """Configuration class for Prometheus metrics"""
    app_info: Gauge = Gauge("fastapi_app_info", "FastAPI application information.", ["app_name"])
    requests: Counter = Counter("fastapi_requests_total", "Total count of requests by method and path.", ["method", "path", "app_name"])
    responses: Counter = Counter("fastapi_responses_total", "Total count of responses by method, path and status codes.", ["method", "path", "status_code", "app_name"])
    requests_processing_time: Histogram = Histogram("fastapi_requests_duration_seconds", "Histogram of requests processing time by path (in seconds)", ["method", "path", "app_name"])
    exceptions: Counter = Counter("fastapi_exceptions_total", "Total count of exceptions raised by path and exception type", ["method", "path", "exception_type", "app_name"])
    requests_in_progress: Gauge = Gauge("fastapi_requests_in_progress", "Gauge of requests by method and path currently being processed", ["method", "path", "app_name"])

class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, app_name: str = "backend") -> None:
        super().__init__(app)
        self.app_name = app_name
        self.metrics = MetricsConfig()
        self.metrics.app_info.labels(app_name=self.app_name).inc()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path, _ = self._get_path(request)  # Track metrics for all paths
        
        return await self._handle_request(method, path, request, call_next)

    async def _handle_request(self, method: str, path: str, request: Request, call_next: RequestResponseEndpoint) -> Response:
        self._update_request_metrics(method, path)
        before_time = time.perf_counter()
        status_code = 500  # Default status for unhandled exceptions

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            self._handle_exception(method, path, e)
            if hasattr(e, "status_code"):  # Use exception status code if available
                status_code = e.status_code
            raise
        else:
            self._record_request_duration(method, path, before_time)
            return response
        finally:
            self._update_response_metrics(method, path, status_code)

    def _update_request_metrics(self, method: str, path: str) -> None:
        labels = {"method": method, "path": path, "app_name": self.app_name}
        self.metrics.requests_in_progress.labels(**labels).inc()
        self.metrics.requests.labels(**labels).inc()

    def _handle_exception(self, method: str, path: str, exception: BaseException) -> None:
        self.metrics.exceptions.labels(
            method=method,
            path=path,
            exception_type=type(exception).__name__,
            app_name=self.app_name
        ).inc()

    def _record_request_duration(self, method: str, path: str, start_time: float) -> None:
        duration = time.perf_counter() - start_time
        trace_id = trace.format_trace_id(trace.get_current_span().get_span_context().trace_id)
        # Add small random delay to prevent timestamp collisions
        time.sleep(random.uniform(0.001, 0.010))  # 1-10ms jitter
        self.metrics.requests_processing_time.labels(
            method=method,
            path=path,
            app_name=self.app_name
        ).observe(duration, exemplar={'TraceID': trace_id})

    def _update_response_metrics(self, method: str, path: str, status_code: int) -> None:
        self.metrics.responses.labels(
            method=method,
            path=path,
            status_code=status_code,
            app_name=self.app_name
        ).inc()
        self.metrics.requests_in_progress.labels(
            method=method,
            path=path,
            app_name=self.app_name
        ).dec()

    @staticmethod
    def _get_path(request: Request) -> tuple[str, bool]:
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True
        return request.url.path, False

def metrics(request: Request) -> Response:
    return Response(
        generate_latest(REGISTRY),
        headers={"Content-Type": "text/plain; version=0.0.4; charset=utf-8"}
    )

def setting_otlp(app: ASGIApp, app_name: str, endpoint: str, log_correlation: bool = True) -> None:
    from app.core.config import settings

    if not settings.ENABLE_TRACING:
        trace.set_tracer_provider(None)
        return

    resource = Resource.create(attributes={
        "service.name": app_name,
        "compose_service": app_name
    })

    tracer = TracerProvider(resource=resource)

    if settings.ENVIRONMENT != "test":
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint, timeout=30)
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer)

    if log_correlation:
        LoggingInstrumentor().instrument(set_logging_format=True)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
