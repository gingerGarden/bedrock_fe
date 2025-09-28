"""
로그인 페이지(`pages/1_login.py`) UI 및 로직 정의.

- BeforeLogin: 로그인 폼 표시 및 인증 처리
- UI 컴포넌트를 클래스로 묶어 구조화 및 재사용성 향상
"""
import streamlit as st

from app.schema.keys import SessionKey, LoginViews
from app.schema.values import LOGIN_TXT_BAR_N_BTN_RATIO
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

            # id, password 바
            _id = st.text_input("ID")
            _pwd = st.text_input("Password", type="password")

            # 로그인, 회원가입 버튼
            col1, col2 = st.columns(2)
            with col1:
                login_btn = st.form_submit_button(
                    "로그인", use_container_width=True, type="primary")
            with col2:
                signup_btn = st.form_submit_button(
                    "회원가입", use_container_width=True)

        # 폼 블록 밖에서 분기(품 내부가 아닌 "밖"에서 처리)
        if login_btn:
            cls._login_action(id=_id, pwd=_pwd)

        # signup_btn 클릭 시, View 전환을 위한 분기
        if signup_btn:
            st.session_state[LoginViews.KEY] = LoginViews.SIGN_UP
            st.rerun()

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
            st.session_state[LoginViews.KEY] = LoginViews.LOGIN_AFTER
            
            # UI를 새로 그림
            st.rerun()
        else:
            st.error("로그인 실패. ID 또는 비밀번호를 확인해주세요.")



class SignUp:
    """
    회원가입 관련 UI와 동작.
    같은 파일 내에서만 보이는 '숨김 페이지' 뷰.
    """
    @classmethod
    def UI(cls):

        st.subheader("신규 계정 생성")

        user_id_locked = st.session_state.get("signup_user_id_verified", False)
        ktr_id_locked = st.session_state.get("signup_ktr_id_verified", False)
        email_locked = st.session_state.get("signup_email_verified", False)

        with st.form("signup_form", clear_on_submit=False):

            # ========== 필드 ==========
            user_id, user_id_checker= cls._user_id_set()    
            ktr_id, ktr_id_checker = cls._ktr_id_set()
            email, email_checker = cls._email_set()
            pwd_raw, pwd_check, user_name, is_developer = cls._details_set()
            submit, go_back = cls._action_btn_set()

        # ========== 이벤트 처리 ==========
        if go_back:
            st.session_state[LoginViews.KEY] = LoginViews.LOGIN_BEFORE
            st.rerun()

    @classmethod
    def _user_id_set(cls):
        c1, c2 = st.columns(LOGIN_TXT_BAR_N_BTN_RATIO)
        with c1:
            user_id = st.text_input(
                "신규 계정",
                key="signup_user_id",
                placeholder="영문/숫자/특수문자(-_) 조합 (4~20자)"
            )
        with c2:
            # user_id 버튼의 "신규 계정" label과 높이를 맞추기 위한 여백
            st.markdown(
                "<div style='height: 1.7rem;'></div>", 
                unsafe_allow_html=True
            )
            user_id_checker = st.form_submit_button(
                "계정 중복 확인",
                use_container_width=True
            )
        return user_id, user_id_checker
    
    @classmethod
    def _ktr_id_set(cls):
        c1, c2 = st.columns(LOGIN_TXT_BAR_N_BTN_RATIO)
        with c1:
            ktr_id = st.text_input(
                "사번",
                key="signup_ktr_id",
                placeholder="사번 1개당 1개의 아이디만 생성 가능"
            )
        with c2:
            # user_id 버튼의 "신규 계정" label과 높이를 맞추기 위한 여백
            st.markdown(
                "<div style='height: 1.7rem;'></div>", 
                unsafe_allow_html=True
            )
            ktr_id_checker = st.form_submit_button(
                "사번 중복 확인",
                use_container_width=True
            )
        return ktr_id, ktr_id_checker

    @classmethod
    def _email_set(cls):
        c1, c2 = st.columns(LOGIN_TXT_BAR_N_BTN_RATIO)
        with c1:
            email = st.text_input(
                "E-mail",
                key="signup_email",
                placeholder="E-mail 1개당 1개의 아이디만 생성 가능"
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
    def _details_set(cls):
        # [사용자 비밀번호 - raw]
        pwd_raw = st.text_input(
            "비밀번호", key="signup_pwd_raw", type="password",
            placeholder="영문/숫자/특수문자(공백 제외)만 허용 (12~64자)"
        )
        # [사용자 비밀번호 - raw check]
        pwd_check = st.text_input(
            "비밀번호 확인", key="signup_pwd_check", type="password"
        )
        # [사용자 이름]
        user_name = st.text_input(
            "사용자 이름", key="signup_user_name",
            placeholder="한글/영문/특수문자(-_) (2~20자)"
        )
        # [개발자 여부]
        is_developer = st.checkbox(
            "개발자 계정 (개발자 계정은 관리자 승인이 필요합니다!)", key="signup_is_developer", 
        )
        return (
            pwd_raw, pwd_check, user_name, is_developer
        )
    
    @classmethod
    def _action_btn_set(cls):
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button(
                "회원가입", type="primary", use_container_width=True
            )
        with col2:
            go_back = st.form_submit_button(
                "로그인 화면 이동", use_container_width=True
            )
        return submit, go_back
    
    # TODO - UI에 기능 붙이기 