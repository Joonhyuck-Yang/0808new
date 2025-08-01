import httpx
import asyncio
import random
import structlog
from typing import Dict, List, Optional, Any
from fastapi import Request, HTTPException
from app.domain.service_discovery import ServiceDiscovery, ServiceInstance
from app.common.config import settings


logger = structlog.get_logger()


class ProxyService:
    """프록시 서비스 클래스"""
    
    def __init__(self, service_discovery: ServiceDiscovery):
        self.service_discovery = service_discovery
        self.client = httpx.AsyncClient(timeout=settings.PROXY_TIMEOUT)
    
    async def proxy_request(self, request: Request, service_name: str, path: str = "") -> httpx.Response:
        """요청을 대상 서비스로 프록시"""
        try:
            # 서비스 인스턴스 조회
            instances = await self.service_discovery.get_service_instances(service_name)
            
            if not instances:
                logger.error("No available instances found", service=service_name)
                raise HTTPException(status_code=503, detail=f"Service {service_name} is not available")
            
            # 헬시한 인스턴스만 필터링
            healthy_instances = [inst for inst in instances if inst.is_healthy]
            
            if not healthy_instances:
                logger.error("No healthy instances found", service=service_name)
                raise HTTPException(status_code=503, detail=f"Service {service_name} is not healthy")
            
            # 로드 밸런싱 (라운드 로빈)
            selected_instance = self._select_instance(healthy_instances)
            
            # 프록시 요청 실행
            return await self._execute_proxy_request(request, selected_instance, path)
            
        except httpx.RequestError as e:
            logger.error("Proxy request failed", service=service_name, error=str(e))
            raise HTTPException(status_code=502, detail="Bad gateway")
        except Exception as e:
            logger.error("Unexpected error in proxy", service=service_name, error=str(e))
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """로드 밸런싱을 위한 인스턴스 선택"""
        # 간단한 라운드 로빈 구현
        # 실제로는 더 정교한 로드 밸런싱 알고리즘 사용 가능
        return random.choice(instances)
    
    async def _execute_proxy_request(
        self, 
        request: Request, 
        instance: ServiceInstance, 
        path: str
    ) -> httpx.Response:
        """실제 프록시 요청 실행"""
        # 대상 URL 구성
        target_url = f"http://{instance.host}:{instance.port}{path}"
        
        # 요청 헤더 준비
        headers = dict(request.headers)
        # 호스트 헤더 제거 (대상 서비스가 처리하도록)
        headers.pop("host", None)
        
        # 요청 바디 준비
        body = await request.body()
        
        # HTTP 메서드에 따른 요청 실행
        method = request.method.lower()
        
        logger.info(
            "Proxying request",
            method=method,
            target_url=target_url,
            service=instance.service_name,
            instance_host=instance.host,
            instance_port=instance.port
        )
        
        if method == "get":
            return await self.client.get(target_url, headers=headers, params=request.query_params)
        elif method == "post":
            return await self.client.post(target_url, headers=headers, content=body)
        elif method == "put":
            return await self.client.put(target_url, headers=headers, content=body)
        elif method == "delete":
            return await self.client.delete(target_url, headers=headers)
        elif method == "patch":
            return await self.client.patch(target_url, headers=headers, content=body)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
    
    async def health_check(self, service_name: str) -> Dict[str, Any]:
        """서비스 헬스체크"""
        try:
            instances = await self.service_discovery.get_service_instances(service_name)
            
            health_status = {
                "service": service_name,
                "total_instances": len(instances),
                "healthy_instances": len([inst for inst in instances if inst.is_healthy]),
                "instances": []
            }
            
            for instance in instances:
                instance_status = {
                    "host": instance.host,
                    "port": instance.port,
                    "healthy": instance.is_healthy,
                    "last_health_check": instance.last_health_check
                }
                health_status["instances"].append(instance_status)
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", service=service_name, error=str(e))
            return {
                "service": service_name,
                "error": str(e),
                "status": "unhealthy"
            }
    
    async def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """서비스 정보 조회"""
        try:
            instances = await self.service_discovery.get_service_instances(service_name)
            
            return {
                "service": service_name,
                "instances": [
                    {
                        "host": inst.host,
                        "port": inst.port,
                        "healthy": inst.is_healthy,
                        "metadata": inst.metadata
                    }
                    for inst in instances
                ]
            }
            
        except Exception as e:
            logger.error("Failed to get service info", service=service_name, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to get service information")
    
    async def close(self):
        """리소스 정리"""
        await self.client.aclose() 