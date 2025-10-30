"""
애플리케이션 전역에서 사용하는 상수(Constant) 정의 모듈.

이 모듈은 주로 다음과 같은 목적을 가진다.
- API 요청 공통 설정 (예: TIMEOUT)
- 사용자 정보 키(`SessionState` / API 응답 파서 공용 키)
- UI 레이아웃 비율 등 프론트엔드 공용 상수

모든 상수는 직접 수정하지 않고, import 하여 참조만 하도록 한다.
"""
from typing import Final, Tuple, List, Dict



# ============================================================
# API 공통 설정
# ============================================================
API_TIMEOUT = (
    3.0,    # Connect timeout (서버 연결 대기 시간)
    5.0     # Read timeout (응답 수신 대기 시간)
)
"""
API 통신 기본 타임아웃 설정.

구조
----
(API 연결 대기 시간, 응답 수신 대기 시간)

용도
----
`requests` 라이브러리의 `timeout` 인자로 전달되어,
서버 지연이나 무한 대기를 방지한다.
예: `requests.post(url, timeout=API_TIMEOUT)`
"""


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


# ============================================================
# Admin - 사용자 조회 키 (Table 주요 속성)
# ============================================================
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
# Admin - Users Table 조회 고정 변수
# ============================================================
class AdminUserTable:

    # ----------------- Time -----------------
    # datetime 신규 컬럼명
    # json으로 전달받은 문자형 datetime을 datetime으로 변환 시, 컬럼명
    DT_ADD_COL: Final[str] = "{col}_df"
    # datetime 컬럼과 현시점 간 차이에 대한 컬럼명
    DT_INTERVAL_COL: Final[str] = "{col}_interval"

    # datetime 컬럼명
    DT_COLUMNS: List[str] = [
        UsersRecord.created_at,
        UsersRecord.updated_at,
        UsersRecord.signup_at,
        UsersRecord.deleted_at
    ]

    # 시간 컬럼 date만 표기할지 여부
    DT_SHOW_ONLY_DATE: Final[bool] = True


    # ----------------- Role -----------------
    # Role 컬럼과 배정된 수치
    ROLE_COL_DICT: Dict[str, int] = {
        "user":0,
        "developer":1, 
        "admin":9
    }

    # Role 신규 컬럼명
    # bool으로 표기된 role 컬럼을 정수로 변환하였을 때 컬럼명
    ROLE_NUM_COL: Final[str] = "{col}_num"
    # 정수 role 컬럼을 합친 정수 컬럼
    ROLE_NUM_TOTAL_COL: Final[str] = "role_total"
    # 합쳐진 정수 role(ROLE_NUM_TOTAL_COL)의 문자열 컬럼명(결과)
    ROLE_STRING_COL: Final[str] = "role_string"


    # ----------------- 최종 출력 -----------------
    # 기본 컬럼 중 최종 출력에 포함될 값
    RESULT_ORIGIN_COLUMNS: List[str] = [
        "idx", "user_id", "ktr_id", "email", "signup"
    ]
    # 최종 출력에 idx를 제외할지 여부
    RESULT_EXCLUDE_IDX: Final[bool] = False

    # 최종 출력 시, 변수명을 어떻게 수정할지
    RESULT_NEW_COLUMN_NAMES: Dict[str, str] = {
        "idx":"idx", 
        "user_id":"ID", 
        "ktr_id":"사번",
        "email":"이메일",
        "signup":"승인여부",
        "deleted_at_interval":"정지일수",
        "role_string":"권한"
    }
    # sort 순서
    RESULT_COLUMN_SORT: List[str] = ["권한", "승인여부", "정지일수", "idx"]
    # 내림차순 오름차순
    RESULT_COLUMN_SORT_ASCENDING: List[bool] = [True, True, False, True]


# ============================================================
# UI 비율 / 화면 구성용 상수
# ============================================================
class Ratio:
    """
    Streamlit 페이지 구성 시 컬럼 비율 등 UI 관련 상수 모음.
    """
    # 로그인 View에서 text_bar, btn의 크기 비율
    LOGIN_BAR_N_BTN: Final[Tuple[int, int]] = [3, 1]
    """
    로그인/회원가입 View에서
    - 입력창(text_input)
    - 버튼(submit_button)
    의 가로 비율을 지정한다.

    예시
    ----
    ```python
    col1, col2 = st.columns(Ratio.LOGIN_BAR_N_BTN)
    ```
    → 입력창:버튼 = 3:1
    """
