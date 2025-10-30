"""
로그인 페이지(`pages/1_login.py`) UI 및 로직 정의.

- AfterLogin : 로그인 성공 후 환영/정보/네비게이션 버튼
- Edit       : 본인 정보 수정(현재 비밀번호 요구, 이메일 중복검사 등)
- SoftDelete : 본인 계정 사용 정지(Soft-delete) 확인/실행

UI는 Streamlit `st.form` 기반으로, 폼 내에서 입력과 버튼을 렌더링하고
폼 블록 **밖**에서 이벤트를 처리하여 사이드이펙트(페이지 이동, 세션 변경 등)를 수행한다.
"""
import streamlit as st
from typing import Tuple

from app.constants.values import Ratio
from app.constants.pathes import PagePath
from app.constants.keys import SessionKey, LoginViews, SignupKey
from app.constants.messages import SOFT_DELETE
from app.utils.session import init_session
from app.utils.p1_login import (
    view_changer, input_cleaner, SignUpUniqueKeys,
    SoftDeleteAction, EditAction
)



class AfterLogin:
    """
    로그인 이후 화면.

    책임
    ----
    - 환영 메시지 및 기본 정보(ID/사번/이메일/권한) 표시
    - 주요 동작 버튼 제공: 챗봇 이동, 로그아웃, 회원정보 수정
    """
    @classmethod
    def UI(cls):
        """
        AfterLogin 메인 뷰 렌더링 + 폼 외부 이벤트 처리.
        """
        st.title("Welcome Back!")
        st.markdown("---")

        with st.form("login_after_form"):

            # 세션에 저장된 유저 정보 표시
            _name = st.session_state[SessionKey.USER_NAME]
            _id = st.session_state[SessionKey.ID]
            _ktr_id = st.session_state[SessionKey.KTR_ID]
            _email = st.session_state[SessionKey.EMAIL]

            st.success(f'**"{_name}"님 환영합니다!**')
            st.info(
                f"""
                ```markdown
                - ID : {_id}
                - 사번 : {_ktr_id}
                - 이메일 : {_email}
                - 권한 : {cls._role_handler()}
                ```
                """
            )
            # 동작 버튼(챗봇, 로그아웃, 회원정보 수정)
            chat_btn, logout_btn, edit_btn = cls._btns()

        # ===== 폼 블록 밖에서 이벤트 처리 =====
        if chat_btn:
            st.switch_page(PagePath.P2_CHAT)

        if logout_btn:
            # 세션 초기화 후 로그인 전 화면으로
            init_session(force=True)
            view_changer(LoginViews.LOGIN_BEFORE)

        if edit_btn: view_changer(LoginViews.EDIT)

    @classmethod
    def _role_handler(cls) -> str:
        """
        세션의 권한 플래그를 읽어 사용자/개발자/관리자 문자열 반환.
        """
        if st.session_state[SessionKey.IS_ADMIN]:
            return "관리자"
        
        if st.session_state[SessionKey.IS_DEVELOPER]:
            return "개발자"
        
        return "사용자"

    @classmethod
    def _btns(cls) -> Tuple[bool, bool, bool]:
        """
        하단 버튼 3종(챗봇/로그아웃/회원정보 수정) 렌더링.
        Returns
        -------
        tuple[bool, bool, bool] : (chat_btn, logout_btn, edit_btn) 클릭 여부
        """
        col1, col2, col3 = st.columns(3)
        with col1:
            chat_btn = st.form_submit_button(
                "챗봇으로 이동", 
                type="primary", 
                use_container_width=True
            )
        with col2:
            logout_btn = st.form_submit_button(
                "로그아웃", 
                use_container_width=True
            )
        with col3:
            edit_btn = st.form_submit_button(
                "회원 정보 수정", 
                use_container_width=True
            )
        return chat_btn, logout_btn, edit_btn



class Edit:
    """
    회원 정보 수정 화면.

    책임
    ----
    - 수정 불가 필드(ID/사번) 표시
    - 수정 가능 필드(이메일/이름/개발자신청/비밀번호 변경) 입력
    - 이메일은 중복확인 플로우 제공(SignUpUniqueKeys 이용)
    - 제출 시 EditAction.run으로 백엔드 호출
    """
    @classmethod
    def UI(cls):
        """
        Edit 메인 뷰 렌더링 + 이벤트 처리.
        - 이메일 중복 확인은 별도의 버튼(폼 내 submit 버튼)으로 처리
        - 회원 정보 수정은 현재 비밀번호 필수
        """
        st.subheader("회원 정보 수정")

        # 이메일 중복확인 UI 상태를 위한 세션키 초기화
        SignUpUniqueKeys.keys_rock()

        with st.form("edit_form", clear_on_submit=False):

            # ========== 필드 ==========
            # 0) 현재 비밀번호 - 계정 정보 변경을 위한 필수 입력 값
            pwd_current = st.text_input(
                "현재 비밀번호", 
                key="edit_pwd_old", 
                type="password",
                placeholder="계정 정보 변경을 위한 필수 입력 값"
            )
            # 1) 수정 불가(ID, 사번) - 현상태를 보여주기만 하는 용도
            cls._no_modify_set()
            # 2) 중복 확인이 필요한 필드(이메일)
            email, email_checker = cls._hard_modify_set()
            # 3) 비교적 자유롭게 수정 가능한 필드(비번/이름/개발자)
            pwd_new_raw, pwd_new_check, user_name, is_developer\
                = cls._easy_modify_set()
            submit, go_back, soft_delete = cls._action_btn_set()

        # ========== 이벤트 처리 ==========
        # 이메일 중복 확인
        if email_checker: SignUpUniqueKeys.checker_action(email=email)

        # 회원 정보 수정
        if submit: EditAction.run(
            pwd_current=input_cleaner(pwd_current),
            user_name=input_cleaner(user_name),
            developer=input_cleaner(is_developer, is_boolean=True),
            email=input_cleaner(email),
            pwd_new_raw=input_cleaner(pwd_new_raw),
            pwd_new_check=input_cleaner(pwd_new_check),
        )
        # 뒤로 가기
        if go_back: view_changer(LoginViews.LOGIN_AFTER)

        # 계정 사용 정지 화면으로 이동
        if soft_delete: view_changer(LoginViews.SOFT_DELETE)

    @classmethod
    def _no_modify_set(cls):
        """
        수정 불가 필드 렌더링(ID/사번). placeholder로 현재 값만 표시.
        """
        # 사용자 계정
        st.text_input(
            "사용자 계정 (변경 불가)", 
            key="edit_user_id", 
            disabled=True,
            placeholder=st.session_state[SessionKey.ID]
        )
        # 사번
        st.text_input(
            "사번 (변경 불가)", 
            key="edit_ktr_id", 
            disabled=True,
            placeholder=st.session_state[SessionKey.KTR_ID]
        )

    @classmethod
    def _hard_modify_set(cls) -> Tuple[str, bool]:
        """
        중복 확인이 필요한 필드 렌더링(이메일).
        - SignUpUniqueKeys.set_condition()으로 버튼 색/메시지 상태 결정
        Returns
        -------
        tuple[str, bool] : (입력 이메일, '중복 확인' 버튼 클릭 여부)
        """
        # 세션에 저장된 값에 따라 변경되는 내용
        btn_type, msg = SignUpUniqueKeys.set_condition(
            bool_key=SignupKey.EMAIL, msg_key=SignupKey.EMAIL_MSG
        )
        c1, c2 = st.columns(Ratio.LOGIN_BAR_N_BTN)
        with c1:
            email = st.text_input(
                "E-mail", 
                key="edit_email",
                placeholder=st.session_state[SessionKey.EMAIL]
            )
        with c2:
            # user_id 버튼의 "신규 계정" label과 높이를 맞추기 위한 여백
            st.markdown(
                "<div style='height: 1.7rem;'></div>", 
                unsafe_allow_html=True
            )
            email_checker = st.form_submit_button(
                "E-mail 중복 확인",
                use_container_width=True,
                type=btn_type
            )

        # 중복확인 결과 메시지
        SignUpUniqueKeys.set_show_msg(bool_key=SignupKey.EMAIL, message=msg)

        return email, email_checker

    @classmethod
    def _easy_modify_set(cls) -> Tuple[str, str, str, bool]:
        """
        자유 변경 가능 필드 렌더링(새 비밀번호/확인, 사용자 이름, 개발자 전환).
        Returns
        -------
        tuple[str, str, str, bool]
        """
        # [사용자 비밀번호 - 신규 raw]
        pwd_new_raw = st.text_input(
            "신규 비밀번호", 
            key="edit_pwd_raw", 
            type="password",
            placeholder="영문/숫자/특수문자(공백 제외)만 허용 (12~64자)"
        )
        # [사용자 비밀번호 - 신규 raw check]
        pwd_new_check = st.text_input(
            "신규 비밀번호 확인", 
            key="edit_pwd_check", 
            type="password"
        )
        # [사용자 이름]
        user_name = st.text_input(
            "사용자 이름 (별명)", 
            key="edit_user_name",
            placeholder="한글/영문/특수문자(-_) (2~20자)"
        )
        # [개발자 여부]
        is_developer = st.checkbox(
            "개발자 계정 전환 (관리자 승인이 떨어질 때까지 사용 불가합니다.)", 
            key="edit_is_developer", 
        )
        return (
            pwd_new_raw, pwd_new_check, user_name, is_developer
        )
    
    @classmethod
    def _action_btn_set(cls) -> Tuple[bool, bool, bool]:
        """
        하단 액션 버튼 3종(수정/뒤로/계정 정지) 렌더링.
        Returns
        -------
        tuple[bool, bool, bool] : (submit, go_back, soft_delete)
        """
        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.form_submit_button(
                "회원 정보 수정", 
                type="primary", 
                use_container_width=True
            )
        with col2:
            go_back = st.form_submit_button(
                "뒤로 가기", 
                use_container_width=True
            )
        with col3:
            soft_delete = st.form_submit_button(
                "계정 사용 정지", 
                use_container_width=True
            )
        return submit, go_back, soft_delete
    


class SoftDelete:
    """
    계정 사용 정지(Soft-delete) 화면.

    책임
    ----
    - 안내문(SOFT_DELETE) 표시
    - 비밀번호 재입력 후 정지 실행(SoftDeleteAction.run)
    - 취소 시 이전 화면(EDIT)으로 복귀
    """
    @classmethod
    def UI(cls):
        """
        SoftDelete 메인 뷰 렌더링 + 이벤트 처리.
        """
        st.subheader("계정 사용 정지 신청")

        with st.form("block_form"):
            
            # 경고/안내
            st.info(SOFT_DELETE)
            
            # 본인 확인용 비밀번호
            _pwd = st.text_input(
                "비밀번호", 
                key="edit_pwd_old", 
                type="password",
                placeholder="비밀번호를 입력하십시오 (12~64자)"
            )
            # 액션 버튼
            back_btn, block_btn = cls._btns()

        # ========== 이벤트 처리 ==========
        # 뒤로가기
        if back_btn: view_changer(LoginViews.EDIT)

        # 계정 정지 버튼
        if block_btn: SoftDeleteAction.run(password=_pwd)

    @classmethod
    def _btns(cls) -> Tuple[bool, bool]:
        """
        뒤로가기 / 계정 정지 버튼 렌더링.
        Returns
        -------
        tuple[bool, bool] : (back_btn, block_btn)
        """
        # 계정 정지, 뒤로가기 버튼
        col1, col2 = st.columns(2)
        with col1:
            back_btn = st.form_submit_button(
                "뒤로가기", 
                use_container_width=True
            )
        with col2:
            block_btn = st.form_submit_button(
                "계정 사용 정지", 
                use_container_width=True, 
                type="primary"
            )
        return back_btn, block_btn

