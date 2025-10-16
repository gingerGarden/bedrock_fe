"""
대시보드 페이지(`pages/3_dashboard.py`) UI 및 로직.

- 로그인된 사용자만 접근 가능.
- 비로그인 시 GoLogin으로 로그인 페이지 안내.
- 실제 대시보드 콘텐츠는 추후 구현 예정.
"""
import streamlit as st
from app.constants.keys import SessionKey, LoginViews
from app.utils.session import init_session
from app.routes.common import GoLogin, basic_ui, InitModelInfo
from app.routes.p5_dashboard import Main



# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
basic_ui(title=None)


# ---------------------------------------------------------
# 2. 세션 상태 초기화
# ---------------------------------------------------------
init_session()          # 세션 상태 초기화 (로그인 정보)
InitModelInfo.run()     # 모델 정보 로드


# ---------------------------------------------------------
# 3. 로그인 여부에 따른 UI 렌더링
# ---------------------------------------------------------
if not st.session_state[SessionKey.LOGGED_IN]:

    # 다른 페이지의 View 초기화
    st.session_state[LoginViews.KEY] = LoginViews.LOGIN_BEFORE

    # 로그인이 되어 있지 않은 경우, 로그인 페이지로 가이드
    GoLogin.UI(title="Dashboard")
else:
    # 다른 페이지의 View 초기화
    st.session_state[LoginViews.KEY] = LoginViews.LOGIN_AFTER

    # UI 출력
    Main.UI()