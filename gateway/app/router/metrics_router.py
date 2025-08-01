from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge
import structlog

logger = structlog.get_logger()
metrics_router = APIRouter()

# 메트릭 정의
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total number of requests',
    ['method', 'service', 'status_code']
)

REQUEST_DURATION = Histogram(
    'gateway_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'service']
)

ACTIVE_CONNECTIONS = Gauge(
    'gateway_active_connections',
    'Number of active connections'
)

SERVICE_HEALTH = Gauge(
    'gateway_service_health',
    'Service health status (1=healthy, 0=unhealthy)',
    ['service']
)


@metrics_router.get("/")
async def metrics():
    """Prometheus 메트릭 엔드포인트"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def record_request_metric(method: str, service: str, status_code: int, duration: float):
    """요청 메트릭 기록"""
    REQUEST_COUNT.labels(method=method, service=service, status_code=status_code).inc()
    REQUEST_DURATION.labels(method=method, service=service).observe(duration)


def update_service_health(service: str, is_healthy: bool):
    """서비스 헬스 메트릭 업데이트"""
    SERVICE_HEALTH.labels(service=service).set(1 if is_healthy else 0) 