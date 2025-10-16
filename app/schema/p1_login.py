"""
백엔드 서버(bedrock_web)의 Login 관련 Schema의 값과 동일
"""
from typing import Annotated, Optional
from pydantic import EmailStr, StringConstraints, BaseModel



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
    pattern=r"^[A-Za-z0-9\uAC00-\uD7A3_-]+$"
)]

Email = EmailStr



class UserLogin(BaseModel):
    user_id: UserId
    password: Password



class UniqueKeys(BaseModel):
    user_id: Optional[UserId] = None
    ktr_id: Optional[KTR_Id] = None
    email: Optional[Email] = None
