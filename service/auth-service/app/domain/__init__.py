import logging
import sys

# auth-service 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# auth-service 로거 생성
logger = logging.getLogger("auth-service")

logger.info("🔐 Auth Service Domain 모듈 초기화")
