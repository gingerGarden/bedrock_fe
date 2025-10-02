"""
로그인/회원가입 유틸 함수 모음.

- view_changer: 현재 화면(View) 변경 후 UI 리렌더링
- SignUpUniqueKey: 회원가입 시 unique key(user_id, ktr_id, email) 중복 검사 처리
"""

import streamlit as st

from typing import Tuple, Optional, Callable, Any
from pydantic import BaseModel

from app.api.p1_login import verify_unique_key
from app.constants.keys import SignupKey, LoginViews
from app.constants.messages import LoginSignup
from app.schema.p1_login import UniqueKeys, Password, UserName



def view_changer(view_name: str):
    """
    로그인 뷰 상태 전환 후 즉시 rerun.

    매개변수
    --------
    view_name : str
        이동할 뷰 이름 (LoginViews.*)

    동작
    ----
    - 세션 상태(LoginViews.KEY)를 새로운 뷰 이름으로 변경
    - st.rerun() 호출하여 UI를 다시 그림
    """
    # View 변경
    st.session_state[LoginViews.KEY] = view_name
    # UI를 새로 그림
    st.rerun()



class SignUpUniqueKeys:
    """
    회원가입 중복 검사 관련 유틸 클래스.

    책임
    ----
    - 버튼 색/메시지 상태 결정 (`set_condition`)
    - 메시지 출력 (`set_show_msg`)
    - 버튼 클릭 시 BE API 호출 및 세션 갱신 (`checker_action`)
    """

    @classmethod
    def keys_rock(cls):
        """
        회원가입 화면 최초 진입 시, 중복 검사 결과 세션 상태 초기화.

        설명
        ----
        - SignupKey.USER_ID, SignupKey.KTR_ID, SignupKey.EMAIL 값을 
          모두 False로 초기화한다.
        - 이미 세션에 값이 있으면 유지하고, 없을 경우만 False를 세팅한다.
        - 이 과정을 통해 중복검사 버튼 상태 및 메시지 출력 로직이 
          예측 가능하게 동작하도록 한다.

        사용처
        ----
        - SignUp UI 클래스의 `UI()` 진입 초기에 호출하여,
          세션 상태의 일관성을 보장.
        """
        if not st.session_state.get(SignupKey.USER_ID, False):
            st.session_state[SignupKey.USER_ID] = False
        if not st.session_state.get(SignupKey.KTR_ID, False):
            st.session_state[SignupKey.KTR_ID] = False
        if not st.session_state.get(SignupKey.EMAIL, False):
            st.session_state[SignupKey.EMAIL] = False

    @classmethod
    def set_condition(
            cls, 
            bool_key: str = SignupKey.USER_ID, 
            msg_key: str = SignupKey.USER_ID_MSG
        ) -> Tuple[str, str]:
        """
        버튼의 색상과 메시지를 세션 상태에 따라 결정.

        매개변수
        --------
        bool_key : str
            해당 key가 True일 경우 버튼은 primary, False일 경우 secondary
        msg_key : str
            버튼 클릭 결과 메시지가 저장된 세션 key

        반환값
        --------
        Tuple[str, str]
            (버튼 타입(primary/secondary), 메시지 문자열 or None)
        """
        # 버튼 색깔: 검증 성공(True) → primary, 실패(False) → secondary
        btn_type = "primary" if st.session_state[bool_key] else "secondary"
        # 메시지 조회 (없으면 None)
        msg = st.session_state.get(msg_key, None)
        return btn_type, msg
    
    @classmethod
    def set_show_msg(
            cls, 
            bool_key: str, 
            message: Optional[str]
        ):
        """
        메시지를 출력하는 함수.

        매개변수
        --------
        bool_key : str
            True → st.info 출력, False → st.error 출력
        message : Optional[str]
            출력할 메시지 (None이면 출력하지 않음)
        """
        if message is not None:
            if st.session_state[bool_key]:
                st.info(message)
            else:
                st.error(message)

    @classmethod
    def checker_action(
            cls, 
            user_id: Optional[str] = None,
            ktr_id: Optional[str] = None,
            email: Optional[str] = None
        ):
        """
        중복 확인 버튼 클릭 시 호출되는 메서드.

        동작
        ----
        1. 어떤 key(user_id/ktr_id/email)를 검사 중인지 식별
        2. 입력값의 유효성(빈값/패턴 불일치) 검증
        3. BE API(verify_unique_key) 호출 → 중복 여부 확인
        4. 세션 상태(st.session_state)에 결과 반영
        5. st.rerun()으로 즉시 UI 갱신

        매개변수
        --------
        user_id : Optional[str]
        ktr_id : Optional[str]
        email : Optional[str]
            셋 중 하나만 값이 있어야 하며, 나머지는 None
        """

        # 1. 대상 Unique-key에 대한 session 내 변수 이름 정의
        tg_key, tg_msg_key = cls._checker_action_key(user_id, ktr_id, email)

        # 2. value 유효성 확인 (빈값, 형식 위반 여부)
        keep_going, msg = cls._checker_action_value(user_id, ktr_id, email)

        # 3. 백엔드 서버로 값 조회 (형식이 유효할 때만)
        if keep_going:
            duplicated, msg, _ = verify_unique_key(user_id, ktr_id, email)
        else:
            # 형식 위반 → 세션 상태 업데이트 후 즉시 rerun
            st.session_state[tg_key] = False
            st.session_state[tg_msg_key] = msg
            st.rerun()
            return
        
        # 4. 결과 정리 및 세션 반영
        if duplicated:
            # 중복된 경우 → 실패
            st.session_state[tg_key] = False
            st.session_state[tg_msg_key] = msg
        else:
            # 중복되지 않은 경우 → 성공
            st.session_state[tg_key] = True
            st.session_state[tg_msg_key] = msg

        # 5. 즉시 UI 갱신
        st.rerun()

    @classmethod
    def _checker_action_key(
            cls, 
            user_id: Optional[str],
            ktr_id: Optional[str],
            email: Optional[str]
        ) -> str:
        """
        어떤 unique key를 검사하는지 결정.

        반환값
        --------
        (세션 상태 bool key, 세션 상태 msg key)

        예:
        user_id → (SignupKey.USER_ID, SignupKey.USER_ID_MSG)
        """
        # 대상 unique key 정의
        if user_id is not None:
            return SignupKey.USER_ID, SignupKey.USER_ID_MSG
        elif ktr_id is not None:
            return SignupKey.KTR_ID, SignupKey.KTR_ID_MSG
        elif email is not None:
            return SignupKey.EMAIL, SignupKey.EMAIL_MSG
        else:
            raise ValueError(LoginSignup.ENTER_TOO_MUCH)
        
    @classmethod
    def _checker_action_value(
            cls, 
            user_id: Optional[str],
            ktr_id: Optional[str],
            email: Optional[str]
        ) -> Tuple[bool, str]:
        """
        입력값 검증 로직.

        동작
        ----
        - 빈값인지 확인 ("" → 실패)
        - UniqueKeys(pydantic)로 패턴 검증
        - 실패 시 적절한 오류 메시지 반환

        반환값
        --------
        (keep_going: bool, msg: str)
        keep_going=True → BE API 호출 가능
        keep_going=False → 오류 메시지 출력 후 중단
        """
        # 값이 None이 아닌 것을 value로 정의
        for k, v in {"user_id":user_id, "ktr_id":ktr_id, "email":email}.items():
            if v is not None:
                value = v
                key = k
                break

        # 1) 빈값인 경우
        if value == "":
            keep_going = False
            msg = LoginSignup.ENTER_NULL
            return keep_going, msg

        # 2) 형식 검증 (Pydantic 모델)
        try:
            UniqueKeys(user_id=user_id, ktr_id=ktr_id, email=email)
            keep_going = True
            msg = None
        except:
            keep_going = False
            msg = LoginSignup.ENTER_OVER
            # user_id 오류 시 추가 안내 메시지 포함
            if key == "user_id":
                msg = f"{msg} ({LoginSignup.USER_ID_PAT})"
        
        return keep_going, msg
    


class SignUpAction:

    @classmethod
    def run(
            cls,
            user_id: str,
            ktr_id: str,
            email: str,
            pwd_raw: str,
            pwd_check: str,
            user_name: str,
            is_developer: bool,
            p_info_agree: bool
        ):
        # 2) UNIQUE key 확인 버튼 입력 상태 확인
        mask, msg = cls.check_keys_rock()
        # mask1이 False인 경우, 에러 문구 출력 후, 중단
        if mask:
            st.error(msg)
            return

        # 1) 비밀번호, 비밀번호 확인, 사용자 이름 공란 확인
        mask, msg = cls.check_pwd_and_username_empty(
            pwd_raw=pwd_raw,
            pwd_check=pwd_check,
            user_name=user_name
        )
        if mask:
            st.error(msg)
            return



        # 3) 비밀번호, 비밀번호 확인, 사용자 이름 확인
        mask, msg = cls.check_pwd_and_username(
            pwd_raw=pwd_raw,
            pwd_check=pwd_check,
            user_name=user_name
        )
        if mask:
            st.error(msg)
            return
        
        # 4) 개인정보 수집 동의 여부 확인
        if not p_info_agree:
            st.error(LoginSignup.PERSONAL_INFO_NOT_AGREE)
            return

        # 5) DB INSERT - Table add 전 백엔드에서 한 번 확인함


    @classmethod
    def check_keys_rock(cls):

        # 순회하면서 UNIQUE key 확인 결과 반환
        duplicated_rock = {
            "계정":st.session_state[SignupKey.USER_ID],
            "사번":st.session_state[SignupKey.KTR_ID],
            "이메일":st.session_state[SignupKey.EMAIL],
        }
        for k, v in duplicated_rock.items():
            if not v:
                return True, LoginSignup.ENTER_TARGET_NOT_PASS.format(k=k)
        return False, None
    
    @classmethod
    def check_pwd_and_username_empty(
            cls,
            pwd_raw: str,
            pwd_check: str,
            user_name: str
        ) -> Tuple[bool, Optional[str]]:

        # 순회하면서 비어있는지 확인
        empty_check = {
            "비밀번호":pwd_raw,
            "비밀번호 확인":pwd_check,
            "사용자 이름":user_name
        }
        for k, v in empty_check.items():
            if not v:
                return True, LoginSignup.ENTER_TARGET_NULL.format(k=k)
        return False, None
        
    @classmethod
    def check_pwd_and_username(
            cls,
            pwd_raw: str,
            pwd_check: str,
            user_name: str
        ) -> Tuple[bool, Optional[str]]:

        # 비밀번호 인증기
        class PasswordCheck(BaseModel):
            pwd: Password
        # 사용자 이름 인증기
        class UserNameCheck(BaseModel):
            name: UserName

        # pwd_raw와 pwd_check가 불일치 하는 경우
        if pwd_raw != pwd_check:
            msg = LoginSignup.PWD_MISSMATCH
            return True, msg
        
        # 비밀번호 형식 확인
        try:
            PasswordCheck(pwd=pwd_raw)
        except:
            msg = (
                LoginSignup.ENTER_WRONG_PWD 
                + f" ({LoginSignup.PWD_PAT})"
            )
            return True, msg

        # 사용자 이름 형식 확인
        try:
            UserNameCheck(name=user_name)
        except:
            msg = (
                LoginSignup.ENTER_WRONG_USERNAME 
                + f"({LoginSignup.USER_NAME_PAT})"
            )
            return True, msg
        
        return False, None