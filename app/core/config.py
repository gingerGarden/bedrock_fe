from typing import Final

# 백엔드 API 서버 기본 URL
# - 개발: localhost
# - 배포: 내부망 IP 또는 도메인으로 변경
BACKEND_GPU_URL: Final[str] = "http://localhost:8030"
BACKEND_WEB_URL: Final[str] = "http://localhost:7030"


# 백엔드 API 버전 (엔드포인트 버전 관리용)
BACKEND_GPU_VERSION: str = "v0"
BACKEND_WEB_VERSION: str = "v0"


