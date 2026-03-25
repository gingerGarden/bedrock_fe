import streamlit as st
from app.constants.keys import SessionKey, LoginViews, PageNum
from app.utils.session import SessControl
from app.routes.common import GoLogin, basic_ui
from app.routes.p3_floragenesis import Main



# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
basic_ui(title=None)


# ---------------------------------------------------------
# 2. 세션 상태 초기화
# ---------------------------------------------------------
SessControl.init()                                          # 세션 상태 초기화 (로그인 정보)
SessControl.set_page_info(page_num=PageNum.FLORAGENESIS)    # 페이지 상태 session 저장
SessControl.init_model_info()                               # 모델 정보 로드


# ---------------------------------------------------------
# 3. 로그인 여부에 따른 UI 렌더링
# ---------------------------------------------------------
if not st.session_state[SessionKey.LOGGED_IN]:

    # 다른 페이지의 View 초기화
    st.session_state[LoginViews.KEY] = LoginViews.LOGIN_BEFORE

    # 로그인이 되어 있지 않은 경우, 로그인 페이지로 가이드
    GoLogin.UI(title="FloraGenesis")
else:
    # 다른 페이지의 View 초기화
    st.session_state[LoginViews.KEY] = LoginViews.LOGIN_AFTER

    # UI 출력
    Main.UI()