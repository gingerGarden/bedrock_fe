from typing import Optional, List, Dict, Union
from requests import Response

from app.constants.values import FixValues
from app.constants.api_urls import AdminAPIKeys
from app.constants.messages import AdminMsg
from app.schemas.p9_admin import (
    AdminBulkResp, MultiRecordsLax, AdminResetPwdResp
)
from bedrock_core.data.api import APIResponseHandler, APIResponseOutput



# ==========================================================
# Admin API Client (FE → BE 통신)
# ----------------------------------------------------------
# - 관리자 기능 관련 API 호출 집합
# - 각 함수는 APIResponseHandler.run()을 통해 호출/응답 처리
# - 반환형: APIResponseOutput = Tuple[Optional[bool], str, Optional[Any]]
#   · ok   : True(성공) | False(실패) | None(파싱 불가/예외)
#   · msg  : 사용자/로그용 메시지(AdminMsg 등)
#   · data : 정상 시 도메인 데이터(레코드/리포트 등), 실패 시 None
# - 모든 함수는 네트워크/HTTP 예외를 내부에서 표준화하여 (ok=None, msg=..., data=None)로 변환
# ==========================================================

def get_all_user_records() -> APIResponseOutput:
    """
    모든 사용자 정보를 조회한다.

    Description
    -----------
    - FE(프론트엔드)에서 관리자 페이지의 전체 사용자 목록을 요구할 때 사용.
    - Soft-deleted(정지) 계정도 포함하여 반환한다.

    Returns
    -------
    APIResponseOutput
        (ok, msg, records)
        - ok      : True | False | None
        - msg     : AdminMsg.GET_RECORDS 또는 오류 메시지
        - records : List[Dict[str, Any]] | None

    Notes
    -----
    - HTTP 200 수신 시 `Status200.get_all_user_records()`로 JSON → Pydantic 검증.
    - 타임아웃은 `API_TIMEOUT` 상수 사용.
    """
    # payload 생성
    payload = {"call":True}
    # API 통신
    return APIResponseHandler.run(
        url=AdminAPIKeys.GET_ALL_USERS,
        func_200=Status200.get_all_user_records,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )

def modify_bulk_signup(
        idxes: List[Union[str, int]],
        way: bool = True
    ) -> APIResponseOutput:
    """
    여러 사용자의 **승인/승인 해제** 상태를 일괄 변경한다.

    Parameters
    ----------
    idxes : list[int | str]
        조작 대상 사용자 idx 리스트(정수 또는 정수 문자열).
    way : bool, default True
        True → 승인, False → 승인 해제.

    Returns
    -------
    APIResponseOutput
        (ok, msg, idx_dict)
        - idx_dict: {'target': [...], 'done': [...], 'no_work': [...], 'over_work': [...]}

    Notes
    -----
    - `idxes`가 비어있으면 네트워크 호출 없이 즉시 (None, AdminMsg.NO_IDX_ENTER, None) 반환.
    - HTTP 200 수신 시 `Status200.bulk_action()`로 표준화.
    """
    # idxes가 비어있는지 방어
    if not idxes:
        return None, AdminMsg.NO_IDX_ENTER, None

    # payload 생성
    payload = {
        "call":True,
        "idxes":idxes,
        "way":way
    }
    # API 통신
    return APIResponseHandler.run(
        url=AdminAPIKeys.BULK_SIGNUP,
        func_200=Status200.bulk_action,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )

def modify_bulk_block(
        idxes: List[Union[str, int]],
        way: bool = True
    ) -> APIResponseOutput:
    """
    여러 사용자의 **정지/복원(soft delete 복원)** 상태를 일괄 변경한다.

    Parameters
    ----------
    idxes : list[int | str]
        조작 대상 사용자 idx 리스트.
    way : bool, default True
        True → 정지(deleted_at=now), False → 복원(deleted_at=NULL).

    Returns
    -------
    APIResponseOutput
        (ok, msg, idx_dict)

    Notes
    -----
    - `idxes`가 비어있으면 네트워크 호출 없이 즉시 (None, AdminMsg.NO_IDX_ENTER, None) 반환.
    - HTTP 200 수신 시 `Status200.bulk_action()`로 표준화.
    """
    # idxes가 비어있는지 방어
    if not idxes:
        return None, AdminMsg.NO_IDX_ENTER, None

    # payload 생성
    payload = {
        "call":True,
        "idxes":idxes,
        "way":way
    }
    # API 통신
    return APIResponseHandler.run(
        url=AdminAPIKeys.BULK_BLOCK,
        func_200=Status200.bulk_action,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )

def modify_bulk_delete(
        idxes: List[Union[str, int]],
    ) -> APIResponseOutput:
    """
    여러 사용자를 **하드 삭제**(DB에서 완전 삭제)한다.

    Parameters
    ----------
    idxes : list[int | str]
        삭제 대상 사용자 idx 리스트.

    Returns
    -------
    APIResponseOutput
        (ok, msg, idx_dict)

    Notes
    -----
    - `idxes`가 비어있으면 네트워크 호출 없이 즉시 (None, AdminMsg.NO_IDX_ENTER, None) 반환.
    - HTTP 200 수신 시 `Status200.bulk_action()`로 표준화.
    """
    # idxes가 비어있는지 방어
    if not idxes:
        return None, AdminMsg.NO_IDX_ENTER, None

    # payload 생성
    payload = {
        "call":True,
        "idxes":idxes
    }
    # API 통신
    return APIResponseHandler.run(
        url=AdminAPIKeys.BULK_DELETE,
        func_200=Status200.bulk_action,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )


def modify_single_password(
        idx: Union[int, str],
        new_pwd: str
    ) -> APIResponseOutput:
    """
    단일 사용자의 비밀번호를 강제 초기화한다(관리자 권한).

    Parameters
    ----------
    idx : int | str
        대상 사용자 idx(1 이상의 정수 또는 정수 문자열).
    new_pwd : str
        새 비밀번호(서버의 Pydantic Password 정책에 부합해야 함).

    Returns
    -------
    APIResponseOutput
        (ok, msg, changed_idx)
        - ok          : True/False/None
        - msg         : 상태/오류 메시지
        - changed_idx : 실제 비밀번호가 변경된 사용자 idx | None

    Notes
    -----
    - idx/new_pwd가 비어있으면 사전 방어로 호출하지 않음.
    - HTTP 200 수신 시 `Status200.modify_single_password()`로 파싱.
    """
    # idx가 비어있는지 방어
    if not idx:
        return None, AdminMsg.NO_IDX_ENTER, None
    
    # new_pwd가 비어있는지 방어
    if not new_pwd:
        return None, AdminMsg.NOT_ENTER_PWD, None
    
    # payload 생성
    payload = {
        "call":True,
        "idx":idx,
        "new_pwd":new_pwd
    }
    # API 통신
    return APIResponseHandler.run(
        url=AdminAPIKeys.SINGLE_RESET_PWD,
        func_200=Status200.modify_single_password,
        payload=payload,
        timeout=FixValues.API_TIMEOUT
    )



# ==========================================================
# HTTP 200 응답 처리 전용 클래스
# ==========================================================
class Status200:
    """
    200 OK 응답을 JSON 파싱 → Pydantic 검증 → (ok, msg, data) 표준 출력으로
    변환하는 핸들러 모음.

    Output Contract
    ---------------
    - 모든 핸들러는 (ok, msg, data) 튜플을 반환한다.
    - 파싱 실패/예상치 못한 스키마 → (None, AdminMsg.PARSING_JSON_FAIL | FAIL_UNKNOWN, None)
    """

    # ------------------------------------------------------
    # 1) 전체 사용자 조회 응답 처리
    # ------------------------------------------------------
    @staticmethod
    def get_all_user_records(resp: Response) -> APIResponseOutput:
        """
        Users Table 전체 조회의 200 응답을 파싱/검증한다.

        Steps
        -----
        1) resp.json() 파싱
        2) `MultiRecordsLax`로 검증
        3) ok=True면 (True, AdminMsg.GET_RECORDS, records) 반환

        Returns
        -------
        APIResponseOutput
            (ok, msg, records)
        """
        # JSON 파싱
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, AdminMsg.PARSING_JSON_FAIL, None
        
        # 공통 스키마로 검증 및 파싱
        try:
            parsed = MultiRecordsLax.model_validate(data)
        except Exception:
            return None, AdminMsg.FAIL_UNKNOWN, None
        
        # 정상 출력시 분기
        if parsed.ok:
            records_list: List[dict] = parsed.records
            return True, AdminMsg.GET_RECORDS, records_list
        
        # ok 필드가 False거나 없음 → 예상치 못한 응답 형식
        return False, AdminMsg.FAIL_UNKNOWN, None
    
    # ------------------------------------------------------
    # 2) Bulk Action 응답 처리 (승인/정지/삭제 공용)
    # ------------------------------------------------------
    @staticmethod
    def bulk_action(resp: Response) -> APIResponseOutput:
        """
        Bulk Action(signup/block/delete) 200 응답을 파싱/검증한다.

        Output
        ------
        (ok, msg, idx_dict)
          idx_dict = {
            'target': [...],
            'done': [...],
            'no_work': [...],
            'over_work': [...]
          }

        Messaging
        ---------
        - ok=True  → AdminMsg.BULK_SUCCESS
        - ok=False → AdminMsg.BULK_FAIL
        """
        # JSON 파싱
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, AdminMsg.PARSING_JSON_FAIL, None
        
        # 공통 스키마로 검증 및 파싱
        try:
            parsed = AdminBulkResp.model_validate(data)
        except Exception:
            return None, AdminMsg.FAIL_UNKNOWN, None
        
        # 메시지 구성 + dict 변환
        idx_dict: Dict[str, List[int]] = parsed.idx.model_dump()

        if parsed.ok:
            msg = AdminMsg.BULK_SUCCESS.format(
                key=parsed.key,
                way=parsed.way,
                target=parsed.idx.target,
                done=parsed.idx.done,
                no_work=parsed.idx.no_work
            )
            return True, msg, idx_dict
        
        # 실패/부분 실패: 과다 적용/미적용 설명
        msg = AdminMsg.BULK_FAIL.format(
            key=parsed.key,
            way=parsed.way,
            target=parsed.idx.target,
            over_work=parsed.idx.over_work
        )
        return False, msg, idx_dict
    
    # ------------------------------------------------------
    # 3) 단일 비밀번호 초기화 응답 처리
    # ------------------------------------------------------
    @staticmethod
    def modify_single_password(resp: Response) -> APIResponseOutput:
        """
        단일 비밀번호 초기화 200 응답을 파싱/검증한다.

        Returns
        -------
        APIResponseOutput
            (ok, msg, idx)

        Notes
        -----
        - 서버의 응답 스키마 `AdminResetPwdResp`를 그대로 신뢰하여 반환한다.
        """
        # JSON 파싱
        try:
            data: Optional[dict] = resp.json()
        except ValueError:
            return None, AdminMsg.PARSING_JSON_FAIL, None
        
        # Pydantic 스키마로 검증 및 파싱
        try:
            parsed = AdminResetPwdResp.model_validate(data)
        except Exception:
            return None, AdminMsg.FAIL_UNKNOWN, None
        
        # response의 ok, msg, idx 그대로 사용
        return parsed.ok, parsed.msg, parsed.idx