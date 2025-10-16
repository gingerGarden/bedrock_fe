"""
로그인/회원가입 유틸 함수 모음.

- view_changer: 현재 화면(View) 변경 후 UI 리렌더링
- input_cleaner: 폼 입력값을 None/Boolean 등으로 정리
- SignUpUniqueKeys: 회원가입 시 unique key(user_id, ktr_id, email) 중복 검사 처리
- SignUpAction: 회원가입 버튼 클릭 시 FE 검증 → BE 호출
- EditAction: 회원 정보 수정 폼 검증/호출/세션 반영
- SoftDeleteAction: 자기 계정 정지(Soft-delete) 처리
"""
import streamlit as st

from typing import Tuple, Dict, Optional, Union
from pydantic import BaseModel, EmailStr

from app.api.p1_login import (
    verify_unique_key, add_new_user, self_block, self_update
)
from app.constants.keys import SignupKey, LoginViews, SessionKey
from app.constants.values import UserUpdateInfo
from app.constants.messages import (
    LoginSignupMsg, LoginSelfBlockMsg, LoginSelfUpdateMsg
)
from app.schema.p1_login import UniqueKeys, Password, UserName
from app.utils.session import init_session
from app.utils.utils import string_space_converter


# ==============================
# Pydantic 기반 단일 필드 검증기
# ==============================
class PasswordCheck(BaseModel):
    """비밀번호 단일 필드 형식 검증용 모델."""
    pwd: Password

# 사용자 이름 인증기
class UserNameCheck(BaseModel):
    """사용자 이름(별명) 단일 필드 형식 검증용 모델."""
    name: UserName

# Email 형식 인증기
class EmailCheck(BaseModel):
    """이메일 단일 필드 형식 검증용 모델."""
    email: EmailStr


# ==============================
# 공용 유틸
# ==============================
def view_changer(view_name: str):
    """
    로그인 뷰 상태 전환 후 즉시 rerun.

    매개변수
    --------
    view_name : str
        이동할 뷰 이름 (LoginViews.*)

    동작
    ----
    - 세션 상태(LoginViews.KEY)를 새로운 뷰로 변경
    - 곧바로 st.rerun() 호출로 UI 재렌더링
    """
    # View 변경
    st.session_state[LoginViews.KEY] = view_name
    # UI를 새로 그림
    st.rerun()


def input_cleaner(
        value: str, 
        is_boolean: bool = False
    ) -> Optional[Union[str, bool]]:
    """
    입력값 정리기.

    목적
    ----
    - 폼 입력값을 다루기 쉽게 정규화:
      * 공백/빈 문자열 → None
      * 불리언은 False를 None으로 취급(옵션)

    Parameters
    ----------
    value : str
        폼에서 받은 원본 문자열
    is_boolean : bool, default False
        True면 False 값을 None으로 변환(미입력 취급)

    Returns
    -------
    Optional[Union[str, bool]]
        정리된 값 (미입력은 None)
    """
    if is_boolean:
        return None if not value else True
    
    return None if value.strip() == "" else value



# ==============================
# 회원가입 중복 검사 유틸
# ==============================
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
        회원가입 화면 최초 진입 시, 중복 검사 결과 세션 상태 초기화(존재하지 않으면 False로 세팅).

        Notes
        -----
        - 각 필드의 '중복검사 통과 여부'를 False로 초기화하여 버튼 색상/메시지 로직이
          예측 가능하게 동작하도록 함.
        - 이미 세션에 값이 있으면 덮어쓰지 않음.
        """
        if not st.session_state.get(SignupKey.USER_ID, False):
            st.session_state[SignupKey.USER_ID] = False
        if not st.session_state.get(SignupKey.KTR_ID, False):
            st.session_state[SignupKey.KTR_ID] = False
        if not st.session_state.get(SignupKey.EMAIL, False):
            st.session_state[SignupKey.EMAIL] = False

    @classmethod
    def keys_rock_init(cls):
        """
        중복 확인 세션 상태를 완전 초기화.

        Behavior
        --------
        - 통과 여부(USER_ID/KTR_ID/EMAIL) → False
        - 메시지(USER_ID_MSG/KTR_ID_MSG/EMAIL_MSG) → None
        - 개인정보 안내 화면에서 뒤로가기 시 등, 상태를 깨끗하게 리셋할 때 사용
        """
        # 중복 확인 결과 초기화
        st.session_state[SignupKey.USER_ID] = False
        st.session_state[SignupKey.KTR_ID] = False
        st.session_state[SignupKey.EMAIL] = False
        
        st.session_state[SignupKey.USER_ID_MSG] = None
        st.session_state[SignupKey.KTR_ID_MSG] = None
        st.session_state[SignupKey.EMAIL_MSG] = None

    @classmethod
    def set_condition(
            cls, 
            bool_key: str = SignupKey.USER_ID, 
            msg_key: str = SignupKey.USER_ID_MSG
        ) -> Tuple[str, str]:
        """
        버튼의 색상(primary/secondary)과 메시지를 세션 상태에 따라 결정.

        Parameters
        ----------
        bool_key : str
            True면 primary, False면 secondary
        msg_key : str
            버튼 클릭 결과 메시지가 저장된 세션 키

        Returns
        -------
        (btn_type, msg) : Tuple[str, str]
            버튼 타입과 현재 메시지(None 가능)
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
        중복 검사 결과 메시지를 출력.

        Parameters
        ----------
        bool_key : str
            True → st.info, False → st.error
        message : Optional[str]
            출력할 메시지 (None이면 미출력)
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

        Flow
        ----
        1) 대상 키(user_id/ktr_id/email) 식별
        2) 입력값 유효성 검사(빈값/패턴 위반)
        3) BE API 호출(verify_unique_key) → exists 여부 판단
        4) 세션 상태 갱신(통과 여부/메시지)
        5) st.rerun()으로 즉시 UI 갱신

        Raises
        ------
        ValueError
            세 개 중 어느 것도 주어지지 않은 경우
        """
        # 1) 대상 세션 키 식별
        tg_key, tg_msg_key = cls._checker_action_key(user_id, ktr_id, email)

        # 2) 값 검증
        keep_going, msg = cls._checker_action_value(user_id, ktr_id, email)

        # 3) 백엔드 조회 (유효할 때만)
        if keep_going:
            duplicated, msg, _ = verify_unique_key(user_id, ktr_id, email)
        else:
            # 형식 위반 → 세션 상태 업데이트 후 즉시 rerun
            st.session_state[tg_key] = False
            st.session_state[tg_msg_key] = msg
            st.rerun()
            return
        
        # 4) 결과 반영
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
        어떤 unique key를 검사 중인지 결정하여 대응 세션 키를 반환.

        Returns
        -------
        (bool_key, msg_key) : Tuple[str, str]
            예) user_id → (SignupKey.USER_ID, SignupKey.USER_ID_MSG)
        """
        # 대상 unique key 정의
        if user_id is not None:
            return SignupKey.USER_ID, SignupKey.USER_ID_MSG
        elif ktr_id is not None:
            return SignupKey.KTR_ID, SignupKey.KTR_ID_MSG
        elif email is not None:
            return SignupKey.EMAIL, SignupKey.EMAIL_MSG
        else:
            raise ValueError(LoginSignupMsg.ENTER_TOO_MUCH)
        
    @classmethod
    def _checker_action_value(
            cls, 
            user_id: Optional[str],
            ktr_id: Optional[str],
            email: Optional[str]
        ) -> Tuple[bool, str]:
        """
        입력값 검증 로직.

        Checks
        ------
        - 빈 문자열 여부
        - Pydantic `UniqueKeys`로 패턴 검증

        Returns
        -------
        (keep_going, msg) : Tuple[bool, str]
            keep_going=True → BE 호출 가능
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
            msg = LoginSignupMsg.ENTER_NULL
            return keep_going, msg

        # 2) 형식 검증 (Pydantic 모델)
        try:
            UniqueKeys(user_id=user_id, ktr_id=ktr_id, email=email)
            keep_going = True
            msg = None
        except:
            keep_going = False
            msg = LoginSignupMsg.ENTER_OVER
            # user_id 오류 시 추가 안내 메시지 포함
            if key == "user_id":
                msg = f"{msg} ({LoginSignupMsg.USER_ID_PAT})"
        
        return keep_going, msg
    


# ==============================
# 회원가입 실행 유틸
# ==============================
class SignUpAction:
    """회원가입 버튼 클릭 시 FE 검증 → BE 호출을 담당."""
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
        """
        회원가입 처리 파이프라인.

        Flow
        ----
        0) user_name 공백 정규화
        1) UNIQUE 키 중복검사 통과 여부 확인(세션 rock 확인)
        2) 필수 입력값 공란 검사
        3) 비밀번호/사용자명 형식 검증
        4) 개인정보 수집 동의 확인
        5) BE(add_new_user) 호출 → 결과 메시지 출력 및 rock 초기화
        """
        # 0) user_name 변환기(공백·양끝 정리 등)
        user_name = string_space_converter(value=user_name)

        # 1) UNIQUE key rock 확인
        mask, msg = cls.check_keys_rock()
        if mask:
            st.error(msg)
            return

        # 2) 공란 검사
        mask, msg = cls.check_pwd_and_username_empty(
            pwd_raw=pwd_raw,
            pwd_check=pwd_check,
            user_name=user_name
        )
        if mask:
            st.error(msg)
            return

        # 3) 형식/일치 검증
        mask, msg = cls.check_pwd_and_username(
            pwd_raw=pwd_raw,
            pwd_check=pwd_check,
            user_name=user_name
        )
        if mask:
            st.error(msg)
            return
        
        # 4) 개인정보 수집 동의
        if not p_info_agree:
            st.error(LoginSignupMsg.PERSONAL_INFO_NOT_AGREE)
            return
        
        # 5) 회원가입 BE 호출
        mask, msg, _ = add_new_user(
            user_id=user_id,
            ktr_id=ktr_id,
            email=email,
            pwd_raw=pwd_raw,
            pwd_check=pwd_check,
            user_name=user_name,
            developer=is_developer,
            signup= False if is_developer else None
        )
        if mask:
            # 개발자 계정은 별도 메시지
            if is_developer:
                st.info(LoginSignupMsg.SUCCESS_ADD_DEV)
            else:
                st.info(msg)
            # 확인 키 초기화
            SignUpUniqueKeys.keys_rock_init()
        else:
            st.error(msg)


    @classmethod
    def check_keys_rock(cls) -> Tuple[bool, Optional[str]]:
        """
        세션에 저장된 중복검사 통과 여부를 점검.

        Returns
        -------
        (is_error, message)
            통과하지 않은 키가 있으면 True와 메시지 반환
        """
        # 순회하면서 UNIQUE key 확인 결과 반환
        duplicated_rock = {
            "계정":st.session_state[SignupKey.USER_ID],
            "사번":st.session_state[SignupKey.KTR_ID],
            "이메일":st.session_state[SignupKey.EMAIL],
        }
        for k, v in duplicated_rock.items():
            if not v:
                return True, LoginSignupMsg.ENTER_TARGET_NOT_PASS.format(k=k)
        return False, None
    
    @classmethod
    def check_pwd_and_username_empty(
            cls,
            pwd_raw: str,
            pwd_check: str,
            user_name: str
        ) -> Tuple[bool, Optional[str]]:
        """
        비밀번호/비번확인/사용자이름의 공란 여부를 확인.
        """
        # 순회하면서 비어있는지 확인
        empty_check = {
            "비밀번호":pwd_raw,
            "비밀번호 확인":pwd_check,
            "사용자 이름":user_name
        }
        for k, v in empty_check.items():
            if not v:
                return True, LoginSignupMsg.ENTER_TARGET_NULL.format(k=k)
        return False, None
        
    @classmethod
    def check_pwd_and_username(
            cls,
            pwd_raw: str,
            pwd_check: str,
            user_name: str
        ) -> Tuple[bool, Optional[str]]:
        """
        비밀번호 일치/형식 및 사용자명 형식을 검증.

        Returns
        -------
        (is_error, message)
        """
        # pwd_raw와 pwd_check가 불일치 하는 경우
        if pwd_raw != pwd_check:
            return True, LoginSignupMsg.PWD_MISSMATCH
        
        # 비밀번호 형식 확인
        try:
            PasswordCheck(pwd=pwd_raw)
        except:
            return True, (
                LoginSignupMsg.ENTER_WRONG_PWD 
                + f" ({LoginSignupMsg.PWD_PAT})"
            )
        # 사용자 이름 형식 확인
        try:
            UserNameCheck(name=user_name)
        except:
            return True, (
                LoginSignupMsg.ENTER_WRONG_USERNAME 
                + f"({LoginSignupMsg.USER_NAME_PAT})"
            )
        return False, None



# ==============================
# 회원 정보 수정 유틸
# ==============================
class EditAction:
    """회원 정보 수정(본인) 처리: 검증 → BE 호출 → 세션 반영."""
    @classmethod
    def run(
            cls, 
            pwd_current: str, 
            user_name: Optional[str],
            developer: Optional[bool],
            email: Optional[str],
            pwd_new_raw: Optional[str],
            pwd_new_check: Optional[str]
        ):
        """
        회원 정보 수정 파이프라인.

        Flow
        ----
        1) 현재 비밀번호 형식 검증(미입력/잘못된 형식 방지)
        2) 값 검증(모두 미입력, 이메일 형식·중복락, 비밀번호 규칙 등)
        3) BE(self_update) 호출
        4) 성공 시 메시지 출력/세션 반영/락 초기화
        """
        # 1) 현재 비밀번호 인증
        mask, msg = cls._pwd_current_check(pwd_current)
        if mask:
            st.error(msg)
            return

        # 2) 입력값 확인
        mask, msg = cls._value_check(
            user_name=user_name,
            developer=developer,
            email=email,
            pwd_current=pwd_current,
            pwd_new_raw=pwd_new_raw,
            pwd_new_check=pwd_new_check
        )
        if mask:
            st.error(msg)
            return

        # 3) 백엔드 API 전달
        mask, msg, result = self_update(
            user_id=st.session_state[SessionKey.ID],
            pwd_current=pwd_current,
            user_name=user_name,
            developer=developer,
            email=email,
            pwd_new_raw=pwd_new_raw,
            pwd_new_check=pwd_new_check
        )

        # 4) 출력/세션 반영
        if mask:
            st.info(msg)
            cls._session_update(result=result)      # 세션 표기값 갱신
            SignUpUniqueKeys.keys_rock_init()       # 이메일 락 등 초기화
        else:
            st.error(msg)

    @classmethod
    def _pwd_current_check(
            cls, 
            pwd_current: str
        ) -> Tuple[bool, Optional[str]]:
        """
        현재 비밀번호 입력/형식 검증.
        """
        # 현재 비밀번호 미입력
        if pwd_current == "" or pwd_current is None:
            return True, LoginSelfUpdateMsg.CURRENT_PWD_NULL
        # 비밀번호 인증기
        try:
            PasswordCheck(pwd=pwd_current)
            return False, None
        except:
            return True, LoginSelfUpdateMsg.CURRENT_PWD_WRONG

    @classmethod    
    def _value_check(
            cls,
            user_name: Optional[str],
            developer: Optional[bool],
            email: Optional[str],
            pwd_current:str,
            pwd_new_raw: Optional[str],
            pwd_new_check: Optional[str]
        ) -> Tuple[bool, Optional[str]]:
        """
        수정 요청 값들의 유효성 검증(모두 빈값, 이메일, 비밀번호 규칙).
        """
        # 0) user_name 정규화
        user_name = string_space_converter(value=user_name)

        # 1) 모두 미입력 여부
        mask, msg = cls._check_all_null(
            user_name=user_name,
            developer=developer,
            email=email,
            pwd_new_raw=pwd_new_raw,
            pwd_new_check=pwd_new_check
        )
        if mask:
            return mask, msg
        
        # 2) 이메일 형식/락 확인 (입력 시에만)
        mask, msg = cls._check_email(email=email)
        if mask:
            return mask, msg

        # 3) 비밀번호 규칙/중복 확인
        mask, msg = cls._check_password(
            pwd_current=pwd_current,
            pwd_new_raw=pwd_new_raw,
            pwd_new_check=pwd_new_check
        )
        if mask:
            return mask, msg
        
        return False, None
                
    @classmethod
    def _check_all_null(
            cls,
            user_name: Optional[str],
            developer: Optional[bool],
            email: Optional[str],
            pwd_new_raw: Optional[str],
            pwd_new_check: Optional[str]
        ) -> Tuple[bool, Optional[str]]:
        """
        모든 수정 대상이 None인지 체크.
        """
        # 조회할 대상의 List
        targets = [
            user_name, developer, email,
            pwd_new_raw, pwd_new_check
        ]
        if all(t is None for t in targets):
            return True, LoginSelfUpdateMsg.ALL_NULL
        return False, None

    @classmethod
    def _check_email(
            cls, 
            email: Optional[str]
        ) -> Tuple[bool, Optional[str]]:
        """
        이메일이 입력된 경우에만 형식·중복락을 검사.
        """
        if email is not None:

            # 현재 이메일과 동일 여부
            if email == st.session_state[SessionKey.EMAIL]:
                return True, LoginSelfUpdateMsg.EMAIL_DUPLICATE
            
            # 형식 검사 + 락 확인
            try:
                EmailCheck(email=email)
                return cls._check_email_rock()      # Email rock 확인
            except:
                return True, LoginSelfUpdateMsg.EMAIL_CHECK_NEED
        return False, None

    @classmethod
    def _check_email_rock(
            cls
        ) -> Tuple[bool, Optional[str]]:
        """
        '이메일 중복 확인' 버튼을 통과했는지 세션 락 확인.
        """
        if st.session_state[SignupKey.EMAIL]:
            return False, None
        return True, LoginSelfUpdateMsg.EMAIL_CHECK_NEED 
    
    @classmethod
    def _check_password(
            cls, 
            pwd_current: str,
            pwd_new_raw: Optional[str],
            pwd_new_check: Optional[str]
        ) -> Tuple[bool, Optional[str]]:
        """
        비밀번호 변경 요청 시 규칙/중복/일치 검증.
        """
        if pwd_new_raw is not None:

            # pwd_new_raw와 pwd_new_check가 불일치 하는 경우
            if pwd_new_raw != pwd_new_check:
                return True, LoginSignupMsg.PWD_MISSMATCH
            
            # 새로운 비밀번호가 기존 비밀번호와 일치하는 경우
            if pwd_current == pwd_new_raw:
                return True, LoginSelfUpdateMsg.PWD_DUPLOCATED
            
            # 비밀번호 형식 확인
            try:
                PasswordCheck(pwd=pwd_new_raw)
                return False, None
            except:
                return True, (
                    LoginSignupMsg.ENTER_WRONG_PWD 
                    + f" ({LoginSignupMsg.PWD_PAT})"
                )
        return False, None    
        
    @classmethod
    def _session_update(
            cls, 
            result: Dict[str, Optional[str]]
        ):
        """
        백엔드가 반환한 변경 필드를 세션에 반영.
        """
        # user_name Session 반영
        if result[UserUpdateInfo.USER_NAME] is not None:
            st.session_state[SessionKey.USER_NAME] =\
                result[UserUpdateInfo.USER_NAME]
            
        # email Session 반영
        if result[UserUpdateInfo.EMAIL] is not None:
            st.session_state[SessionKey.EMAIL] =\
                result[UserUpdateInfo.EMAIL]



# ==============================
# 계정 정지(Soft-delete) 유틸
# ==============================
class SoftDeleteAction:
    """자기 계정 정지 플로우(입력 검증 → BE 호출 → 세션 초기화)."""
    @classmethod
    def run(cls, password: str):
        """
        계정 정지 실행.

        Flow
        ----
        1) 비밀번호 입력/형식 검증
        2) BE(self_block) 호출
        3) 성공 시 안내 후 세션 초기화
        """
        # 입력 비밀번호 형식 확인
        mask, msg = cls._pwd_checker(password=password)
        if mask:
            st.error(msg)
            return
        
        # 입력 비밀번호 일치 확인 - 백엔드 통신
        mask, msg, _ = self_block(
            user_id=st.session_state[SessionKey.ID], 
            password=password
        )

        # 결과 출력 및 세션 초기화
        if mask:
            st.info(msg)
            init_session(force=True)
        else:
            st.error(msg)

    @classmethod
    def _pwd_checker(
            cls, 
            password: str
        ) -> Tuple[bool, str]:
        """
        정지 전 비밀번호 입력/형식 검증.
        """
        # 비밀번호 미입력
        if password is None or password == "":
            return True, LoginSelfBlockMsg.PWD_NULL
        
        try:
            PasswordCheck(pwd=password)
            return False, None
        except:
            # 잘못된 비밀번호 입력 - 형식 오류 - 백엔드와 동일 오류 반환
            return True, LoginSelfBlockMsg.PWD_WRONG