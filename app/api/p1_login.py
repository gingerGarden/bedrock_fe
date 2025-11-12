"""
Login API 연동 모듈.

이 모듈은 Streamlit(FE) → FastAPI(BE) 간 로그인/회원가입 관련 API 호출을 담당한다.
공통 전송/에러 처리 흐름은 APIResponseHandler.run()에 위임하고,
정상 응답(2xx)에 대한 파싱/검증은 Status200의 각 메서드로 캡슐화한다.

구성
----
- verify_login()       : 로그인 검증 API 호출
- verify_unique_key()  : 회원가입 시 중복 검사 API 호출
- add_new_user()       : 신규 사용자 생성 API 호출
- self_block()         : 본인 계정 정지(Soft-delete) API 호출
- self_update()        : 본인 계정 정보 변경 API 호출
- Status200            : 2xx 응답 파서 모음(엔드포인트별 성공 페이로드 검증)
"""
from typing import Dict, Optional, Union
from requests import Response

from app.constants.values import FixValues
from app.constants.api_urls import LoginAPIKeys
from app.constants.keys import SessionKey, UserInfo, UserUpdateInfo
from app.constants.messages import (
    LoginMsg, LoginSignupMsg, LoginSelfBlockMsg, LoginSelfUpdateMsg
)

from bedrock_core.data.api import APIResponseHandler, APIResponseOutput




# ============================================================
# 로그인 ID/비밀번호 검증
# ============================================================
def verify_login(
        user_id: str, 
        password: str
    ) -> APIResponseOutput:
    """
    로그인 자격 증명(아이디/비밀번호) 검증 API 호출.

    동작 흐름
    ---------
    1) payload = {user_id, password}
    2) LoginAPIKeys.VERIFY_ID 로 POST
    3) 2xx 수신 → Status200.verify_login()으로 파싱

    Returns
    -------
    APIResponseOutput
        (성공 여부[bool|None], 메시지[str|None], 사용자 정보 딕트[dict|None])
        - 성공 시: (True, <성공 메시지>, {"user_name":..., "ktr_id":..., "email":..., "developer":..., "admin":...})
        - 실패 시: (False|None, <에러 메시지>, None)
    """
    # payload 생성
    payload = {
        "user_id":user_id, 
        "password":password
    }
    # API 통신
    return APIResponseHandler.run(
        url=LoginAPIKeys.VERIFY_ID,
        func_200=Status200.verify_login,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )

# ============================================================
# 유니크 키(user_id / ktr_id / email) 중복 확인
# ============================================================
def verify_unique_key(
        user_id: Optional[str] = None,
        ktr_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> APIResponseOutput:
    """
    회원가입 시 유니크 키(user_id/ktr_id/email) 중복 여부 확인 API 호출.

    제약
    ----
    - 3개 중 정확히 1개만 값이 있어야 함(None/빈문자열("")은 무시).
    - 위반 시: (None, LoginSignupMsg.UNIQUE_KEY_ONLY_ONE, None) 반환.

    Returns
    -------
    APIResponseOutput
        (중복 여부[bool|None], 메시지[str|None], {"key": <검사대상>} 또는 None)
        - 예: (False, "[중복 확인] 사용 가능한 ID입니다.", {"key": "user_id"})
    """
    # 값이 0개 들어가거나, 1개를 초과해서 들어가는 경우를 방어
    provided = {
        k: v for k, v in (("user_id", user_id), ("ktr_id", ktr_id), ("email", email))
        if v not in (None, "")
    }
    if len(provided) != 1:
        return None, LoginSignupMsg.UNIQUE_KEY_ONLY_ONE, None

    payload = {"user_id":user_id, "ktr_id":ktr_id, "email":email}

    # API 통신
    return APIResponseHandler.run(
        url=LoginAPIKeys.VERIFY_UNIQUE_KEY,
        func_200=Status200.verify_unique_key,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )

# ============================================================
# 신규 사용자 추가
# ============================================================
def add_new_user(
        user_id: str,
        ktr_id: str,
        email: str,
        pwd_raw:str,
        pwd_check:str,
        user_name: str,
        developer: bool,
        signup: Optional[bool] = None
    ):
    """
    신규 계정 생성 API 호출.

    동작 흐름
    ---------
    1. UsersAdd 스키마와 동일한 payload 생성
    2. LoginAPIKeys.ADD_USER 엔드포인트로 POST 요청
    3. 응답 201 Created → Status200.add_new_user()로 파싱

    매개변수
    --------
    user_id : str        신규 사용자 ID
    ktr_id : str         사번 (UNIQUE)
    email : str          이메일 주소
    pwd_raw : str        비밀번호 원문
    pwd_check : str      비밀번호 확인용 입력
    user_name : str      사용자 이름
    developer : bool     개발자 여부
    signup : Optional[bool]
        True → 즉시 승인 / False → 대기 / None → 서버 설정에 따름

    반환값
    ------
    APIResponseOutput
        (성공 여부[bool|None], 메시지[str|None], {"idx": <신규 PK>} 또는 None)
    """
    payload = {
        "user_id":user_id,
        "ktr_id":ktr_id,
        "email":email,
        "pwd_raw":pwd_raw,
        "pwd_check":pwd_check,
        "user_name":user_name,
        "developer":developer,
        "admin":False,
        "signup":signup
    }
    return APIResponseHandler.run(
        url=LoginAPIKeys.ADD_USER,
        func_200=Status200.add_new_user,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )


# ============================================================
# 유저 스스로 계정 정지
# ============================================================
def self_block(
        user_id: str,
        password: str
    ) -> APIResponseOutput:
    """
    유저 본인이 자신의 계정을 정지(Soft-delete)하는 API 호출.

    동작 흐름
    ---------
    1) payload = {user_id, password}
    2) LoginAPIKeys.SELF_BLOCK 로 POST
    3) 2xx 수신 → Status200.self_block()으로 파싱

    Returns
    -------
    APIResponseOutput
        (성공 여부[bool|None], 메시지[str|None], {"idx": <정지된 PK>} 또는 None)
    """
    # payload 생성
    payload = {
        "user_id":user_id, 
        "password":password
    }
    # API 통신
    return APIResponseHandler.run(
        url=LoginAPIKeys.SELF_BLOCK,
        func_200=Status200.self_block,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )


# ============================================================
# 유저 스스로 계정 정보 변경
# ============================================================
def self_update(
        user_id: str,
        pwd_current: str,
        *,
        user_name: Optional[str]=None,
        developer: Optional[bool]=None,
        email: Optional[str]=None,
        pwd_new_raw: Optional[str]=None,
        pwd_new_check: Optional[str]=None
    ) -> APIResponseOutput:
    """
    유저 본인 계정 정보 변경 API 호출.

    설명
    ----
    - 서버는 UsersUpdate 스키마에 따라 검증/적용.
    - 비밀번호 변경은 (pwd_current, pwd_new_raw, pwd_new_check) 셋트가 모두 유효해야 함.
    - 이름/이메일/개발자 신청/비밀번호 변경/자기 계정 정지(deleted_at_key)는 서버 규칙에 따름.

    Returns
    -------
    APIResponseOutput
        (성공 여부[bool|None], 메시지[str|None], {"user_name":..., "email":...} 또는 None)
    """
    # payload 생성
    payload = {
        "user_id": user_id,
            "payload": {
                "user_name": user_name,
                "developer": developer,
                "email": email,
                "pwd_current": pwd_current,
                "pwd_new_raw": pwd_new_raw,
                "pwd_new_check": pwd_new_check
        }
    }
    # API 통신
    return APIResponseHandler.run(
        url=LoginAPIKeys.SELF_UPDATE,
        func_200=Status200.self_update,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )


# ============================================================
# 정상 응답(2xx) 처리 클래스
# ============================================================
class Status200:
    """
    2xx 정상 응답을 엔드포인트별로 해석/검증하는 헬퍼.

    규칙
    ----
    - 각 메서드는 requests.Response → (ok, msg, data) 튜플을 반환
    - JSON 파싱 실패 시: (None, <파싱 실패 메시지>, None)
    - 필수 키 누락/형식 불일치 시: (None|False, <예상치 못한 응답 형식>, None)
    """
    @staticmethod
    def verify_login(resp: Response) -> APIResponseOutput:
        """
        로그인 검증 2xx 응답 파서.

        성공 시
        -------
        (True, LoginMsg.VERIFY_LOGIN_SUCCESS,
            {
                "user_name": <str>,
                "ktr_id": <str>,
                "email": <str>,
                "developer": <bool>,
                "admin": <bool>
            })

        실패 시
        -------
        (False|None, <에러 메시지>, None)
        """
        # response의 json에서 dictionary 반환
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, LoginMsg.PARSING_JSON_FAIL, None
        
        # 정상 출력 시 분기
        if data.get("ok") is True:
            # 권한 정보 딕셔너리 생성
            user_info: Dict[str, Union[str, bool]] = {
                UserInfo.USER_NAME:data[UserInfo.USER_NAME],
                UserInfo.KTR_ID:data[UserInfo.KTR_ID],
                UserInfo.EMAIL:data[UserInfo.EMAIL],
                UserInfo.DEVELOPER:data[UserInfo.DEVELOPER], 
                UserInfo.ADMIN:data[UserInfo.ADMIN]
            }
            return True, LoginMsg.VERIFY_LOGIN_SUCCESS, user_info
        
        # ok 필드가 False거나 없음 → 예상치 못한 응답 형식
        return False, LoginMsg.FAIL_UNKNOWN, None
    
    @staticmethod
    def verify_unique_key(resp: Response) -> APIResponseOutput:
        """
        유니크 키 중복 검사 2xx 응답 파서.

        성공 시
        -------
        (exists: bool, msg: str, {"key": <"user_id"|"ktr_id"|"email">})

        실패 시
        -------
        (None, LoginSignupMsg.FAIL_UNKNOWN, None)
        """
        # response의 json에서 dictionary 반환
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, LoginSignupMsg.PARSING_JSON_FAIL, None

        # 정상 출력 시 분기
        if data.get("ok") is True:

            key = data.get("key")
            exists = data.get("exists")
            msg = data.get("msg")

            if key is None or exists is None or msg is None:
                return None, LoginSignupMsg.FAIL_UNKNOWN, None
            
            return exists, msg, {"key":key}

        return None, LoginSignupMsg.FAIL_UNKNOWN, None

    @staticmethod
    def add_new_user(resp: Response) -> APIResponseOutput:
        """
        신규 사용자 생성 2xx 응답 파서.

        성공 시
        -------
        (True, LoginSignupMsg.SUCCESS_ADD, {SessionKey.USER_IDX:<int>})    # idx 반환 가능하나, 별도 사용처가 없어서 하지 않음

        실패 시
        -------
        (False|None, <에러 메시지>, None)
        """
        # response의 json에서 dictionary 반환
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, LoginSignupMsg.PARSING_JSON_FAIL, None
        
        # 정상 출력시 분기
        if data.get("ok") is True:

            idx = data.get("idx")

            if not isinstance(idx, int):
                return None, LoginSignupMsg.FAIL_UNKNOWN, None
            
            return True, LoginSignupMsg.SUCCESS_ADD, {SessionKey.USER_IDX:idx}
        
        return False, LoginSignupMsg.FAIL_UNKNOWN, None
    
    @staticmethod
    def self_block(resp: Response) -> APIResponseOutput:
        """
        본인 계정 정지 2xx 응답 파서.

        성공 시
        -------
        (True, LoginSelfBlockMsg.SUCCESS, {SessionKey.USER_IDX:<int>})

        실패 시
        -------
        (False|None, <에러 메시지>, None)
        """
        # response의 json에서 dictionary 반환
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, LoginSelfBlockMsg.PARSING_JSON_FAIL, None
        
        # 정상 출력 시 분기
        if data.get("ok") is True:
            idx: int = data.get("idx")
            return True, LoginSelfBlockMsg.SUCCESS, {SessionKey.USER_IDX:idx}
        
        # ok 필드가 False거나 없음 → 예상치 못한 응답 형식
        return False, LoginSelfBlockMsg.FAIL_UNKNOWN, None
    
    @staticmethod
    def self_update(resp: Response) -> APIResponseOutput:
        """
        본인 계정 정보 변경 2xx 응답 파서.

        성공 시
        -------
        (True, LoginSelfUpdateMsg.SUCCESS,
            {
                "user_name": <str|None>,  # 요청에서 변경했다면 존재
                "email": <str|None>       # 요청에서 변경했다면 존재
            })

        실패 시
        -------
        (False|None, <에러 메시지>, None)
        """
        # response의 json에서 dictionary 반환
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, LoginSelfUpdateMsg.PARSING_JSON_FAIL, None
        
        # 정상 출력 시 분기
        if data.get("ok") is True:

            user_info: Dict[str, Optional[str]] = {
                UserUpdateInfo.USER_NAME:data[UserUpdateInfo.USER_NAME],
                UserUpdateInfo.EMAIL:data[UserUpdateInfo.EMAIL]
            }
            return True, LoginSelfUpdateMsg.SUCCESS, user_info
        
        # ok 필드가 False거나 없음 → 예상치 못한 응답 형식
        return False, LoginSelfUpdateMsg.FAIL_UNKNOWN, None