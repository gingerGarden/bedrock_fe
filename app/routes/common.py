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
from app.constants.pathes import PagePath, KTR_ICON
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