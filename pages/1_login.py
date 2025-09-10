"""
로그인 페이지(`pages/1_login.py`) UI 및 로직.

- Streamlit 멀티페이지 규칙에 따라 pages/ 디렉터리에 위치.
- basic_ui로 페이지 전역 스타일(제목, 아이콘 등) 설정.
- init_session과 InitModelInfo로 전역 상태 초기화.
- 로그인 여부에 따라 BeforeLogin / AfterLogin UI를 렌더링.
"""
import streamlit as st
from app.schema.keys import SessionKey
from app.utils.session import init_session
from app.routes.common import basic_ui, InitModelInfo
from app.routes.p1_login import BeforeLogin, AfterLogin



# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
basic_ui(title="Log-in")


# ---------------------------------------------------------
# 2. 세션 상태 초기화
# ---------------------------------------------------------
init_session()
InitModelInfo.run()


# ---------------------------------------------------------
# 3. 로그인 상태에 따른 UI 렌더링
# ---------------------------------------------------------
if not st.session_state[SessionKey.LOGGED_IN]:
    # 로그인 전: ID/PW 입력 폼
    BeforeLogin.UI()
else:
    # 로그인 후: 사용자 정보 + 기능 버튼
    AfterLogin.UI()

    # -----------------------------------------------------
    # 로그인 후 제공되는 버튼
    # - Go to Chat: 채팅 페이지로 이동
    # - Logout: 세션 초기화 후 로그인 상태 해제
    # -----------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        AfterLogin.go_to_chat()

    with col2:
        AfterLogin.logout()

