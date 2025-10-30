"""
로그인 페이지(`pages/1_login.py`) UI 및 로직.

개요
----
- Streamlit 멀티페이지 규칙상 이 파일은 `pages/` 폴더에 위치한다.
- 공통 레이아웃/테마는 `basic_ui()`로 설정한다.
- 페이지 진입 시 `init_session()`과 `InitModelInfo.run()`으로 전역 상태를 초기화한다.
- 로그인 여부(SessionKey.LOGGED_IN)에 따라
  - 비로그인: BeforeLogin / SignUp / ShowPersonalInfoAgree 중 하나 렌더링
  - 로그인  : AfterLogin / Edit / SoftDelete 중 하나 렌더링
- 회원가입/수정 과정에서 사용되는 중복키 상태는 화면 전환 지점에서
  `SignUpUniqueKeys.keys_rock_init()`으로 항상 초기화하여 UI 불일치(버튼 색/메시지 잔상)를 방지한다.
"""
import streamlit as st
from app.constants.keys import SessionKey, LoginViews
from app.utils.session import init_session
from app.utils.p1_login import SignUpUniqueKeys
from app.routes.common import basic_ui, InitModelInfo
from app.routes.p1_login_after import AfterLogin, Edit, SoftDelete
from app.routes.p1_login_before import (
    BeforeLogin, SignUp, ShowPersonalInfoAgree, LostPassword
)



# ---------------------------------------------------------
# 1) 페이지 기본 설정
#    - 제목/아이콘/레이아웃 등 전역 UI 프리셋 적용
# ---------------------------------------------------------
basic_ui(title=None)


# ---------------------------------------------------------
# 2) 세션/모델 정보 초기화
#    - 세션 기본키들 미설정 시 기본값 주입
#    - 모델 목록/기본 모델 등 1회성 메타 정보 로딩
# ---------------------------------------------------------
init_session()
InitModelInfo.run()


# ---------------------------------------------------------
# 3) 로그인 상태 분기
#    - LOGGED_IN이 True면 로그인 이후 화면 스택,
#      False면 로그인 이전 화면 스택을 렌더링
# ---------------------------------------------------------
if st.session_state[SessionKey.LOGGED_IN]:
    
    # 로그인 후: 기본 뷰는 LOGIN_AFTER
    view = st.session_state.setdefault(
        LoginViews.KEY, LoginViews.LOGIN_AFTER
    )

    if view == LoginViews.LOGIN_AFTER:
        # 환영/요약 정보 + 이동 버튼들
        AfterLogin.UI()
        # 회원가입용 중복키 상태는 로그인 후 메인으로 돌아올 때 초기화
        SignUpUniqueKeys.keys_rock_init()

    elif view == LoginViews.EDIT:
        # 회원 정보 수정(본인)
        Edit.UI()

    else:
        # 계정 사용 정지(Soft-delete) 화면
        SoftDelete.UI()
        # 정지 화면에서 돌아왔을 때도 중복키 잔상 없도록 초기화
        SignUpUniqueKeys.keys_rock_init()

else:
    # 로그인 전: 기본 뷰는 LOGIN_BEFORE
    view = st.session_state.setdefault(
        LoginViews.KEY, LoginViews.LOGIN_BEFORE
    )
    if view == LoginViews.LOGIN_BEFORE:
        # 로그인 폼 (ID/Password)
        BeforeLogin.UI()
        # 로그인 폼으로 돌아올 때 중복키 상태 초기화(회원가입 잔상 제거)
        SignUpUniqueKeys.keys_rock_init()

    elif view == LoginViews.PERSONAL_INFO_AGREE:
        # 개인정보 수집/이용 안내
        ShowPersonalInfoAgree.UI()
        # 안내 화면에서 이탈 시에도 중복키 상태는 초기화
        SignUpUniqueKeys.keys_rock_init()


    elif view == LoginViews.LOST_PASSWORD:
        # 비밀번호 분실
        LostPassword.UI()
        # 정지 화면에서 돌아왔을 때도 중복키 잔상 없도록 초기화
        SignUpUniqueKeys.keys_rock_init()

    else:
        # 회원가입 폼
        SignUp.UI()
