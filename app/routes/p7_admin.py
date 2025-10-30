from typing import Optional

import streamlit as st
import pandas as pd

from st_aggrid import (
    AgGrid, GridOptionsBuilder, GridUpdateMode, 
    DataReturnMode, JsCode
)
from app.constants.messages import NO_ADMIN_USER
from app.constants.pathes import PagePath
from app.constants.keys import AdminViews
from app.constants.values import UsersRecord
from app.utils.p7_admin import UserTable, view_changer



class Main:

    @classmethod
    def UI(cls):

        st.subheader("대상 유저 목록")
        SideBar.main()

        
        
class SideBar:

    @classmethod
    def main(cls):

        with st.sidebar:
            
            # 1) 조회
            f_all, f_user_id, f_developer, f_signup, f_block, user_id = cls._find_btns()

            st.markdown("---")

            # 2) 조작
            a_signup, pwd_convert_btn, a_block, a_delete, pwd = cls._action_btns()

        # 세션 플래그 초기화
        if AdminViews.KEY not in st.session_state:
            st.session_state[AdminViews.KEY] = None

        # ========== 이벤트 처리 ==========
        # 1) 조회
        # 전체 조회
        if f_all: view_changer(AdminViews.ALL)
        # 계정 조회
        if f_user_id: view_changer(AdminViews.USER_ID)
        # 승인 대기 계정 조회
        if f_signup: view_changer(AdminViews.SIGNUP)
        # 정지 계정 조회
        if f_block: view_changer(AdminViews.BLOCK)
        # 개발자 계정 조회
        if f_developer: view_changer(AdminViews.DEVELOPER)

        # 현재 뷰에 따른 렌더링
        if st.session_state[AdminViews.KEY] == AdminViews.ALL:
            cls.show_all_users_aggrid()

        # 2) 조작
        # 대상 승인
        if a_signup: pass
        # 대상 정지 (soft-delete)
        if a_block: pass
        # 대상 삭제 (hard-delete)
        if a_delete: pass
        # 비밀번호 변경
        if pwd_convert_btn: pass

    @classmethod
    def _find_btns(cls):
        st.markdown("1) 조회")
        col1, col2 = st.columns(2)
        with col1:
            # 승인대기 계정 조회 버튼
            f_signup = st.button(
                "승인 대기",
                use_container_width=True,
                type="primary"
            )

            # 단일 계정 조회 버튼
            f_user_id = st.button(
                "단일 계정",
                use_container_width=True,
                type="primary"
            )

        with col2:
            # 계정 정지 계정 조회 버튼
            f_block = st.button(
                "정지 계정",
                use_container_width=True
            )
            # 전체 이용자 조회 버튼
            f_developer = st.button(
                "개발자",
                use_container_width=True
            )
            # 전체 이용자 조회 버튼
            f_all = st.button(
                "전체",
                use_container_width=True
            )

        # 탐색 대상 ID 입력
        user_id = st.text_input(
            "ID",
            placeholder="검색하고자 하는 ID"
        )

        return f_all, f_user_id, f_developer, f_signup, f_block, user_id


    @classmethod        
    def _action_btns(cls):
        st.markdown("2) 조작")

        col1, col2 = st.columns(2)
        with col1:
            # 대상 계정 승인
            a_signup = st.button(
                "승인",
                use_container_width=True,
                type="primary"
            )
        with col1:
            # 대상 계정 정지
            a_block = st.button(
                "정지",
                use_container_width=True
            )
        with col2:
            # 비밀번호 변경
            pwd_convert_btn = st.button(
                "비밀번호 변경",
                use_container_width=True
            )
        with col2:
            # 대상 계정 삭제
            a_delete = st.button(
                "삭제",
                use_container_width=True
            )

        # 비밀번호 입력 칸
        pwd = st.text_input(
            "신규 비밀번호",
            placeholder="12~64자리 문자열"
        )

        return a_signup, pwd_convert_btn, a_block, a_delete, pwd
    
    @classmethod
    def show_all_users_aggrid(cls):

        # 0) Table 세션 초기화
        cls.init_table(except_key=AdminViews.TABLE_ALL)

        # 1) all Table 세션이 None인 경우, DB 조회
        if (
                AdminViews.TABLE_ALL not in st.session_state or
                st.session_state[AdminViews.TABLE_ALL] is None
            ):
            mask, msg, df = UserTable.all()
            if not mask:
                st.error(msg)
                return
            st.session_state[AdminViews.TABLE_ALL] = df

        # 2) AgGrid 렌더링
        gb_option = cls._grid_option(df = st.session_state[AdminViews.TABLE_ALL])
        grid_response = AgGrid(
            st.session_state[AdminViews.TABLE_ALL],
            gridOptions=gb_option,
            height=700,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,  # 필터/정렬 반영한 데이터 반환
            update_mode=GridUpdateMode.SELECTION_CHANGED,         # 선택 변경 시에만 rerun 트리거
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,  # JsCode 사용 시 필요
            key="users_aggrid"         # 키 고정으로 상태 안정
        )
        
        # 3) 선택된 행 반환 # TODO - 버튼 연동부터 진행
        selected_rows: list = grid_response["selected_rows"]

    @classmethod
    def _grid_option(cls, df: pd.DataFrame) -> GridOptionsBuilder:
        # Option 구성
        gb = GridOptionsBuilder.from_dataframe(df)
        # 컬럼 넓이 자동 맞춤
        gb.configure_default_column(
            resizable=True, filter=True, sortable=True
        )
        # ✅ 체크박스 보이게 + 행 클릭만으로도 멀티 선택 토글 허용
        gb.configure_selection(
            selection_mode="multiple",
            use_checkbox=True,
            rowMultiSelectWithClick=True
        )
        # ✅ 행 클릭 선택 허용 (suppress = False)
        gb.configure_grid_options(
            suppressRowClickSelection=False,
            rowSelection="multiple",
            # ✅ getRowId는 문자열 반환이 더 안정적
            getRowId=JsCode("function(params) { return String(params.data.idx); }"),
        )
        # 특정 컬럼 숨기기 (idx는 내부 식별용으로 두고 표시 숨김)
        gb.configure_column(UsersRecord.idx, hide=True)
        return gb.build()

    @classmethod
    def init_table(cls, except_key: Optional[str] = None):

        for key in [
            AdminViews.TABLE_ALL,
            AdminViews.TABLE_USER_ID,
            AdminViews.TABLE_SIGNUP,
            AdminViews.TABLE_DEVELOPER,
            AdminViews.TABLE_BLOCK
        ]:
            if key != except_key:
                st.session_state[key] = None



class NoAdmin:

    @classmethod
    def UI(cls):

        st.title("No Admin!")
        st.markdown("---")

        st.error("관리자 권한이 있는 유저만 사용할 수 있습니다!")

        with st.container():
            st.info(NO_ADMIN_USER)

        # Main 페이지 이동
        cls.go_to_main()

    @classmethod
    def go_to_main(cls):
        """Main 페이지 이동"""
        if st.button(
            "메인(Main) 페이지 이동",
            use_container_width=True,
            type="primary"
        ):
            st.switch_page(PagePath.P0_MAIN)
