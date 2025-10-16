"""
애플리케이션의 주요 파일·디렉터리 경로 상수 모듈.

- 페이지 이동, 이미지 로드, 데이터 파일 접근 시 경로를 중앙에서 관리.
- 경로 변경 시 이 모듈만 수정하면 전체 코드에 반영 가능.
"""
from typing import Final


# Page 경로 관리
class PagePath:
    """페이지 파일 경로 (st.switch_page 등에서 사용)."""
    P1_LOGIN: Final[str] = "pages/1_Login.py"
    P2_CHAT: Final[str] = "pages/2_KHA_chat.py"
    P3_FLORA_GENESIS: Final[str] = "pages/3_FloraGenesis.py"
    P4_PANCODR: Final[str] = "pages/4_PANCDR.py"
    P5_DASHBOARD: Final[str] = "pages/5_Dashboard.py"
    P6_SETTING: Final[str] = "pages/6_Setting.py"
    P7_ADMIN: Final[str] = "pages/7_Admin.py"
    




# --- 리소스 파일 경로 ---

# 페이지 아이콘(파비콘)으로 사용될 이미지 파일 경로
KTR_ICON: Final[str] = "src/KTR-icon.ico"

# 프로토타입용 사용자 인증 정보가 담긴 JSON 파일 경로
DB_PATH: Final[str] = "src/test_db.json"