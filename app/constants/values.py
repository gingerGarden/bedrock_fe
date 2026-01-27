"""
애플리케이션 전역에서 사용하는 상수(Constant) 정의 모듈.

이 모듈은 주로 다음과 같은 목적을 가진다.
- API 요청 공통 설정 (예: TIMEOUT)
- 사용자 정보 키(`SessionState` / API 응답 파서 공용 키)
- UI 레이아웃 비율 등 프론트엔드 공용 상수

모든 상수는 직접 수정하지 않고, import 하여 참조만 하도록 한다.
"""
from typing import Final, Tuple, List, Dict
from app.constants.keys import UsersRecord



# ============================================================
# 주요 공통 설정
# ============================================================
class FixValues:

    # 기본 비밀번호 - 관리자 비밀번호 수정 시
    DEFAULT_PASSWORD: Final[str] = "1a2b3c4d5e6f"
    # API 통신 기본 타임아웃 설정
    API_TIMEOUT: Tuple[float, float] = (
        3.0,    # Connect timeout (서버 연결 대기 시간)
        5.0     # Read timeout (응답 수신 대기 시간)
    )
    # Chat Time Out
    CHAT_TIME_OUT: Final[int] = 300
    """
    app/api/p2_chat.py - streaming_response의 출력에서, API의 대기 시간
    """
    # Flash life
    FLASH_LIFE: Final[int] = 2
    """
    Flash로 별도 출력하는 로그가 재렌더링 과정을 몇 번까지 버틸지 내부에서 st.rerun()으로 렌더링 되는 절차를 이야기함
    새로운 데이터가 flash에 입력 시, 초기화 됨
    """


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
    # Admin Table 크기
    ADMIN_TABLE_SIZE: int = 650



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
    # 최종 출력 시, 변수명을 어떻게 수정할지
    RESULT_NEW_COLUMN_NAMES: Dict[str, str] = {
        "idx":"idx", 
        "user_id":"ID", 
        "ktr_id":"사번",
        "email":"이메일",
        "signup":"승인여부",
        DT_INTERVAL_COL.format(col="signup_at"):"승인일수",
        DT_INTERVAL_COL.format(col="deleted_at"):"정지일수",
        "role_string":"권한"
    }
    
    # sort 순서
    RESULT_COLUMN_SORT: List[str] = ["권한", "승인여부", "정지일수", "idx"]
    # 내림차순 오름차순
    RESULT_COLUMN_SORT_ASCENDING: List[bool] = [True, True, False, True]
    # index 표기 여부
    SHOW_FE_IDX: bool = True
    # 결측값 string - FE에서 실수열의 렌더링 오류 방지를 위해 string으로 전환 - 결측값의 문자열 리스트 - 필터를 위한
    STRING_NA: List[str] = ["", "nan", "NaN", "None", "NaT"]





