from typing import Final



class LoginAPI:

    UNIQUE_KEY_ONLY_ONE: Final[str] = "[입력오류] user_id, ktr_id, email 중 하나를 입력하십시오."
    
    PARSING_JSON_FAIL: Final[str] = "[접속 실패] 응답 JSON 파싱 실패"
    FAIL_UNKNOWN: Final[str] = "[접속 실패] 예상치 못한 응답 형식"

    VERIFY_LOGIN_SUCCESS: Final[str] = "[접속 성공] 정상적인 ID와 비밀번호 입력"


class LoginSignup:
    
    ID_NULL: Final[str] = "[입력오류] ID를 입력하지 않았습니다."
    PWD_NULL: Final[str] = "[입력오류] 비밀번호를 입력하지 않았습니다."
    ID_AND_PWD_WRONG: Final[str] = "[입력오류] ID나 비밀번호를 잘못 입력하였습니다."
    PWD_MISSMATCH: Final[str] = "[입력오류] 비밀번호가 일치하지 않습니다."

    ENTER_TOO_MUCH: Final[str] = "[입력오류] 값을 하나만 입력하십시오."
    ENTER_NULL: Final[str] = "[입력오류] 값이 입력되지 않았습니다."
    ENTER_OVER: Final[str] = "[입력오류] 범위를 벗어나는 값을 입력하였습니다."

    ENTER_TARGET_NULL: Final[str] = "[입력오류] {k}이(가) 비어있습니다."
    ENTER_TARGET_NOT_PASS: Final[str] = "[입력오류] {k} 중복 확인이 통과되지 않았습니다."

    ENTER_WRONG_PWD: Final[str] = f"[입력오류] '비밀번호' 형식이 잘못됐습니다."
    ENTER_WRONG_USERNAME: Final[str] = f"[입력오류] '사용자 이름' 형식이 잘못됐습니다."
    
    USER_ID_PAT: Final[str] = "영문/숫자/특수문자(-_) 조합 (4~20자)"
    PWD_PAT: Final[str] = "영문/숫자/특수문자(공백 제외)만 허용 (12~64자)"
    USER_NAME_PAT: Final[str] = "한글/영문/특수문자(-_) (2~20자)"

    PERSONAL_INFO_NOT_AGREE: Final[str] = "개인정보 수집 미동의 시, 회원가입이 제한됩니다."


# 유저 정지 요청에 따른 안내문
SOFT_DELETE = """
계정 사용을 정지하도록 하겠습니까?

정지 시, 관리자 요청에 의해서만 계정 재사용이 가능합니다.

정지된 계정 정보는 3년간 보관되며, 3년 이후 자동 폐기됩니다.

정말 정지하시겠습니까?
"""


# 개인정보사용 방법
PERSONAL_INFO_AGREE = """
귀하는~~~~
"""


# 첫 화면 소개글
MAIN_INTRO = """
version: KHA alpha v0.0.1

#### 1. 개요
```
사이드바에서 'Login'을 선택하여 로그인을 진행해주세요.
```
* 해당 버전은 알파 테스트으로 MVP(Minimum Viable Product)를 지향합니다.
* 로그인 후, 각 기능들을 정상적으로 사용할 수 있습니다.
    - KHA 사용을 위해선 log-in이 필요합니다
    - KHA 알파 버전은 회원가입을 지원하지 않습니다
    - 개발 단계이므로, 담당 개발자에게 계정 문의 바랍니다
---

#### 2. 주요 기능
* login : 사용자 인증 및 상태 유지 - 사용자별 멀티턴 에이전트
* chat : 백엔드 LLM 응답 연동 UI
* dashboard : 사용자 대화량 통계 및 주요 지표 시각화
* admin : 사용자 관리 및 로그 확인 (관리자 전용)
---

#### 3. 주의 사항
* 본 서비스는 알파 버전입니다
* 데이터는 테스트 목적에 한정됩니다

&nbsp;
"""