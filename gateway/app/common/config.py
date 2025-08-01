from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 서비스 디스커버리 설정
    SERVICE_DISCOVERY_TYPE: str = "consul"  # consul, redis, static
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    CONSUL_TOKEN: Optional[str] = None
    
    # Redis 설정 (서비스 디스커버리용)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 프록시 설정
    PROXY_TIMEOUT: int = 30
    PROXY_MAX_RETRIES: int = 3
    PROXY_RETRY_DELAY: float = 1.0
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 메트릭 설정
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # 서비스 매핑 (정적 설정)
    SERVICE_MAPPINGS: dict = {
        "user-service": {
            "host": "localhost",
            "port": 8001,
            "health_check": "/health"
        },
        "order-service": {
            "host": "localhost", 
            "port": 8002,
            "health_check": "/health"
        },
        "product-service": {
            "host": "localhost",
            "port": 8003,
            "health_check": "/health"
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 설정 인스턴스 생성
settings = Settings() 