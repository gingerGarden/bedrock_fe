"""
로그인 페이지(`pages/1_login.py`) UI 및 로직 정의.

- BeforeLogin: 로그인 폼 표시 및 인증 처리
- AfterLogin: 로그인 성공 후 환영 메시지, 기능 버튼 표시
- UI 컴포넌트를 클래스로 묶어 구조화 및 재사용성 향상
"""
import streamlit as st

from app.schema.pathes import PagePath
from app.schema.keys import SessionKey
from app.utils.session import init_session
from app.utils.auth import verify_user



class BeforeLogin:
    """
    로그인 이전 상태의 UI와 동작.
    """
    @classmethod
    def UI(cls):
        """
        ID/Password 입력 폼 렌더링.
        - st.form을 사용해 'Login' 버튼 클릭 시만 제출.
        """
        with st.form("login_form"):

            id = st.text_input("ID")
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            # submit 클릭 시
            if submitted:
                cls._login_action(id=id, pwd=pwd)

    @classmethod
    def _login_action(cls, id: str, pwd: str):
        """
        사용자 인증 처리.
        - verify_user로 ID/비밀번호 검증
        - 성공: 세션 상태 갱신, st.rerun()으로 UI 갱신
        - 실패: 오류 메시지 출력
        """
        is_valid, role = verify_user(id, pwd)
        if is_valid:
            st.session_state[SessionKey.LOGGED_IN] = True
            st.session_state[SessionKey.ID] = id
            st.session_state[SessionKey.ROLE] = role
            
            # UI를 새로 그림
            st.rerun()
        else:
            st.error("로그인 실패. ID 또는 비밀번호를 확인해주세요.")



class AfterLogin:
    """
    로그인 이후 상태의 UI와 동작.
    """
    @staticmethod
    def UI():
        """
        로그인 후 사용자 정보 표시.
        - 환영 메시지
        - 사용자 ID 및 권한
        """
        _id = st.session_state[SessionKey.ID]
        _role = st.session_state[SessionKey.ROLE]

        st.success(f"{_id}님 환영합니다!")
        st.info(f"* 사용자: {_id}\n* 권한: {_role}")

    @staticmethod
    def go_to_chat():
        """
        'Go to Chat' 버튼.
        - 클릭 시 채팅 페이지로 이동
        """
        if st.button(
            "Go to Chat", 
            use_container_width=True, 
            type="primary"
        ):
            st.switch_page(PagePath.P2_CHAT)
    
    @staticmethod
    def logout():
        """
        'Logout' 버튼.
        - 클릭 시 세션 초기화(init_session(force=True))
        - UI 갱신으로 로그인 페이지로 복귀
        """
        st.button(
            "Logout",
            on_click=lambda: init_session(force=True),
            use_container_width=True
        )