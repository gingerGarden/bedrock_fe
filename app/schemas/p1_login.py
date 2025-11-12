"""
백엔드 서버(bedrock_web)의 Login 관련 Schema와 동일한 Pydantic 정의.

목적
----
- FE와 BE 간의 유저 정보·로그인·중복검사 등의 데이터 형식을 완전히 일치시키기 위함.
- Annotated + StringConstraints를 활용하여 각 필드의 길이, 정규식, 공백 처리 규칙을 명확히 고정.
"""
from typing import Annotated, Optional
from pydantic import EmailStr, StringConstraints, BaseModel


# ==============================
# Primitive 타입 정의 (공용 스키마)
# ==============================
# 사용자 로그인 ID
UserId = Annotated[str, StringConstraints(
    strip_whitespace=True,      # 문자열 앞뒤 공백 제거
    min_length=4, 
    max_length=20,
    pattern=r'^[A-Za-z0-9_-]+$'
)]

KTR_Id = Annotated[str, StringConstraints(
    strip_whitespace=True,      # 문자열 앞뒤 공백 제거
    min_length=8,
    max_length=8,
    pattern=r'^[1-2][0-9]+$'
)]

Password = Annotated[str, StringConstraints(
    strip_whitespace=True,      # 문자열 앞뒤 공백 제거
    min_length=12, 
    max_length=64,
    pattern=r'^[A-Za-z0-9!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]+$'
)]

UserName = Annotated[str, StringConstraints(
    strip_whitespace=True,      # 문자열 앞뒤 공백 제거
    min_length=2, 
    max_length=20,
    pattern=r"^[A-Za-z0-9\uAC00-\uD7A3_\-\(\)]+$"
)]

Email = EmailStr



# ==============================
# 로그인 요청 스키마
# ==============================
class UserLogin(BaseModel):
    """
    로그인 요청용 스키마.

    Attributes
    ----------
    user_id : UserId
        로그인 ID (4~20자, 영문/숫자/기호(_,-))
    password : Password
        비밀번호 (12~64자, 공백 불가)
    """
    user_id: UserId
    password: Password


# ==============================
# 유일성(중복 검사) 요청 스키마
# ==============================
class UniqueKeys(BaseModel):
    """
    유저 고유 키 중 하나 이상을 전달받아 중복 여부를 검사하기 위한 스키마.

    Notes
    -----
    - 세 필드(user_id, ktr_id, email)는 모두 선택적(Optional)
    - 실제 API에서는 최소 하나는 필수로 전달되어야 함 (별도 validator로 보장 가능)

    Attributes
    ----------
    user_id : Optional[UserId]
        사용자 로그인 ID
    ktr_id : Optional[KTR_Id]
        KTR 내부 사번 또는 ID
    email : Optional[Email]
        이메일 주소
    """
    user_id: Optional[UserId] = None
    ktr_id: Optional[KTR_Id] = None
    email: Optional[Email] = None
