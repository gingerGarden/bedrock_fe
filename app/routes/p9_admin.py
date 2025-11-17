import streamlit as st

from app.core.config import KILL_HARD_DELETE_SWITCH
from app.constants.messages import NO_ADMIN_USER, AdminBtns
from app.constants.pathes import PagePath
from app.constants.keys import AdminViews, AdminUserModify, FlashKeys
from app.constants.values import FixValues
from app.utils.p9_admin import (
    view_changer, GetTable, ShowTable, SideBarAction
)
from app.utils.utils import Flash



class Main:
    """
    Admin 페이지의 메인 컨테이너.

    책임(Responsibilities)
    ----------------------
    - Flash 메시지(최근 실행 로그) 출력
    - 실제 UI 조작은 SideBar.main()에서 수행

    사용 흐름(High-level Flow)
    --------------------------
    1) Flash.render()가 현재 사이클에서 존재하는 1회의 플래시를 표시
    2) SideBar.main()이 좌측 사이드바 UI와 버튼 이벤트를 처리
    """
    @classmethod
    def UI(cls):
        """
        메인 뷰 엔트리포인트. 페이지 상단 로그와 사이드바를 렌더링한다.
        """
        # Flash - Table 조작에 대한 로그 출력
        box = st.empty()
        with box.container():
            Flash.render(flash_key=FlashKeys.ADMIN_TABLE)

        # SideBar에 의해 조작되는 화면
        SideBar.main()


        
class SideBar:
    """
    관리자 페이지의 좌측 사이드바 + 본문 렌더링 트리거.

    구성 요소
    --------
    - _find_btns(): 조회 관련 버튼 및 검색 입력
    - _action_btns(): 승인/정지/삭제/비밀번호 변경 등 조작 버튼
    - main(): 조회/조작 이벤트 처리 후 현재 뷰에 맞는 테이블 렌더링
    """

    @classmethod
    def main(cls):
        """
        사이드바 UI를 구성하고, 버튼 이벤트를 통해 뷰 전환/조작을 수행한다.

        이벤트 처리 요약
        ----------------
        1) 조회:
           - 'DB 조회' 클릭 시 GetTable.base()로 전체 DF 준비 후 AdminViews.ALL로 전환
           - 뷰 필터 버튼(모두 보기/승인대기/정지/개발자/단일 조회)에 따라 뷰 전환 및 필요한 DF 준비
        2) 렌더링:
           - 현재 세션의 AdminViews.KEY 값에 따라 ShowTable.rendering(...) 호출
           - 렌더링 시 선택 인덱스 초기화
        3) 조작:
           - 승인/정지/삭제/비밀번호 변경 버튼 클릭 시 SideBarAction.* 호출
        """
        with st.sidebar:
            
            # 1) 조회
            (
                f_search, f_clear, 
                f_all, f_signup,
                f_developer, f_block, 
                f_user_id, 
                user_id
            ) = cls._find_btns()
            st.markdown("---")

            # 2) 조작
            (
                a_signup, a_signup_block, 
                a_block, a_again_use, 
                a_delete, pwd_converter, 
                pwd
            ) = cls._action_btns()

        # 세션 플래그 초기화 (최초 진입 시 현재 뷰 키 보장)
        if AdminViews.KEY not in st.session_state:
            st.session_state[AdminViews.KEY] = None

        # ========== 이벤트 처리 ==========
        # 1) 조회
        # 전체 DB 조회: 데이터 소량 가정 → 전체 pull 후 FE에서 필터링
        if f_search:
            # 데이터의 양이 적어 전체 DB를 조회하는 형태로 하며, 이때 미리 생성
            GetTable.base()                    # ALL/SIGNUP/BLOCK/DEVELOPER DF 준비
            view_changer(AdminViews.ALL)       # ALL 뷰로 전환
        if f_all:
            view_changer(AdminViews.ALL)
        # 승인 대기 계정 조회
        if f_signup:
            view_changer(AdminViews.SIGNUP)
        # 정지 계정 조회
        if f_block: 
            view_changer(AdminViews.BLOCK)
        # 개발자 계정 조회
        if f_developer: 
            view_changer(AdminViews.DEVELOPER)
        # 계정 조회
        if f_user_id: 
            GetTable.one_user(user_id=user_id) # 단일 ID DF 준비
            view_changer(AdminViews.USER_ID)
        # 선택 초기화
        if f_clear:
            view_changer(AdminViews.CLEAR)

            
        # 현재 뷰에 따른 렌더링 (각 뷰 진입 시 선택 초기화)
        if st.session_state[AdminViews.KEY] == AdminViews.ALL:
            st.session_state[AdminUserModify.INDEX_LIST] = []   # 조회 버튼 클릭 시, 선택 해제
            ShowTable.rendering(key=AdminViews.TABLE_ALL)
        if st.session_state[AdminViews.KEY] == AdminViews.SIGNUP:
            st.session_state[AdminUserModify.INDEX_LIST] = []
            ShowTable.rendering(key=AdminViews.TABLE_SIGNUP)
        if st.session_state[AdminViews.KEY] == AdminViews.BLOCK:
            st.session_state[AdminUserModify.INDEX_LIST] = []
            ShowTable.rendering(key=AdminViews.TABLE_BLOCK)
        if st.session_state[AdminViews.KEY] == AdminViews.DEVELOPER:
            st.session_state[AdminUserModify.INDEX_LIST] = []
            ShowTable.rendering(key=AdminViews.TABLE_DEVELOPER)
        if st.session_state[AdminViews.KEY] == AdminViews.USER_ID:
            st.session_state[AdminUserModify.INDEX_LIST] = []
            ShowTable.rendering(key=AdminViews.TABLE_USER_ID)
        if st.session_state[AdminViews.KEY] == AdminViews.CLEAR:
            st.session_state[AdminUserModify.INDEX_LIST] = []
            ShowTable.rendering(key=AdminViews.TABLE_CLAER)

        # 2) 조작 (버튼 이벤트 → 액션 호출)
        # 승인
        if a_signup: SideBarAction.signup(way=True)
        # 승인 해제
        if a_signup_block: SideBarAction.signup(way=False)
        # 정지 (Soft-delete)
        if a_block: SideBarAction.block(way=True)
        # 정지 해제
        if a_again_use: SideBarAction.block(way=False)
        # 삭제 (Hard-delete) - 모달 내부에서 재확인 - Soft-delete가 된 대상만 허용
        if a_delete: SideBarAction.delete()
        # 비밀번호 변경
        if pwd_converter: SideBarAction.modify_password(new_pwd=pwd)

    @classmethod
    def _find_btns(cls):
        """
        조회 섹션 UI 생성.

        Returns
        -------
        Tuple[bool, bool, bool, bool, bool, bool, str]
            각각 버튼 클릭 플래그와 검색 ID 입력값을 반환.
        """
        st.markdown("1) 조회")
        
        col1, col2 = st.columns(2)
        with col1:
            # 전체 이용자 조회(백엔드 → DF 준비)
            f_search = st.button(
                "DB 조회",
                use_container_width=True,
                type="primary",
                help=AdminBtns.DB_SEARCH
            )
            # 전체 보기(ALL DF 렌더)
            f_all = st.button(
                "모두 보기",
                use_container_width=True,
                help=AdminBtns.ALL_FILTER
            )

            # 개발자 필터
            f_developer = st.button(
                "개발자", 
                use_container_width=True,
                help=AdminBtns.DEVELOPER_FILTER
            )
            # 단일 계정 필터
            f_user_id = st.button(
                "단일 ID", 
                use_container_width=True,
                help=AdminBtns.ID_FILTER
            )

        with col2:
            # 초기화 필터
            f_clear = st.button(
                "선택 초기화", 
                use_container_width=True,
                type="primary",
                help=AdminBtns.CLEAR_FILTER
            )
            # 승인 대기 필터
            f_signup = st.button(
                "승인 대기", 
                use_container_width=True,
                help=AdminBtns.SIGNUP_FILTER
            )
            # 정지 계정 필터
            f_block = st.button(
                "정지 계정", 
                use_container_width=True,
                help=AdminBtns.BLOCK_FILTER
            )

        # 탐색 대상 ID 입력 (단일 조회 시 사용)
        user_id = st.text_input(
            "ID",
            placeholder="검색하고자 하는 ID"
        )

        return (
            f_search, f_clear, 
            f_all, f_signup,
            f_developer, f_block, 
            f_user_id, 
            user_id
        )

    @classmethod        
    def _action_btns(cls):
        """
        조작 섹션 UI 생성.

        Returns
        -------
        Tuple[bool, bool, bool, bool, bool, bool, str]
            승인/정지/삭제/승인해제/정지해제/비번변경 버튼 클릭 플래그 + 입력 비밀번호 문자열.
        """
        st.markdown("2) 조작")

        col1, col2 = st.columns(2)
        with col1:
            # 대상 계정 승인
            a_signup = st.button(
                "승인",
                use_container_width=True,
                type="primary",
                help=AdminBtns.SIGNUP_TRUE
            )
            # 대상 계정 정지
            a_block = st.button(
                "정지",
                use_container_width=True,
                help=AdminBtns.BLOCK_TRUE
            )
            # 대상 계정 삭제 (Hard-delete, 위험 → 별도 모달에서 재확인)
            a_delete = st.button(
                "삭제",
                use_container_width=True,
                disabled=KILL_HARD_DELETE_SWITCH,   # 안전 스위치(운영 차단용)
                help=AdminBtns.DELETE
            )
        with col2:
            # 대상 계정 승인 해제
            a_signup_block = st.button(
                "승인 해제",
                use_container_width=True,
                help=AdminBtns.SIGNUP_FALSE
            )
            # 대상 계정 정지 해제
            a_again_use = st.button(
                "정지 해제",
                use_container_width=True,
                help=AdminBtns.BLOCK_FALSE
            )
            # 비밀번호 변경
            pwd_converter = st.button(
                "비번 변경",
                use_container_width=True,
                help=AdminBtns.PASSWORD_CONVERT
            )

        # 비밀번호 입력 칸 (비번 변경 시 사용)
        pwd = st.text_input(
            "신규 비밀번호",
            placeholder="12~64자리 문자열",
            value=FixValues.DEFAULT_PASSWORD
        )

        return (
            a_signup, a_signup_block, 
            a_block, a_again_use,
            a_delete, pwd_converter,
            pwd
        )
    

    
class NoAdmin:
    """
    관리자 권한이 없는 사용자가 접근했을 때 노출되는 페이지.

    책임
    ----
    - 안내 메시지 표시
    - 메인 페이지로 이동하는 버튼 제공
    """

    @classmethod
    def UI(cls):
        """No-Admin 안내 화면 렌더링."""
        st.title("No Admin!")
        st.markdown("---")

        st.error("관리자 권한이 있는 유저만 사용할 수 있습니다!")

        with st.container():
            st.info(NO_ADMIN_USER)

        # Main 페이지 이동
        cls.go_to_main()

    @classmethod
    def go_to_main(cls):
        """
        '메인(Main) 페이지 이동' 버튼 렌더링 및 클릭 시 페이지 전환.
        """
        if st.button(
            "메인(Main) 페이지 이동",
            use_container_width=True,
            type="primary"
        ):
            st.switch_page(PagePath.P0_MAIN)
