from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# =========================
# 데이터 조회
# =========================
class MultiRecordsLax(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 추가 필드 무시
    ok: bool
    records: List[Dict[str, Any]]  # 내부는 dict로만 받음




# =========================
# 유저 정보 변경
# =========================
AdminBulkKeyLiteral = Literal["signup", "block", "delete"]

class AdminBulkIdxes(BaseModel):
    """
    Bulk 액션 결과에 대한 idx 집계 보고서.

    의미
    ----
    - target   : 요청이 지목한 모든 대상 idx
    - done     : 실제로 처리(상태 변경/삭제)된 idx
    - no_work  : 조건 미충족(이미 같은 상태 등)으로 스킵된 idx
    - over_work: (이론상 불가) 중복/과다 처리로 판정된 idx

    비고
    ----
    - 'over_work'는 논리적으로 0건이어야 정상이며, 값이 존재한다면 서버 로직 점검 필요.
    """
    target: List[int] = Field(
        ..., 
        description="요청으로 전달된 대상 idx 전체"
    )
    done: List[int] = Field(
        default_factory=list, 
        description="실제 DB에서 처리된 idx"
    )
    no_work: List[int] = Field(
        default_factory=list, 
        description="조건 불일치 등으로 미적용된 idx"
    )
    over_work: List[int] = Field(
        default_factory=list, 
        description="(이론상 불가) 과다 적용된 idx"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target": [1, 2, 3],
                "done": [1, 3],
                "no_work": [2],
                "over_work": []
            }
        }
    )

class AdminBulkResp(BaseModel):
    """
    Bulk 액션(signup/block/delete) 실행 결과.

    판정 규칙(권장)
    --------------
    - ok:
        - True  : 과다 적용이 없고(over_work=False), 실제 처리된 항목(done)이 1개 이상
        - False : 그 외(전부 미적용, 과다 적용 발생 등)
    - key : 수행된 액션 종류("signup" | "block" | "delete")
    - way :
        - signup: True(승인) / False(승인 해제)
        - block : True(정지) / False(정지 해제)
        - delete: 항상 True (방향 개념 없음)
    - over_work: 과다 적용 여부(정상 동작이라면 False)

    Attributes
    ----------
    ok : bool
        정상 동작 여부(정책에 맞춘 판정).
    key : AdminBulkKeyLiteral
        수행된 액션 종류.
    way : bool
        액션 방향(삭제는 True로 고정).
    over_work : bool
        과다 적용 여부(논리적으로 False가 정상).
    idx : AdminBulkIdxes
        대상/처리/미처리/과다적용 결과 집계.
    """
    ok: bool = Field(
        ..., 
        description="정상 동작 여부(과다 적용이 없고, 실제 처리된 항목이 1개 이상)"
    )
    key: AdminBulkKeyLiteral = Field(
        ..., 
        description="수행된 액션: signup | block | delete"
    )
    way: bool = Field(
        ...,
        description="수행된 액션의 방향(delete는 무조건 True)"
    )
    over_work: bool = Field(
        ..., 
        description="과다 적용 여부(논리적으로는 False가 정상)"
    )
    idx: AdminBulkIdxes = Field(
        ..., 
        description="대상/처리/미처리/과다적용 idx 리포트"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ok": True,
                "key": "signup",
                "way": True,
                "over_work": False,
                "idx": {
                    "target": [10, 11, 12],
                    "done": [10, 12],
                    "no_work": [11],
                    "over_work": []
                }
            }
        }
    )



class AdminResetPwdResp(BaseModel):
    """
    단일 사용자 비밀번호 재설정 응답.

    Attributes
    ----------
    ok : bool
        성공 여부.
    msg : Optional[str]
        결과 메시지(성공/실패 원인 설명).
    idx : Optional[int]
        비밀번호가 변경된 대상 사용자 idx (실패 시 None 가능).
    """
    ok: bool
    msg: Optional[str] = None
    idx: Optional[int] = None