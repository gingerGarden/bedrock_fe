import streamlit as st
from app.tools.t00_common import ToolCommon
from app.utils.utils import btn_type_converter
from .config import (
    SessionKeys, View, Titles, Check, WidgetKeys, EQUIPMENTS
)
from .utils import ToolUtils, Data
from .routes import EXPSetup, EXPSetup, ColumnsSetup



class Main:

    @classmethod
    def UI(cls):
        # 세션 초기화
        ToolUtils.init_session()

        # 에러 세션이 감지되면 다이얼로그 출력
        if st.session_state.get(SessionKeys.ERROR_MESSAGE):
            cls.error_dialog()
        
        # 현재 뷰에 따른 렌더링 분기
        current_view = st.session_state[SessionKeys.CURRENT_VIEW]
        if current_view == View.MAIN:
            cls.render_main_view()
        elif current_view == View.EXP_SETUP:
            EXPSetup.UI()
        elif current_view == View.COLUMN_SETUP:
            ColumnsSetup.UI()

    @classmethod
    def render_main_view(cls):

        # 뒤로가기 버튼
        ToolCommon.back_button()

        st.title(Titles.MAIN_TITLE)
        st.markdown("---")

        # 1. 데이터 업로드 섹션
        cls.upload_section()
        st.markdown("---")

        # 2. 설정 버튼 섹션
        with st.container(border=True):
            st.subheader(Titles.MAIN_SETUP)
            cls.setting_btn_section()
        st.markdown("---")

        # 3. 데이터 처리 버튼
        with st.container(border=True):
            st.subheader(Titles.MAIN_ACTION)
            cls.handler_btn_section()

    @classmethod
    def upload_section(cls):
        with st.expander(Titles.MAIN_UPLOAD, expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                f1 = st.file_uploader(
                    EQUIPMENTS["e1"]["name"], 
                    key=ToolUtils.get_wkey(WidgetKeys.U1)
                )
                f3 = st.file_uploader(
                    EQUIPMENTS["e3"]["name"], 
                    key=ToolUtils.get_wkey(WidgetKeys.U3)
                )
            with col2:
                f2 = st.file_uploader(
                    EQUIPMENTS["e2"]["name"], 
                    key=ToolUtils.get_wkey(WidgetKeys.U2)
                )
                f4 = st.file_uploader(
                    EQUIPMENTS["e4"]["name"], 
                    key=ToolUtils.get_wkey(WidgetKeys.U4)
                )

            # 파일이 업로드되면 세션에 저장
            if f1: Data.get(file=f1, data_key="e01-혈액분석기")
            if f2: Data.get(file=f2, data_key="e02-생화학분석기")
            if f3: Data.get(file=f3, data_key="e03-응고분석기")
            if f4: Data.get(file=f4, data_key="e04-요분석기")
    
    @classmethod
    def setting_btn_section(cls):
        col1, col2, col3 = st.columns(3)
        # 설정 항목
        with col1:
            # 실험 전체 설정
            if st.button(
                    "실험 설정", 
                    use_container_width=True, 
                    type=btn_type_converter(target=st.session_state[Check.EXP_SETUP])
                ):
                ToolUtils.set_view(View.EXP_SETUP)
                st.rerun()
        with col2:
            # 변수 설정 화면
            if st.button(
                    "변수 설정", 
                    use_container_width=True, 
                    type=btn_type_converter(target=st.session_state[Check.COLUMN_SETUP])
                ):
                ToolUtils.set_view(View.COLUMN_SETUP)
                st.rerun()
        with col3:
            # 초기 상태로 변경
            if st.button("초기화", use_container_width=True):
                ToolUtils.init_session(force=True)
                st.rerun()

    @classmethod
    def handler_btn_section(cls):
        # 데이터 처리
        col1, col2, col3, col4 = st.columns(4)
        # 데이터 출력 항목
        with col1:
            if st.button(EQUIPMENTS["e1"]["name"], use_container_width=True):
                # TODO - 비즈니스 로직 - 혈액 분석기 장착 예정
                pass
        with col2:
            if st.button(EQUIPMENTS["e2"]["name"], use_container_width=True):
                # TODO - 비즈니스 로직 - 생화학 분석기 장착 예정
                pass
        with col3:
            if st.button(EQUIPMENTS["e3"]["name"], use_container_width=True):
                # TODO - 비즈니스 로직 - 응고 분석기 장착 예정
                pass
        with col4:
            if st.button(EQUIPMENTS["e4"]["name"], use_container_width=True):
                # TODO - 비즈니스 로직 - 요 분석기 장착 예정
                pass

    @staticmethod
    @st.dialog("데이터 로드 오류")
    def error_dialog():
        # 세션에 메시지와 대상 위젯 추출
        msg = st.session_state.get(SessionKeys.ERROR_MESSAGE)
        target_widget = st.session_state.get(SessionKeys.ERROR_TARGET_WIDGET)

        st.warning(f"⚠️ {msg}")
        st.info("확인을 누르면 해당 업로드 항목이 초기화됩니다.")

        if st.button("확인", use_container_width=True, type="primary"):
            # 문제가 된 특정 위젯만 카운터를 올려서 초기화
            ToolUtils.reset_widget(target_widget)
            st.rerun()
