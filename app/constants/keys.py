"""
프론트엔드에서 사용하는 상수 키 관리 모듈.

이 모듈은 Streamlit 기반 프론트엔드가 백엔드(FastAPI)와 상호작용할 때
공통적으로 참조하는 키(key) 문자열을 중앙집중적으로 관리한다.

주요 목적
----------
- 문자열 하드코딩으로 인한 오타 방지
- View 전환, 세션 상태, 입력 필드 등에서 일관된 키 사용
- 유지보수 및 코드 가독성 향상

구성
----
- LoginViews        : 로그인 관련 View 구분용 키
- SessionKey        : Streamlit 세션 상태(`st.session_state`)용 키
- StreamLitChatKey  : Streamlit `st.chat_message` 위젯용 키
- SignupKey         : 회원가입 시 중복 확인 상태/메시지용 키
"""
from typing import Final



# ============================================================
# Streamlit 세션 상태 관리용 키
# ============================================================
class SessionKey:
    """
    Streamlit의 `st.session_state` 내에서 사용하는 표준 키.

    모든 페이지 간 공유되는 전역 상태로,
    로그인 여부, 사용자 정보, 모델 선택 정보 등을 포함한다.
    """
    # --- 로그인 상태/사용자 정보 ---
    LOGGED_IN: Final[str] = "logged_in"             # 로그인 여부(bool)
    ID: Final[str] = "id"                           # 현재 로그인된 사용자 ID
    USER_IDX: Final[int] = "user_idx"               # 사용자 index(DB)
    USER_NAME: Final[str] = "user_name"             # 사용자 이름(별명)
    KTR_ID: Final[str] = "ktr_id"                   # 사용자 사번
    EMAIL: Final[str] = "email"                     # 사용자 이메일
    IS_DEVELOPER: Final[str] = "is_developer"       # 개발자 권한 여부
    IS_ADMIN: Final[str] = "is_admin"               # 관리자 권한 여부
    
    # --- 대화/스트리밍 ---
    MESSAGE: Final[str] = "message"                 # 채팅 대화 기록
    STREAMING: Final[str] = "streaming"             # 현재 LLM 응답 스트리밍 여부
    STOP_STREAM: Final[str] = "stop_stream"         # LLM 응답 스트리밍 정지 여부
    TEMP_RESPONSE: Final[str] = "temp_response"     # 응답 중단 시 복구용 임시 저장소

    # --- 모델 관련 ---
    MODEL_LIST: Final[str] = "model_list"           # 사용 가능 모델 목록
    MODEL: Final[str] = "model"                     # 현재 선택된 모델 이름
    MODEL_IDX: Final[str] = "model_number"          # 모델 목록에서 선택된 인덱스

    
# Flash 사용을 위한 키
class FlashKeys:
    # admin 페이지의 Table 조작 로그가 출력되는 Flash
    ADMIN_TABLE: Final[str] = "flash_admin_table_box"


# ============================================================
# 사용자 정보 키
# ============================================================
class UserInfo:
    """
    로그인 성공 시 백엔드로부터 전달받는 사용자 정보 딕셔너리의 키 모음.

    각 값은 SessionState 또는 API 파서(`Status200.verify_login`)에서도 동일하게 사용된다.
    """
    USER_NAME: Final[str] = "user_name"         # 사용자 표시명 (닉네임)
    KTR_ID: Final[str] = "ktr_id"               # 기관 사번
    EMAIL: Final[str] = "email"                 # 이메일 주소
    DEVELOPER: Final[str] = "developer"         # 개발자 계정 여부 (bool)
    ADMIN: Final[str] = "admin"                 # 관리자 계정 여부 (bool)


class UserUpdateInfo:
    """
    사용자 정보 수정 API(`/self_update`) 응답에서 사용하는 키 모음.

    변경 가능한 필드만 정의되어 있으며,
    업데이트 후 UI에 반영되는 최소 필드를 지정한다.
    """
    USER_NAME: Final[str] = "user_name"         # 변경된 사용자 이름
    EMAIL: Final[str] = "email"                 # 변경된 이메일


# Admin - 사용자 조회 키 (Table 주요 속성)
class UsersRecord:
    """
    Users Table로부터 사용자 정보 전달 시, Record의 키
    """
    user_id: Final[str] = "user_id"
    ktr_id: Final[str] = "ktr_id"
    user_name: Final[str] = "user_name"
    email: Final[str] = "email"
    developer: Final[str] = "developer"
    admin: Final[str] = "admin"
    signup: Final[str] = "signup"
    idx: Final[str] = "idx"
    created_at: Final[str] = "created_at"
    updated_at: Final[str] = "updated_at"
    signup_at: Final[str] = "signup_at"
    deleted_at: Final[str] = "deleted_at"



# ============================================================
# 로그인 페이지 View 구분용 키
# ============================================================
class LoginViews:
    """
    로그인 페이지 내부의 View 전환 상태를 관리하기 위한 키 집합.

    Streamlit의 세션 상태(`st.session_state[LoginViews.KEY]`)에 저장되어
    현재 활성화된 화면을 구분한다.
    """
    KEY: Final[str] = "login_view"                          # 현재 뷰 상태 식별자

    LOGIN_BEFORE: Final[str] = "login_before"               # 로그인 전 화면
    SIGN_UP: Final[str] = "sign_up"                         # 회원가입 화면
    PERSONAL_INFO_AGREE: Final[str] = "p_info_agree"        # 개인정보 수집 동의 화면
    LOST_PASSWORD: Final[str] = "lost_password"             # 비밀번호 분실 화면

    LOGIN_AFTER: Final[str] = "login_after"                 # 로그인 성공 후 화면
    EDIT: Final[str] = "edit"                               # 회원 정보 수정 화면
    SOFT_DELETE: Final[str] = "soft_delete"                 # 계정 사용 정지 화면



# ============================================================
# 회원가입 관련 세션 키 (중복검사 및 메시지 관리)
# ============================================================
class SignupKey:
    """
    회원가입 과정에서 중복 확인 결과 및 메시지를 세션에 저장하기 위한 키.

    각 필드는 Streamlit 세션(`st.session_state`) 내에서
    SignUpUniqueKeys / SignUpAction 클래스와 함께 사용된다.
    """
    # --- 중복검사 통과 여부 (bool) ---
    USER_ID: Final[str] = "signup_user_id_verified"         # user_id 중복검사 통과 여부
    KTR_ID: Final[str] = "signup_ktr_id_verified"           # ktr_id 중복검사 통과 여부
    EMAIL: Final[str] = "signup_email_verified"             # email 중복검사 통과 여부
    
    # --- 중복검사 결과 메시지 (str) ---
    USER_ID_MSG: Final[str] = "signup_user_id_message"      # user_id 결과 메시지
    KTR_ID_MSG: Final[str] = "signup_ktr_id_message"        # ktr_id 결과 메시지
    EMAIL_MSG: Final[str] = "signup_email_message"          # email 결과 메시지



# ============================================================
# Admin 페이지 View 구분용 키
# ============================================================
class AdminViews:
    KEY: Final[str] = "admin_view"

    # View key
    ALL: Final[str] = "f_all"
    USER_ID: Final[str] = "f_user_id"
    SIGNUP: Final[str] = "f_signup"
    DEVELOPER: Final[str] = "f_developer"
    BLOCK: Final[str] = "f_block"
    CLEAR: Final[str] = "f_clear"

    # View에 할당된 Table key
    TABLE_ALL: Final[str] = "t_all"
    TABLE_USER_ID: Final[str] = "t_user_id"
    TABLE_SIGNUP: Final[str] = "t_signup"
    TABLE_DEVELOPER: Final[str] = "t_developer"
    TABLE_BLOCK: Final[str] = "t_block"
    TABLE_CLAER: Final[str] = "t_clear"


class AdminUserModify:
    INDEX_LIST: Final[str] = "admin_selected_idxes"         # Admin Table에서 선택된 index를 담는 list
    ADMIN_IDX_LIST: Final[str] = "admin_admin_idxes"        # Admin Table에서 Admin인 유저들의 index를 담는 list
    BLOCK_IDX_LIST: Final[str] = "admin_block_idxes"        # Admin Table에서 Block(Soft-delete)인 유저들의 index를 담는 list

    DELETE_WAIT: Final[str] = "admin_delete_wait"           # Admin Table에서 dialog에서 중복 입력 방어


# ============================================================
# Streamlit Chat 위젯용 키
# ============================================================
class StreamLitChatKey:
    """
    Streamlit의 `st.chat_message` 컴포넌트에서 사용하는 키.

    채팅 메시지 객체의 기본 구조를 정의한다.
    """
    ROLE: Final[str] = "role"               # 발신자 역할 (user/assistant/system)
    CONTENT: Final[str] = "content"         # 메시지 본문 텍스트

