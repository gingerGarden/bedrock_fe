"""
백엔드 API 엔드포인트 URL 상수 정의 모듈.

이 모듈은 프론트엔드(Streamlit 등)에서 백엔드(FastAPI)로 요청을 보낼 때 사용하는
API 엔드포인트(URL)를 중앙집중적으로 관리한다.

주요 목적
----------
- URL 문자열 하드코딩 방지
- 환경별(API Gateway, GPU/WEB 분리) 백엔드 URL 일관성 유지
- 버전 관리(BACKEND_WEB_VERSION, BACKEND_GPU_VERSION) 반영
- 유지보수성 및 코드 가독성 향상

구성
----
- LoginAPIKeys : 사용자 인증·회원관리 관련 API URL
- ChatAPIKeys  : LLM 기반 채팅/모델 조회 관련 API URL
"""
from typing import Final

from app.core.config import (
    BACKEND_GPU_URL, BACKEND_WEB_URL, 
    BACKEND_GPU_VERSION, BACKEND_WEB_VERSION
)



# ============================================================
# 로그인 / 회원가입 / 계정관리 관련 API URL
# ============================================================
class LoginAPIKeys:
    """
    백엔드 Login API 엔드포인트 URL 정의 클래스.

    구성
    ----
    - 로그인(ID/PW 검증)
    - 회원가입(중복 확인, 계정 생성)
    - 사용자 정보 수정(비밀번호 변경, 이메일 변경, 계정 정지 등)

    모든 엔드포인트는 WEB 백엔드(`BACKEND_WEB_URL`)를 기반으로 함.
    """

    # 공통 URL prefix (예: http://127.0.0.1:8001/v1/login)
    _BASE: Final[str] = f"{BACKEND_WEB_URL}/{BACKEND_WEB_VERSION}/login"

    # --- 1. 로그인 ---
    VERIFY_ID: Final[str] = f"{_BASE}/verify"
    """로그인 검증 API — ID/비밀번호 일치 여부 확인."""

    # --- 2. 회원가입 ---
    VERIFY_UNIQUE_KEY: Final[str] = f"{_BASE}/verify_unique_key"
    """회원가입 시 유니크 키(user_id / ktr_id / email) 중복 검사 API."""
    ADD_USER: Final[str] = f"{_BASE}/add_user"
    """신규 사용자 계정 생성 API."""

    # --- 3. 회원 정보 수정 / 자기계정 관리 ---
    SELF_BLOCK: Final[str] = f"{_BASE}/self_block"
    """사용자 본인이 자신의 계정을 Soft Delete(사용 중지) 요청하는 API."""
    SELF_UPDATE: Final[str] = f"{_BASE}/self_update"
    """사용자 본인이 자신의 계정 정보를 수정하는 API."""



# ============================================================
# 관리자 권한 관련 API URL
# ============================================================
class AdminAPIKeys:
    _BASE: Final[str] = f"{BACKEND_WEB_URL}/{BACKEND_WEB_VERSION}/admin"

    # --- 1. 조회 ---
    GET_ALL_USERS: Final[str] = f"{_BASE}/search_all"

    # --- 2. 다수 이용자 변경 ---
    # 승인/승인해제
    BULK_SIGNUP: Final[str] = f"{_BASE}/signup"
    # 정지/복원
    BULK_BLOCK: Final[str] = f"{_BASE}/block"
    # 완전 삭제
    BULK_DELETE: Final[str] = f"{_BASE}/delete"

    # --- 3. 단일 이용자 비밀번호 변경 ---
    SINGLE_RESET_PWD: Final[str] = f"{_BASE}/reset_pwd"



# ============================================================
# GPU 백엔드 (Chat / Model 관련) API URL
# ============================================================
class ChatAPIKeys:
    """
    백엔드 Chat API 엔드포인트 URL 정의 클래스.

    구성
    ----
    - LLM 채팅/질의응답
    - 모델 리스트 및 기본 모델 조회
    - 백엔드 상태 점검(Ping)

    모든 엔드포인트는 GPU 백엔드(`BACKEND_GPU_URL`)를 기반으로 함.
    """
    # 공통 URL prefix (예: http://127.0.0.1:8002/v1)
    _BASE: Final[str] = f"{BACKEND_GPU_URL}/{BACKEND_GPU_VERSION}"

    # --- Base (기본 기능) ---
    PING: Final[str] = f"{_BASE}/base/ping"
    """서버 연결 상태 확인용 Ping API."""
    MODEL_LIST: Final[str] = f"{_BASE}/base/model_list"
    """현재 GPU 서버에 로드된 모델 리스트 조회 API."""
    DEFAULT_MODEL: Final[str] = f"{_BASE}/base/default_model"
    """기본(default) 모델 정보 조회 API."""

    # --- Chat ---
    CHAT: Final[str] = f"{_BASE}/chat/web"
    """단순 대화용 채팅 API — 일반 LLM 질의응답."""
    CHAT_WITH_META: Final[str] = f"{_BASE}/chat/web_with_meta"
    """메타데이터 기반 채팅 API — 대화 기록, 출처 정보 등 포함."""
