"""
로그인/회원가입 초기 화면 관련 페이지 구성.

- BeforeLogin: 로그인 폼 UI + 인증 처리
- SignUp: 회원가입 폼 UI + 중복검사 버튼 로직
- ShowPersonalInfoAgree: 개인정보 수집 안내 화면

구현 메모
---------
- 모든 화면은 Streamlit `st.form` 기반으로, 폼 내부에서 입력/버튼을 렌더링하고
  폼 블록 "밖"에서 클릭 이벤트를 분기 처리한다(rerun/화면전환 안정성).
- 회원가입 필드의 '중복 확인' 버튼은 세션키(SignupKey.*)를 이용해
  버튼 색(검증 통과: primary / 미통과: secondary)과 메시지를 동기화한다.
"""
from typing import Optional, Tuple

import streamlit as st

from app.api.p1_login import verify_login
from app.constants.values import UserInfo, Ratio
from app.constants.keys import SessionKey, LoginViews, SignupKey
from app.constants.messages import LoginMsg, LoginSignupMsg, PERSONAL_INFO_AGREE
from app.schema.p1_login import UserLogin
from app.utils.p1_login import view_changer, SignUpAction, SignUpUniqueKeys



class BeforeLogin:
    """
    로그인 이전 상태의 UI와 동작 관리 클래스.

    책임
    ----
    - 로그인 입력 폼(ID/비밀번호) 표시
    - 로그인 버튼 클릭 시 프론트/백엔드 검증
    - 회원가입 버튼 클릭 시 회원가입 화면으로 이동
    """
    @classmethod
    def UI(cls):
        """
        로그인/회원가입 폼 렌더링 및 이벤트 처리.

        동작 흐름
        --------
        1) 로그인 폼에 ID, Password 입력
        2) '로그인' 버튼 클릭 → _login_action() 실행
        3) '회원가입' 버튼 클릭 → view_changer(LoginViews.SIGN_UP) 호출
        """

        st.title("Login")
        st.markdown("---")

        with st.form("login_form"):

            # ID/Password 입력 + 버튼 렌더링
            _id, _pwd, login_btn, signup_btn = cls._id_pwd_set()

        # ========== 이벤트 처리 ==========
        # 로그인 버튼 → 로그인 프로세스 실행
        if login_btn: cls._login_action(user_id=_id, pwd=_pwd)
            
        # 회원가입 버튼 → 회원가입 화면으로 이동
        if signup_btn: view_changer(LoginViews.SIGN_UP)

    @classmethod
    def _id_pwd_set(
            cls
        ) -> Tuple[str, str, bool, bool]:
        """
        로그인 입력 필드와 버튼 UI를 렌더링하고 현재 입력/클릭 상태를 반환.

        Returns
        -------
        (user_id, password, login_clicked, signup_clicked)
        """
        # id, password 바
        _id = st.text_input("ID")
        _pwd = st.text_input("Password", type="password")

        # 로그인, 회원가입 버튼
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button(
                "로그인", 
                use_container_width=True, 
                type="primary"
            )
        with col2:
            signup_btn = st.form_submit_button(
                "회원가입", 
                use_container_width=True
            )
        
        return _id, _pwd, login_btn, signup_btn

    @classmethod
    def _login_action(cls, user_id: str, pwd: str):
        """
        '로그인' 버튼 클릭 시 실행되는 프로세스.

        처리 단계
        --------
        1) FE 1차 검증(_user_login_fe_error_msg)
        2) 통과 시 BE 호출(_login_action_send_to_backend)
        3) 실패 시 오류 메시지 표시
        """
        # FE에서 id, password 1차 검증
        msg = cls._user_login_fe_error_msg(user_id, password=pwd)
        if msg is None:
            cls._login_action_send_to_backend(user_id, pwd)
        else:
            st.error(msg)

    @classmethod
    def _login_action_send_to_backend(cls, user_id: str, pwd: str):
        """
        BE API(verify_login) 호출 및 로그인 성공 처리.

        동작
        ----
        - verify_login(user_id, password) 호출
        - 성공: 세션 상태 갱신(SessionKey.*) 후 로그인 후 화면으로 전환
        - 실패: 백엔드 메시지 표시
        """
        # 백엔드와 통신
        access, msg, values = verify_login(user_id=user_id, password=pwd)
        if access:
            st.session_state[SessionKey.LOGGED_IN] = True
            st.session_state[SessionKey.ID] = user_id
            st.session_state[SessionKey.IS_DEVELOPER] = values[UserInfo.DEVELOPER]
            st.session_state[SessionKey.IS_ADMIN] = values[UserInfo.ADMIN]
            st.session_state[SessionKey.USER_NAME] = values[UserInfo.USER_NAME]
            st.session_state[SessionKey.KTR_ID] = values[UserInfo.KTR_ID]
            st.session_state[SessionKey.EMAIL] = values[UserInfo.EMAIL]
            # View 변경
            view_changer(LoginViews.LOGIN_AFTER)
        else:
            st.error(msg)

    @classmethod
    def _user_login_fe_error_msg(
            cls,
            user_id: str, 
            password: str
        ) -> Optional[str]:
        """
        Frontend 1차 검증(빠른 피드백용).

        검증 항목
        --------
        1) 미입력(null) 체크
        2) Pydantic(UserLogin) 기반 제약 조건(길이/패턴) 검증

        Returns
        -------
        - 에러가 있으면 사용자 메시지(str)
        - 통과하면 None
        """
        # 1) 값 자체가 비어있는 경우
        if not user_id:
            return LoginMsg.ID_NULL
        if not password:
            return LoginMsg.PWD_NULL
        
        # 2) 제약 조건 검증 (길이, 패턴 등)
        try:
            UserLogin(user_id=user_id, password=password)
        except:
            return LoginMsg.ID_AND_PWD_WRONG
        
        return None    


class SignUp:
    """
    회원가입 UI와 동작 처리 클래스.

    책임
    ----
    - 신규 계정 입력 필드(user_id, ktr_id, email, 비밀번호, 이름, 개발자 여부) 렌더링
    - 각 필드의 '중복 확인' 버튼 제공 및 결과 메시지/색상 반영
    - '회원가입' 제출 시 SignUpAction.run() 호출(최종 검증+BE 연동)
    """
    @classmethod
    def UI(cls):
        """
        회원가입 화면 렌더링 + 이벤트 처리.
        - 중복 키 세션 초기화(SignUpUniqueKeys.keys_rock)
        - 각 필드/버튼 렌더링
        - 폼 밖에서 이벤트 분기(중복확인/제출/이동)
        """
        st.subheader("신규 계정 생성")

        # 중복 키 검증 상태 세션 초기화(버튼 색/메시지 구동용)
        SignUpUniqueKeys.keys_rock()

        with st.form("signup_form", clear_on_submit=False):

            # ========== 필드 ==========
            user_id, user_id_checker= cls._user_id_set()
            ktr_id, ktr_id_checker = cls._ktr_id_set()
            email, email_checker = cls._email_set()
            pwd_raw, pwd_check, user_name, is_developer = cls._details_set()
            p_info_agree = cls._personal_info_agree_set()
            submit, show_p_info_agree, go_back = cls._action_btn_set()

        # ========== 이벤트 처리 ==========
        # 개인정보 수집 안내로 이동
        if show_p_info_agree: view_changer(LoginViews.PERSONAL_INFO_AGREE)
            
        # 로그인 화면으로 이동
        if go_back: view_changer(LoginViews.LOGIN_BEFORE)

        # 계정 중복 확인 버튼
        if user_id_checker: SignUpUniqueKeys.checker_action(user_id=user_id)
        
        # 사번 중복 확인 버튼
        if ktr_id_checker: SignUpUniqueKeys.checker_action(ktr_id=ktr_id)

        # 이메일 중복 확인 버튼
        if email_checker: SignUpUniqueKeys.checker_action(email=email)

        # 회원가입 제출(최종 검토 → BE 호출)
        if submit: SignUpAction.run(
            user_id=user_id,
            ktr_id=ktr_id,
            email=email,
            pwd_raw=pwd_raw,
            pwd_check=pwd_check,
            user_name=user_name,
            is_developer=is_developer,
            p_info_agree=p_info_agree
        )

    # user_id 버튼 셋
    @classmethod
    def _user_id_set(cls) -> Tuple[str, bool]:
        """
        신규 계정(user_id) 입력 + '계정 중복 확인' 버튼 렌더링.

        버튼 상태
        --------
        - SignUpUniqueKeys.set_condition() 결과에 따라 primary/secondary 지정
        - SignUpUniqueKeys.set_show_msg()로 중복 결과 메시지 출력

        Returns
        -------
        tuple[str, bool] : (입력한 user_id, '중복 확인' 클릭 여부)
        """
        # 세션에 저장된 값에 따라 변경되는 내용
        btn_type, msg = SignUpUniqueKeys.set_condition(
            bool_key=SignupKey.USER_ID, msg_key=SignupKey.USER_ID_MSG
        )
        # 버튼 렌더링
        c1, c2 = st.columns(Ratio.LOGIN_BAR_N_BTN)
        with c1:
            user_id = st.text_input(
                "신규 계정",
                key="signup_user_id",
                placeholder=LoginSignupMsg.USER_ID_PAT
            )
        with c2:
            # user_id 버튼의 "신규 계정" label과 높이를 맞추기 위한 여백
            st.markdown(
                "<div style='height: 1.7rem;'></div>", 
                unsafe_allow_html=True
            )
            # 버튼
            user_id_checker = st.form_submit_button(
                "계정 중복 확인",
                use_container_width=True,
                type=btn_type
            )
        # 메시지 출력
        SignUpUniqueKeys.set_show_msg(bool_key=SignupKey.USER_ID, message=msg)

        return user_id, user_id_checker

    @classmethod
    def _ktr_id_set(cls) -> Tuple[str, bool]:
        """
        사번(ktr_id) 입력 + '사번 중복 확인' 버튼 렌더링.

        Returns
        -------
        tuple[str, bool] : (입력한 ktr_id, '중복 확인' 클릭 여부)
        """
        # 세션에 저장된 값에 따라 변경되는 내용
        btn_type, msg = SignUpUniqueKeys.set_condition(
            bool_key=SignupKey.KTR_ID, msg_key=SignupKey.KTR_ID_MSG
        )

        # 버튼 렌더링
        c1, c2 = st.columns(Ratio.LOGIN_BAR_N_BTN)
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
            # 버튼
            ktr_id_checker = st.form_submit_button(
                "사번 중복 확인",
                use_container_width=True,
                type=btn_type
            )

        # 메시지 출력
        SignUpUniqueKeys.set_show_msg(
            bool_key=SignupKey.KTR_ID, 
            message=msg
        )

        return ktr_id, ktr_id_checker

    @classmethod
    def _email_set(cls) -> Tuple[str, bool]:
        """
        이메일(email) 입력 + 'E-mail 중복 확인' 버튼 렌더링.

        Returns
        -------
        tuple[str, bool] : (입력한 email, '중복 확인' 클릭 여부)
        """
        # 세션에 저장된 값에 따라 변경되는 내용
        btn_type, msg = SignUpUniqueKeys.set_condition(
            bool_key=SignupKey.EMAIL, msg_key=SignupKey.EMAIL_MSG
        )
        # 버튼 렌더링
        c1, c2 = st.columns(Ratio.LOGIN_BAR_N_BTN)
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
                use_container_width=True,
                type=btn_type
            )

        # 메시지 출력
        SignUpUniqueKeys.set_show_msg(
            bool_key=SignupKey.EMAIL, 
            message=msg
        )

        return email, email_checker
    
    @classmethod
    def _details_set(cls) -> Tuple[str, str, str, bool]:
        """
        기타 상세 정보 입력(비밀번호/비밀번호 확인/사용자 이름/개발자 여부).

        Returns
        -------
        tuple[str, str, str, bool]
            (pwd_raw, pwd_check, user_name, is_developer)
        """
        # [사용자 비밀번호 - raw]
        pwd_raw = st.text_input(
            "비밀번호", 
            key="signup_pwd_raw", 
            type="password",
            placeholder=LoginSignupMsg.PWD_PAT
        )
        # [사용자 비밀번호 - raw check]
        pwd_check = st.text_input(
            "비밀번호 확인", 
            key="signup_pwd_check", 
            type="password"
        )
        # [사용자 이름]
        user_name = st.text_input(
            "사용자 이름 (별명)", 
            key="signup_user_name",
            placeholder=LoginSignupMsg.USER_NAME_PAT
        )
        # [개발자 여부]
        is_developer = st.checkbox(
            "개발자 계정 (개발자 계정은 관리자 승인이 필요합니다!)", 
            key="signup_is_developer", 
        )
        return (
            pwd_raw, pwd_check, user_name, is_developer
        )
    
    @classmethod
    def _personal_info_agree_set(cls) -> bool:
        """
        개인정보 수집 동의 체크박스 섹션.

        Returns
        -------
        bool : 체크 여부
        """
        st.markdown("---")
        
        p_info_agree = st.checkbox(
            "(필수) 개인정보 수집에 동의합니다.",
            key="signup_personal_info_agree", 
        )
        return p_info_agree
    
    @classmethod
    def _action_btn_set(cls) -> Tuple[bool, bool, bool]:
        """
        하단 액션 버튼(회원가입, 개인정보 수집 안내 보기, 로그인 화면 이동) 렌더링.

        Returns
        -------
        tuple[bool, bool, bool]
            (submit_clicked, show_p_info_clicked, go_back_clicked)
        """
        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.form_submit_button(
                "회원가입", type="primary", use_container_width=True
            )
        with col2:
            show_p_info_agree = st.form_submit_button(
                "개인정보 수집 내용 확인", use_container_width=True
            )

        with col3:
            go_back = st.form_submit_button(
                "로그인 화면 이동", use_container_width=True
            )
        return submit, show_p_info_agree, go_back
    


class ShowPersonalInfoAgree:
    """
    개인정보 수집 안내 문구 화면.
    - 안내문 출력
    - '회원가입 화면으로 돌아가기' 버튼 클릭 시 회원가입 화면으로 이동
    - 돌아갈 때 중복검사 세션 상태를 초기화하여 버튼/메시지가 최신 상태로 반영되도록 함
    """
    @classmethod
    def UI(cls):
        """
        개인정보 수집 안내 화면 렌더링 + 이벤트 처리.
        """
        st.subheader("개인정보 수집에 대한 내용")

        with st.form("show_personal_info_form"):

            st.markdown(PERSONAL_INFO_AGREE)

            back_btn = st.form_submit_button(
                "회원가입 화면으로 돌아가기", 
                type="primary", 
                use_container_width=True
            )

        # 중복검사 세션 상태 초기화(버튼 색/메시지 일관성 유지)
        SignUpUniqueKeys.keys_rock_init()

        if back_btn: view_changer(LoginViews.SIGN_UP)