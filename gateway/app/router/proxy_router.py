from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
import structlog
from typing import Dict, Any

from app.domain.proxy_service import ProxyService
from app.common.config import settings

logger = structlog.get_logger()
proxy_router = APIRouter()


def get_proxy_service(request: Request) -> ProxyService:
    """프록시 서비스 의존성 주입"""
    return request.app.state.proxy_service


@proxy_router.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """모든 서비스 요청을 프록시"""
    try:
        # 서비스 이름 검증
        if service_name not in settings.SERVICE_MAPPINGS:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        # 프록시 요청 실행
        response = await proxy_service.proxy_request(request, service_name, f"/{path}")
        
        # 응답 스트리밍
        async def generate():
            async for chunk in response.aiter_bytes():
                yield chunk
        
        return StreamingResponse(
            generate(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Proxy request failed", service=service_name, path=path, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@proxy_router.get("/{service_name}")
async def proxy_root_request(
    service_name: str,
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """서비스 루트 경로 프록시"""
    return await proxy_request(service_name, "", request, proxy_service)


@proxy_router.get("/services/{service_name}/health")
async def service_health_check(
    service_name: str,
    proxy_service: ProxyService = Depends(get_proxy_service)
) -> Dict[str, Any]:
    """서비스 헬스체크"""
    return await proxy_service.health_check(service_name)


@proxy_router.get("/services/{service_name}/info")
async def service_info(
    service_name: str,
    proxy_service: ProxyService = Depends(get_proxy_service)
) -> Dict[str, Any]:
    """서비스 정보 조회"""
    return await proxy_service.get_service_info(service_name)


@proxy_router.get("/services")
async def list_services() -> Dict[str, Any]:
    """등록된 서비스 목록 조회"""
    return {
        "services": list(settings.SERVICE_MAPPINGS.keys()),
        "service_discovery_type": settings.SERVICE_DISCOVERY_TYPE
    } 