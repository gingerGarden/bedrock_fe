"""
공통 UI 컴포넌트 및 초기화 로직 모듈

- basic_ui:
    모든 페이지의 전역 UI 설정(페이지 제목, 아이콘, 레이아웃)을 적용.
- GoLogin:
    로그인이 필요한 페이지에서 안내 메시지와 로그인 페이지 이동 버튼 제공.
- InitModelInfo:
    앱 시작 시 백엔드에서 모델 정보를 가져와 세션에 저장.
"""
from typing import Optional

import streamlit as st
from app.api.p2_chat import get_available_models, get_default_model
from app.constants.pathes import PagePath, KTR_ICON
from app.constants.keys import SessionKey
from app.constants.messages import NONE_LOGIN_USER



def basic_ui(
        title: Optional[str] = None,
        wide: bool = False
    ):
    """
    페이지 공통 UI 설정 적용.

    - 모든 페이지 상단에서 호출하여 동일한 레이아웃과 디자인 유지.
    - st.set_page_config는 스크립트 실행 시 한 번만 호출 가능.

    Args:
        title (str, optional): 페이지 타이틀. 지정 시 페이지 상단에 표시.
    """
    _layout = "wide" if wide else "centered"

    st.set_page_config(
        page_title="KHA alpha",             # 브라우저 탭 제목
        page_icon=KTR_ICON,                 # 페이지 아이콘
        layout=_layout,                     # 화면 레이아웃 (가운데 정렬)
        initial_sidebar_state="expanded"    # 실행 시 사이드바 기본 상태 (펼쳐짐)
    )

    if title is not None:
        # 페이지 타이틀 및 구분선
        st.title(title)
        st.markdown("---")



class GoLogin:
    """
    로그인 필요 알림 및 로그인 페이지 이동 UI.
    """
    @classmethod
    def UI(cls, title: Optional[str] = None):
        """로그인 안내 메시지와 이동 버튼 렌더링."""

        if title is not None:
            st.title(title)
            st.markdown("---")

        st.error("로그인이 필요합니다!")

        with st.container():
            st.info(NONE_LOGIN_USER)

        cls.go_to_login()

    @classmethod
    def go_to_login(cls):
        """'log-in page' 버튼 클릭 시 페이지 전환."""
        if st.button(
            "로그인(Login) 페이지 이동", 
            use_container_width=True, type="primary"
        ):
            st.switch_page(PagePath.P1_LOGIN)



class InitModelInfo:
    """
    모델 정보 초기화 관리 클래스.

    앱 실행 시:
        - 모델 목록 로드
        - 기본 모델명 로드
        - 기본 모델 인덱스 계산 후 세션 저장
    """
    @classmethod
    def run(cls):
        """모델 정보 초기화 전체 실행."""
        # 모델 목록 로드
        cls.model_list_in_session()
        # 디폴트 모델명 로드
        cls.default_model_in_session()
        # 디폴트 모델명 index 로드
        cls.default_model_idx_in_session()

    @classmethod
    def model_list_in_session(cls):
        """세션에 모델 목록이 없으면 API 호출."""
        # 모델 목록이 없는 경우에만 불러온다
        if SessionKey.MODEL_LIST not in st.session_state:
            st.session_state[SessionKey.MODEL_LIST] = get_available_models()

    @classmethod
    def default_model_in_session(cls):
        """세션에 기본 모델명이 없으면 API 호출."""
        # default 모델 이름이 없는 경우에만 불러온다
        if SessionKey.MODEL not in st.session_state:
            st.session_state[
                SessionKey.MODEL
            ] = get_default_model()

    @classmethod
    def default_model_idx_in_session(cls):
        """
        세션에 기본 모델 인덱스가 없으면 계산 후 저장.
        - st.selectbox index 인자에 사용.
        """
        if SessionKey.MODEL_IDX not in st.session_state:
            # dafault 모델 이름 index 로드
            cls.set_model_idx()

    @classmethod
    def set_model_idx(cls):
        """기본 모델명에 해당하는 인덱스를 세션에 저장."""
        st.session_state[SessionKey.MODEL_IDX] = st.session_state[
            SessionKey.MODEL_LIST].index(st.session_state[SessionKey.MODEL])
