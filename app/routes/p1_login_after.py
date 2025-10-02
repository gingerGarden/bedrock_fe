"""
로그인 페이지(`pages/1_login.py`) UI 및 로직 정의.

- AfterLogin: 로그인 성공 후 환영 메시지, 기능 버튼 표시
- UI 컴포넌트를 클래스로 묶어 구조화 및 재사용성 향상
"""
import streamlit as st

from app.constants.values import Ratio
from app.constants.pathes import PagePath
from app.constants.keys import SessionKey, LoginViews
from app.constants.messages import SOFT_DELETE
from app.utils.session import init_session
from app.utils.p1_login import view_changer



class AfterLogin:
    """
    로그인 이후 상태의 UI와 동작.
    """
    @classmethod
    def UI(cls):
        """
        로그인 후 사용자 정보 표시.
        - 환영 메시지
        - 사용자 ID 및 권한
        """
        with st.form("login_after_form"):

            _id = st.session_state[SessionKey.ID]

            st.success(f"{_id}님 환영합니다!")
            st.info(f"* 사용자: {_id}\n* 권한: {cls._role_handler()}")

            # ------------- 필드 -------------
            chat_btn, logout_btn, edit_btn = cls._btns()

        # 폼 블록 밖에서 분기(품 내부가 아닌 "밖"에서 처리)
        if chat_btn:
            st.switch_page(PagePath.P2_CHAT)

        if logout_btn:
            init_session(force=True)
            view_changer(LoginViews.LOGIN_BEFORE)

        if edit_btn: view_changer(LoginViews.EDIT)

    @classmethod
    def _role_handler(cls) -> str:

        if st.session_state[SessionKey.IS_ADMIN]:
            return "관리자"
        
        if st.session_state[SessionKey.IS_DEVELOPER]:
            return "개발자"
        
        return "사용자"

    @classmethod
    def _btns(cls):
        col1, col2, col3 = st.columns(3)
        with col1:
            chat_btn = st.form_submit_button(
                "챗봇으로 이동", type="primary", use_container_width=True
            )
        with col2:
            logout_btn = st.form_submit_button(
                "로그아웃", use_container_width=True
            )
        with col3:
            edit_btn = st.form_submit_button(
                "회원 정보 수정", use_container_width=True
            )
        return chat_btn, logout_btn, edit_btn



class Edit:

    @classmethod
    def UI(cls):

        st.subheader("회원 정보 수정")

        with st.form("edit_form", clear_on_submit=False):

            # ========== 필드 ==========
            # 0) 현재 비밀번호 - 계정 정보 변경을 위한 필수 입력 값
            pwd_current = st.text_input(
                "현재 비밀번호", key="edit_pwd_old", type="password",
                placeholder="계정 정보 변경을 위한 필수 입력 값"
            )
            # 1) 수정이 불가능한 값 - 현상태를 보여주기만 하는 용도
            cls._no_modify_set()
            # 2) 수정이 어렵지만 가능한 값 - 중복 확인 후 변경 가능
            email, email_checker = cls._hard_modify_set()
            # 3) 쉽게 수정해도 되는 값 - 중복 가능
            pwd_new_raw, pwd_new_check, user_name, is_developer\
                = cls._easy_modify_set()
            submit, go_back, soft_delete = cls._action_btn_set()

        # ========== 이벤트 처리 ==========
        if go_back: view_changer(LoginViews.LOGIN_AFTER)

        if soft_delete: view_changer(LoginViews.SOFT_DELETE)

    @classmethod
    def _no_modify_set(cls):
        """
        수정 불가능한 값 - 보여주기만 하는 용도
        """
        # 사용자 계정
        st.text_input(
            "사용자 계정 (변경 불가)", key="edit_user_id", disabled=True,
            placeholder=st.session_state[SessionKey.ID]
        )
        # 사번
        st.text_input(
            "사번 (변경 불가)", key="edit_ktr_id", disabled=True,
            placeholder="#TODO - DB에서 받아온다"
        )

    @classmethod
    def _hard_modify_set(cls):
        """
        수정이 어려운 값 - 중복 확인 필요
        """
        c1, c2 = st.columns(Ratio.LOGIN_BAR_N_BTN)
        with c1:
            email = st.text_input(
                "E-mail", key="edit_email",
                placeholder="#TODO - DB에서 받아온다"
            )
        with c2:
            # user_id 버튼의 "신규 계정" label과 높이를 맞추기 위한 여백
            st.markdown(
                "<div style='height: 1.7rem;'></div>", 
                unsafe_allow_html=True
            )
            email_checker = st.form_submit_button(
                "E-mail 중복 확인",
                use_container_width=True
            )
        return email, email_checker

    @classmethod
    def _easy_modify_set(cls):
        """
        수정 가능한 값
        """
        # [사용자 비밀번호 - 신규 raw]
        pwd_new_raw = st.text_input(
            "신규 비밀번호", key="edit_pwd_raw", type="password",
            placeholder="영문/숫자/특수문자(공백 제외)만 허용 (12~64자)"
        )
        # [사용자 비밀번호 - 신규 raw check]
        pwd_new_check = st.text_input(
            "신규 비밀번호 확인", key="edit_pwd_check", type="password"
        )
        # [사용자 이름]
        user_name = st.text_input(
            "사용자 이름", key="edit_user_name",
            placeholder="한글/영문/특수문자(-_) (2~20자)"
        )
        # [개발자 여부]
        is_developer = st.checkbox(
            "개발자 계정 전환 (관리자 승인이 떨어질 때까지 사용 불가합니다.)", key="edit_is_developer", 
        )
        return (
            pwd_new_raw, pwd_new_check, user_name, is_developer
        )
    
    @classmethod
    def _action_btn_set(cls):
        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.form_submit_button(
                "회원 정보 수정", type="primary", use_container_width=True
            )
        with col2:
            go_back = st.form_submit_button(
                "뒤로 가기", use_container_width=True
            )
        with col3:
            soft_delete = st.form_submit_button(
                "계정 사용 정지", use_container_width=True
            )
        return submit, go_back, soft_delete
    


class SoftDelete:

    @classmethod
    def UI(cls):
        with st.form("block_form"):
            
            # 경고 화면
            _id = st.session_state[SessionKey.ID]

            st.info(SOFT_DELETE)
            
            # 비밀 번호 입력
            pwd_current = st.text_input(
                "현재 비밀번호", key="edit_pwd_old", type="password",
                placeholder="현재 비밀번호를 입력하십시오 (12~64자)"
            )
            # 버튼 모음
            back_btn, block_btn = cls._btns()

        if back_btn: view_changer(LoginViews.EDIT)

    @classmethod
    def _btns(cls):

        # 계정 정지, 뒤로가기 버튼
        col1, col2 = st.columns(2)
        with col1:
            back_btn = st.form_submit_button(
                "뒤로가기", use_container_width=True
            )
        with col2:
            block_btn = st.form_submit_button(
                "계정 사용 정지", use_container_width=True, type="primary"
            )

        return back_btn, block_btn

