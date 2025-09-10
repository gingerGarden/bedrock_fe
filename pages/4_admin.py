"""
관리자 페이지(`pages/4_admin.py`) UI 및 로직.

- 로그인된 사용자만 접근 가능.
- 비로그인 시 GoLogin으로 로그인 페이지 안내.
- 관리자 전용 기능은 추후 구현 예정.
"""
import streamlit as st
from app.schema.keys import SessionKey
from app.utils.session import init_session
from app.routes.common import GoLogin, basic_ui, InitModelInfo



# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
basic_ui(title="Admin")


# ---------------------------------------------------------
# 2. 세션 상태 초기화
# ---------------------------------------------------------
init_session()          # 세션 상태 초기화 (로그인 정보)
InitModelInfo.run()     # 모델 정보 로드


# ---------------------------------------------------------
# 3. 로그인 여부에 따른 UI 렌더링
# ---------------------------------------------------------
if not st.session_state[SessionKey.LOGGED_IN]:
    # 로그인이 되어 있지 않은 경우, 로그인 페이지로 가이드
    GoLogin.UI()