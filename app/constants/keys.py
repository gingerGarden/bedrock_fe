"""
프론트엔드에서 사용하는 상수 키 관리 모듈.

- API 엔드포인트 URL, 세션 상태 키, 로그인 관련 키 등을 중앙에서 정의.
- 문자열 하드코딩 대신 상수를 사용하여 오타 방지 및 가독성·유지보수성 향상.
"""
from typing import Final



# Login을 위한 Key들을 정리한 객체
class LoginKey:
    """로그인 기능 및 사용자 정보(test_db.json) 관련 키."""
    USER: Final[str] = "users"
    ID: Final[str] = "id"
    PASSWD: Final[str] = "pwd"
    ROLE: Final[str] = "role"


# Login 페이지의 View들을 관리하기 위한 객체
class LoginViews:
    """로그인 페이지의 View를 컨트롤하기 위한 키"""
    KEY: Final[str] = "login_view"
    LOGIN_BEFORE: Final[str] = "login_before"
    SIGN_UP: Final[str] = "sign_up"
    PERSONAL_INFO_AGREE: Final[str] = "p_info_agree"
    LOGIN_AFTER: Final[str] = "login_after"
    EDIT: Final[str] = "edit"
    SOFT_DELETE: Final[str] = "soft_delete"


# Session 관리를 위한 Key들을 정리한 객체
class SessionKey:
    """Streamlit `st.session_state`에서 사용하는 키."""
    LOGGED_IN: Final[str] = "logged_in"         # 로그인 여부
    ID: Final[str] = "id"                       # 현재 로그인된 사용자 ID
    IS_DEVELOPER: Final[str] = "is_developer"   # 현재 로그인된 사용자 개발자 권한 여부
    IS_ADMIN: Final[str] = "is_admin"           # 현재 로그인된 사용자 관리자 권한 여부
    
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


# Signup보조 세션 키
class SignupKey:
    # Session 내 중복 여부 승인 결과가 저장되는 키
    USER_ID: Final[str] = "signup_user_id_verified"
    KTR_ID: Final[str] = "signup_ktr_id_verified"
    EMAIL: Final[str] = "signup_email_verified"
    # 중복 여부에 대한 메시지가 저장되는 키
    USER_ID_MSG: Final[str] = "signup_user_id_message"
    KTR_ID_MSG: Final[str] = "signup_ktr_id_message"
    EMAIL_MSG: Final[str] = "signup_email_message"