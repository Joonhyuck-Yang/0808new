import asyncio
import aiohttp
import redis.asyncio as redis
import consul
import structlog
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from app.common.config import settings


logger = structlog.get_logger()


@dataclass
class ServiceInstance:
    """서비스 인스턴스 정보"""
    service_name: str
    host: str
    port: int
    health_check_url: str
    metadata: Dict[str, Any] = None
    is_healthy: bool = True
    last_health_check: float = 0.0


class ServiceDiscovery:
    """서비스 디스커버리 클래스"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.consul_client: Optional[consul.Consul] = None
        self.redis_client: Optional[redis.Redis] = None
        self.health_check_interval = 30  # 30초마다 헬스체크
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """서비스 디스커버리 초기화"""
        logger.info("Initializing service discovery", type=settings.SERVICE_DISCOVERY_TYPE)
        
        if settings.SERVICE_DISCOVERY_TYPE == "consul":
            await self._initialize_consul()
        elif settings.SERVICE_DISCOVERY_TYPE == "redis":
            await self._initialize_redis()
        elif settings.SERVICE_DISCOVERY_TYPE == "static":
            await self._initialize_static()
        else:
            raise ValueError(f"Unsupported service discovery type: {settings.SERVICE_DISCOVERY_TYPE}")
        
        # 헬스체크 태스크 시작
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Service discovery initialized successfully")
    
    async def _initialize_consul(self):
        """Consul 클라이언트 초기화"""
        try:
            self.consul_client = consul.Consul(
                host=settings.CONSUL_HOST,
                port=settings.CONSUL_PORT,
                token=settings.CONSUL_TOKEN
            )
            logger.info("Consul client initialized")
        except Exception as e:
            logger.error("Failed to initialize Consul client", error=str(e))
            raise
    
    async def _initialize_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error("Failed to initialize Redis client", error=str(e))
            raise
    
    async def _initialize_static(self):
        """정적 서비스 매핑 초기화"""
        for service_name, config in settings.SERVICE_MAPPINGS.items():
            instance = ServiceInstance(
                service_name=service_name,
                host=config["host"],
                port=config["port"],
                health_check_url=config["health_check"],
                metadata=config.get("metadata", {})
            )
            self.services[service_name] = [instance]
        
        logger.info("Static service mapping initialized", services=list(self.services.keys()))
    
    async def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """서비스 인스턴스 목록 조회"""
        if settings.SERVICE_DISCOVERY_TYPE == "consul":
            return await self._get_consul_instances(service_name)
        elif settings.SERVICE_DISCOVERY_TYPE == "redis":
            return await self._get_redis_instances(service_name)
        else:
            return self.services.get(service_name, [])
    
    async def _get_consul_instances(self, service_name: str) -> List[ServiceInstance]:
        """Consul에서 서비스 인스턴스 조회"""
        try:
            _, services = self.consul_client.catalog.service(service_name)
            instances = []
            
            for service in services:
                instance = ServiceInstance(
                    service_name=service_name,
                    host=service["ServiceAddress"] or service["Address"],
                    port=service["ServicePort"],
                    health_check_url=f"/health",
                    metadata=service.get("ServiceMeta", {})
                )
                instances.append(instance)
            
            return instances
        except Exception as e:
            logger.error("Failed to get Consul instances", service=service_name, error=str(e))
            return []
    
    async def _get_redis_instances(self, service_name: str) -> List[ServiceInstance]:
        """Redis에서 서비스 인스턴스 조회"""
        try:
            service_key = f"service:{service_name}"
            instances_data = await self.redis_client.hgetall(service_key)
            
            instances = []
            for instance_id, instance_data in instances_data.items():
                # JSON 파싱 로직 필요
                # 임시로 간단한 구현
                host, port = instance_data.split(":")
                instance = ServiceInstance(
                    service_name=service_name,
                    host=host,
                    port=int(port),
                    health_check_url="/health"
                )
                instances.append(instance)
            
            return instances
        except Exception as e:
            logger.error("Failed to get Redis instances", service=service_name, error=str(e))
            return []
    
    async def _health_check_loop(self):
        """헬스체크 루프"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """모든 서비스에 대한 헬스체크 수행"""
        for service_name, instances in self.services.items():
            for instance in instances:
                await self._check_instance_health(instance)
    
    async def _check_instance_health(self, instance: ServiceInstance):
        """개별 인스턴스 헬스체크"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{instance.host}:{instance.port}{instance.health_check_url}"
                async with session.get(url, timeout=5) as response:
                    instance.is_healthy = response.status == 200
                    instance.last_health_check = asyncio.get_event_loop().time()
        except Exception as e:
            instance.is_healthy = False
            logger.warning("Health check failed", service=instance.service_name, host=instance.host, error=str(e))
    
    async def cleanup(self):
        """리소스 정리"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Service discovery cleanup completed") 