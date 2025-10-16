"""
애플리케이션 전역에서 사용하는 상수(Constant) 정의 모듈.

이 모듈은 주로 다음과 같은 목적을 가진다.
- API 요청 공통 설정 (예: TIMEOUT)
- 사용자 정보 키(`SessionState` / API 응답 파서 공용 키)
- UI 레이아웃 비율 등 프론트엔드 공용 상수

모든 상수는 직접 수정하지 않고, import 하여 참조만 하도록 한다.
"""
from typing import Final, Tuple



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
