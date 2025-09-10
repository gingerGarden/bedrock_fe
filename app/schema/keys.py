"""
프론트엔드에서 사용하는 상수 키 관리 모듈.

- API 엔드포인트 URL, 세션 상태 키, 로그인 관련 키 등을 중앙에서 정의.
- 문자열 하드코딩 대신 상수를 사용하여 오타 방지 및 가독성·유지보수성 향상.
"""
from typing import Final
from app.core.config import BACKEND_GPU_URL, BACKEND_VERSION



# Login을 위한 Key들을 정리한 객체
class LoginKey:
    """로그인 기능 및 사용자 정보(test_db.json) 관련 키."""
    USER: Final[str] = "users"
    ID: Final[str] = "id"
    PASSWD: Final[str] = "pwd"
    ROLE: Final[str] = "role"


# Session 관리를 위한 Key들을 정리한 객체
class SessionKey:
    """Streamlit `st.session_state`에서 사용하는 키."""
    LOGGED_IN: Final[str] = "logged_in"         # 로그인 여부
    ID: Final[str] = "id"                       # 현재 로그인된 사용자 ID
    ROLE: Final[str] = "role"                   # 현재 로그인된 사용자 권한
    
    MESSAGE: Final[str] = "message"             # 채팅 대화 기록
    STREAMING: Final[str] = "streaming"         # 현재 LLM 응답 스트리밍 진행 여부

    MODEL_LIST: Final[str] = "model_list"       # 백엔드에서 가져온 사용 가능 모델 목록
    MODEL: Final[str] = "model"                 # 현재 사용자가 선택한 모델
    MODEL_IDX: Final[str] = "model_number"      # 모델 목록에서 현재 선택된 모델의 인덱스


# streamlit chat의 키
class StreamLitChatKey:
    """`st.chat_message` 위젯에서 사용하는 키."""
    ROLE: Final[str] = "role"
    CONTENT: Final[str] = "content"


# API URL의 모음
class APIKey:
    """백엔드 API 엔드포인트 URL."""
    _BASE: Final[str] = f"{BACKEND_GPU_URL}/{BACKEND_VERSION}"

    # --- Base ---
    PING: Final[str] = f"{_BASE}/base/ping"
    MODEL_LIST: Final[str] = f"{_BASE}/base/model_list"
    DEFAULT_MODEL: Final[str] = f"{_BASE}/base/default_model"

    # --- Chat ---
    CHAT: Final[str] = f"{_BASE}/chat/web"
    CHAT_WITH_META: Final[str] = f"{_BASE}/chat/web_with_meta"