from typing import Optional, List, Union
from requests import Response
from datetime import datetime

from app.constants.values import API_TIMEOUT
from app.constants.api_urls import AdminAPIKeys
from app.constants.messages import AdminMsg
from bedrock_core.data.api import APIResponseHandler, APIResponseOutput



def get_all_user_records() -> APIResponseOutput:
    # payload 생성
    payload = {"call":True}
    # API 통신
    return APIResponseHandler.run(
        url=AdminAPIKeys.GET_ALL_USERS,
        func_200=Status200.get_all_user_records,
        payload=payload,
        timeout=API_TIMEOUT
    )



class Status200:

    @classmethod
    def get_all_user_records(
            cls, resp: Response
        ) -> APIResponseOutput:
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, AdminMsg.PARSING_JSON_FAIL, None
        
        # 정상 출력 시 분기
        if data.get("ok") is True:
            records: List[str, Union[str, bool, datetime]] = data["records"]
            return True, AdminMsg.GET_RECORDS, records
        
        # ok 필드가 False거나 없음 → 예상치 못한 응답 형식
        return False, AdminMsg.FAIL_UNKNOWN, None