"""
Streamlit 세션 상태(`st.session_state`) 관리 유틸리티.

- st.session_state는 앱 실행 중 사용자의 상태와 데이터를 유지하는 딕셔너리 형태 저장소.
- 이 모듈은 세션 상태를 안전하게 초기화하는 기능을 제공.
"""
import streamlit as st

from app.constants.keys import SessionKey, LoginViews



def init_session(force: bool = False):
    """
    세션 상태 초기화.

    - st.session_state에 LOGGED_IN 키가 없거나 force=True일 때만 초기화 실행.
    - 불필요한 세션 리셋을 방지하면서, 로그아웃 시 강제 초기화를 지원.

    Args:
        force (bool, optional): True면 현재 상태를 무시하고 강제 초기화.
    """
    # 현재 세션 내 login을 위한 키가 존재하는지 여부
    mask = SessionKey.LOGGED_IN not in st.session_state

    if force or mask:
        _init_session_action()



def _init_session_action():
    """
    세션 기본값 설정.
    - 모델 목록 등 초기 로딩 데이터는 별도 로직에서 유지.
    """
    default = {
        # Login 관련 정보 초기화
        SessionKey.LOGGED_IN: False,
        SessionKey.ID: None,
        SessionKey.USER_NAME: None,
        SessionKey.KTR_ID: None,
        SessionKey.EMAIL: None,

        SessionKey.IS_DEVELOPER: None,
        SessionKey.IS_ADMIN: None,

        # 대화 내용 초기화
        SessionKey.MESSAGE: [],
        SessionKey.STREAMING: False,
        SessionKey.STOP_STREAM: False,

        # View 초기화
        LoginViews.KEY: LoginViews.LOGIN_BEFORE

    }
    for key, value in default.items():
        st.session_state[key] = value