"""
로그인 페이지(`pages/1_login.py`) UI 및 로직.

- Streamlit 멀티페이지 규칙에 따라 pages/ 디렉터리에 위치.
- basic_ui로 페이지 전역 스타일(제목, 아이콘 등) 설정.
- init_session과 InitModelInfo로 전역 상태 초기화.
- 로그인 여부에 따라 BeforeLogin / AfterLogin UI를 렌더링.
"""
import streamlit as st
from app.constants.keys import SessionKey, LoginViews
from app.utils.session import init_session
from app.routes.common import basic_ui, InitModelInfo
from app.routes.p1_login_after import AfterLogin, Edit, SoftDelete
from app.routes.p1_login_before import BeforeLogin, SignUp, ShowPersonalInfoAgree



# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
basic_ui(title="Login")


# ---------------------------------------------------------
# 2. 세션 상태 초기화
# ---------------------------------------------------------
init_session()
InitModelInfo.run()


# ---------------------------------------------------------
# 3. 로그인 상태에 따른 UI 렌더링
# ---------------------------------------------------------
if st.session_state[SessionKey.LOGGED_IN]:
    
    # 로그인 후: 뷰 상태(login_after/edit)로 분기
    view = st.session_state.setdefault(
        LoginViews.KEY, LoginViews.LOGIN_AFTER
    )

    if view == LoginViews.LOGIN_AFTER:
        # 로그인 후: 사용자 간단한 정보 + 기능 버튼
        AfterLogin.UI()
    elif view == LoginViews.EDIT:
        # 회원 정보 수정
        Edit.UI()
    else:
        # 회원 정지
        SoftDelete.UI()

else:
    # 로그인 전: 뷰 상태(login_before/sign_up)로 분기
    view = st.session_state.setdefault(
        LoginViews.KEY, LoginViews.LOGIN_BEFORE
    )

    # session의 P1_LOGIN_VIEW_KEY에 따른 View 교체
    if view == LoginViews.LOGIN_BEFORE:
        # 로그인 이전
        BeforeLogin.UI()
    elif view == LoginViews.PERSONAL_INFO_AGREE:
        # 개인정보수집 약관
        ShowPersonalInfoAgree.UI()
    else:
        # 회원 가입
        SignUp.UI()
