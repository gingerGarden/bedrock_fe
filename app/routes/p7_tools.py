"""
도구 마켓플레이스 - 유틸리티 포털 형태로 만들자

1. 도구 검색기
    * '도구명' 으로 검색
    * 'Tag' 으로 검색
2. 도구 테이블
    * |도구명|설명|Tag|버전|
    * 도구 테이블에 있는 도구를 클릭하여 해당 기능 사용 가능
3. 신규 도구 개발 요청
    * 게시글 형태로 신규 도구 개발 요청 가능
"""
from typing import Final
import streamlit as st
import pandas as pd

from app.constants.messages import ToolsMainMsg
from app.constants.pathes import TOOLS_JSON
from app.constants.keys import ToolsViews
from app.schemas.p7_tools import ToolDFCols
from app.routes.p7_tools_board import ToolsBoard
from app.tools import TOOL_ROUTER
from app.tools.t00_common import ToolCommon
from app.tools import ToolSessionManager

from bedrock_core.utils.file import read_json



class Main:

    fn1_toolmarket: Final[str] = "도구모음"
    fn2_board: Final[str] = "도구 신청 게시판"

    @classmethod
    def UI(cls):

        # --- 사이드바 네비게이션 ---
        with st.sidebar:
            st.title("Tools 메뉴")
            menu = st.radio(
                "이동할 메뉴를 선택하세요",
                [
                    cls.fn1_toolmarket, 
                    cls.fn2_board
                ],
                key="tools_sidebar_menu"
            )
            st.markdown("---")

        # --- 메뉴 분기 ---
        if menu == cls.fn2_board:
            ToolsBoard.UI()
            # Tools의 각 도구에 있는 세션이 게시판 이동 시 초기화되게 함
            ToolSessionManager.clear_all_tool_sessions()
        else:
            ToolsMarkets.UI()



class ToolsMarkets:

    # 개발되어 있는 도구에 대한 정보 모음
    tool_df = pd.DataFrame(read_json(TOOLS_JSON))
    tag_list = sorted(set().union(*tool_df["Tag"]))

    @classmethod
    def UI(cls):

        # 0. 현재 뷰 상태 확인
        current_view = st.session_state.get(ToolsViews.KEY, ToolsViews.MAIN)

        # 1. 상세 도구 화면 분기
        if current_view != ToolsViews.MAIN:
            cls.render_tool_detail(current_view)
            return

        # 2. 마켓플레이스 목록 화면
        st.title(ToolsMainMsg.TITLE)
        st.markdown(ToolsMainMsg.INTRO)
        st.markdown("---")

        # 검색기 UI
        search_name, search_tags = cls.search()
        # 필터링된 데이터 프레임 획득
        display_df = cls._tool_df_handler(search_name=search_name, search_tags=search_tags)
        st.markdown("---")

        # 3. 도구 목록 출력
        cls.show_tool_table(display_df)

    @classmethod
    def search(cls):
        st.write("### 도구 검색기")

        # 도구명 기반 검색기
        search_name = st.text_input(
            "도구명 검색", placeholder="예: 데이터 전처리기", label_visibility="collapsed"
        )
        # Tag 기반 검색기
        search_tags = st.multiselect(
            "Tag 필터", options=cls.tag_list, placeholder="Tag 복수 선택"
        )
        return search_name, search_tags
    
    @classmethod
    def show_tool_table(cls, tool_df: pd.DataFrame):

        st.write("### 도구 목록")

        if tool_df.empty:
            st.warning(ToolsMainMsg.NO_TOOLS)
        else:
            # 각 도구를 카드 형태로 렌더링
            for idx, row in tool_df.iterrows():
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1])

                    with col_info:
                        # 제목 및 버전
                        st.markdown(f"#### {row[ToolDFCols.NAME]} `{row[ToolDFCols.VERSION]}`")
                        # 설명
                        st.write(row[ToolDFCols.DESCRIPT])
                        # 태그 뱃지 (HTML 활용)
                        tags = row[ToolDFCols.TAG]
                        tag_html = " ".join([
                            f"<span style='background-color:#f0f2f6; color:#31333F; padding:2px 10px; "
                            f"border-radius:12px; margin-right:6px; font-size:0.8rem; font-weight:600;'>{t}</span>"
                            for t in tags
                        ])
                        st.markdown(tag_html, unsafe_allow_html=True)

                    with col_btn:
                        # 버튼 수직 중앙 정렬을 위한 여백
                        st.write(" ")
                        st.write(" ")
                        # 클릭 시 해당 도구의 page_key를 세션에 저장하여 뷰 전환
                        if st.button("도구 사용", key=f"use_{row['page_key']}_{idx}", use_container_width=True, type="primary"):
                            st.session_state[ToolsViews.KEY] = row['page_key']
                            st.rerun()

    @classmethod
    def render_tool_detail(cls, page_key: str):

        # 대상 도구 정보 반환
        tool_info = cls.tool_df[cls.tool_df['page_key'] == page_key].iloc[0]

        # 라우터에서 도구 UI 실행
        if page_key in TOOL_ROUTER:
            # 구현된 도구 실행 (뒤로가기 버튼은 각 도구의 UI() 내부에서 호출)
            TOOL_ROUTER[page_key]()
        else:
            ToolCommon.back_button()
            ToolCommon.dummy_ui(page_key=page_key, tool_info=tool_info)

    @classmethod
    def _tool_df_handler(
            cls, 
            search_name: str | None = None,
            search_tags: list[str] | None = None
        ) -> pd.DataFrame:

        if not search_name and not search_tags:
            return cls.tool_df

        copy_df = cls.tool_df.copy()
                
        # search_name 필터
        if search_name:
            copy_df = copy_df[
                copy_df[ToolDFCols.NAME]
                .str.contains(search_name, case=False)  # case=False : 대소문자 무시
            ]
        if search_tags:
            copy_df = copy_df[
                [bool(set(i) & set(search_tags)) for i in copy_df[ToolDFCols.TAG]]
            ]
        return copy_df