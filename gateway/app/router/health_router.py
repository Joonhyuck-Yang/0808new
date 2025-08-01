from fastapi import APIRouter, Request
from typing import Dict, Any
import structlog
import time

logger = structlog.get_logger()
health_router = APIRouter()


@health_router.get("/")
async def health_check() -> Dict[str, Any]:
    """기본 헬스체크"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "api-gateway"
    }


@health_router.get("/ready")
async def readiness_check(request: Request) -> Dict[str, Any]:
    """준비 상태 체크"""
    try:
        # 서비스 디스커버리 상태 확인
        service_discovery = getattr(request.app.state, 'service_discovery', None)
        proxy_service = getattr(request.app.state, 'proxy_service', None)
        
        if not service_discovery or not proxy_service:
            return {
                "status": "not_ready",
                "reason": "Services not initialized",
                "timestamp": time.time()
            }
        
        return {
            "status": "ready",
            "timestamp": time.time(),
            "service_discovery": "initialized",
            "proxy_service": "initialized"
        }
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {
            "status": "not_ready",
            "reason": str(e),
            "timestamp": time.time()
        }


@health_router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """생존 상태 체크"""
    return {
        "status": "alive",
        "timestamp": time.time()
    } 