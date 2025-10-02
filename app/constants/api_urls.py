from typing import Final

from app.core.config import (
    BACKEND_GPU_URL, BACKEND_WEB_URL, 
    BACKEND_GPU_VERSION, BACKEND_WEB_VERSION
)



# Chat API URL의 모음
class ChatAPIKeys:
    """백엔드 Chat API 엔드포인트 URL."""
    _BASE: Final[str] = f"{BACKEND_GPU_URL}/{BACKEND_GPU_VERSION}"

    # --- Base ---
    PING: Final[str] = f"{_BASE}/base/ping"
    MODEL_LIST: Final[str] = f"{_BASE}/base/model_list"
    DEFAULT_MODEL: Final[str] = f"{_BASE}/base/default_model"

    # --- Chat ---
    CHAT: Final[str] = f"{_BASE}/chat/web"
    CHAT_WITH_META: Final[str] = f"{_BASE}/chat/web_with_meta"


# Login API URL의 모음
class LoginAPIKeys:
    """백엔드 Login API 엔드포인트 URL."""
    _BASE: Final[str] = f"{BACKEND_WEB_URL}/{BACKEND_WEB_VERSION}/login"

    # 1. 로그인 - 아이디와 패스워드 일치 확인
    VERIFY_ID: Final[str] = f"{_BASE}/verify"

    # 2. 회원가입
    # 중복 키(ID/사번/email) 체크
    VERIFY_UNIQUE_KEY: Final[str] = f"{_BASE}/verify_unique_key"
    # 계정 추가
    ADD_USER: Final[str] = f"{_BASE}/add_user"

