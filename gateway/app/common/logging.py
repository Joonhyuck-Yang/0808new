import structlog
import logging
import sys
from typing import Any, Dict


def setup_logging() -> None:
    """구조화된 로깅 설정"""
    
    # 기본 로깅 설정
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # structlog 설정
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """로거 인스턴스 반환"""
    return structlog.get_logger(name)


def log_request(request_data: Dict[str, Any]) -> None:
    """요청 로깅"""
    logger = get_logger("gateway.request")
    logger.info("Incoming request", **request_data)


def log_response(response_data: Dict[str, Any]) -> None:
    """응답 로깅"""
    logger = get_logger("gateway.response")
    logger.info("Outgoing response", **response_data)


def log_error(error_data: Dict[str, Any]) -> None:
    """에러 로깅"""
    logger = get_logger("gateway.error")
    logger.error("Error occurred", **error_data) 