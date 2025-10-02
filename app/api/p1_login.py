from typing import Dict, Optional

from requests import Response

from app.constants.values import Role, API_TIMEOUT
from app.constants.api_urls import LoginAPIKeys
from app.constants.messages import LoginAPI

from bedrock_core.data.api import APIResponseHandler, APIResponseOutput




# login ID, 비번 인증
def verify_login(
        user_id: str, 
        password: str
    ) -> APIResponseOutput:

    # payload 생성
    payload = {
        "user_id":user_id, 
        "password":password
    }
    # API 통신
    return APIResponseHandler.run(
        url=LoginAPIKeys.VERIFY_ID,
        payload=payload,
        func_200=Status200.verify_login,
        timeout=API_TIMEOUT
    )

# UNIQUE key에 대한 중복 확인
def verify_unique_key(
        user_id: Optional[str] = None,
        ktr_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> APIResponseOutput:

    # 값이 0개 들어가거나, 1개를 초과해서 들어가는 경우를 방어
    provided = {
        k: v for k, v in (("user_id", user_id), ("ktr_id", ktr_id), ("email", email))
        if v not in (None, "")
    }
    if len(provided) != 1:
        return None, LoginAPI.UNIQUE_KEY_ONLY_ONE, None

    payload = {"user_id":user_id, "ktr_id":ktr_id, "email":email}

    # API 통신
    return APIResponseHandler.run(
        url=LoginAPIKeys.VERIFY_UNIQUE_KEY,
        payload=payload,
        func_200=Status200.verify_unique_key,
        timeout=API_TIMEOUT
    )


def add_new_user(
        user_id: str,
        ktr_id: str,
        email: str,
        pwd_raw:str,
        pwd_check:str,
        user_name: str,
        developer: bool
    ):
    payload = {
        "user_id":user_id,
        "ktr_id":ktr_id,
        "email":email,
        "pwd_raw":pwd_raw,
        "pwd_check":pwd_check,
        "user_name":user_name,
        "developer":developer
    }



class Status200:

    @classmethod
    def verify_login(cls, resp: Response) -> APIResponseOutput:
        
        # response의 json에서 dictionary 반환
        try:
            data = resp.json()
        except ValueError:
            return None, LoginAPI.PARSING_JSON_FAIL, None
        
        # 정상 출력 시 분기
        if data.get("ok") is True:
            # 권한 정보 딕셔너리 생성
            roles: Dict[str, bool] = {
                Role.DEVELOPER:data.get(Role.DEVELOPER),
                Role.ADMIN:data.get(Role.ADMIN)
            }
            return True, LoginAPI.VERIFY_LOGIN_SUCCESS, roles
        
        # ok 필드가 False거나 없음 → 예상치 못한 응답 형식
        return False, LoginAPI.FAIL_UNKNOWN, None
    
    @classmethod
    def verify_unique_key(cls, resp: Response):
        # response의 json에서 dictionary 반환
        try:
            data = resp.json()
        except ValueError:
            return None, LoginAPI.PARSING_JSON_FAIL, None

        # 정상 출력 시 분기
        if data.get("ok") is True:

            key = data.get("key")
            exists = data.get("exists")
            msg = data.get("msg")

            if key is None or exists is None or msg is None:
                return None, LoginAPI.FAIL_UNKNOWN, None
            
            return exists, msg, {"key":key}

        return None, LoginAPI.FAIL_UNKNOWN, None



