import uuid
import streamlit as st
from typing import Literal, Optional, Dict, Final

from app.constants.values import FixValues



def string_space_converter(value: str) -> str:
    """
    문자열 내 존재하는 공백을 언더스코어("_")로 변환한다.
    문자열이 아닌 경우는 그대로 반환한다.

    Args:
        value (str): 대상 문자열

    Returns:
        str: 공백이 언더스코어로 치환된 문자열 (문자열이 아닌 경우 그대로 반환)
    """
    if isinstance(value, str):
        # 앞뒤 공백 제거
        value = value.strip()
        # 빈 문자열이 아니라면 공백을 "_"로 치환
        if value != "":
            return value.replace(" ", "_")
        else:
            return value
    # 문자열이 아닐 경우 원본 그대로 반환
    return value


def make_request_id(
        prefix: str | None = None,
        *,
        norm_str: str = "_",
        sep: str = ".",
        prefix_base: str = "auto"
    ) -> str:
    """
    고유한 request_id를 생성한다.

    - 기본적으로 UUID4(hex)를 사용하여 충돌 가능성이 극히 낮은 ID를 생성한다.
    - prefix가 주어질 경우, 안전하게 정규화한 뒤 UUID 앞에 붙인다.
    - prefix가 없거나, 정규화 결과가 무의미한 경우(prefix가 전부 제거된 경우),
      prefix_base 값을 대신 사용한다.

    반환 형식:
    - prefix가 없는 경우      : "<uuid4hex>"
    - prefix가 있는 경우      : "<prefix_norm><sep><uuid4hex>"
    """
    # 허용할 안전 문자 집합
    # request_id는 로그, HTTP 헤더, URL, SSE 등 다양한 경로로 전달될 수 있으므로
    # 파싱 문제를 일으킬 수 있는 문자는 사전에 차단한다.
    safe_str_tuple = (".", "-", "_")
    
    # 구분자(sep)는 안전 문자만 허용
    if sep not in safe_str_tuple:
        raise ValueError(
            f"sep must be one of {safe_str_tuple}"
        )
    # 치환 문자(norm_str)는 반드시 길이 1의 안전 문자여야 함
    if len(norm_str) != 1 or norm_str not in safe_str_tuple:
        raise ValueError(
            f"norm_str must be one of {safe_str_tuple} and size must be 1"
        )
    
    # UUID4 기반의 고유 request_id 생성
    # 분산 환경에서도 충돌
    base = uuid.uuid4().hex

    # prefix가 없다면, 고유 request_id만 반환
    if not prefix:
        return base
    
    # prefix가 있다면, prefix를 sub와 합쳐서 반환
    prefix_norm = (
        # SAFE_REGEX에 해당하지 않는 문자 norm_str로 치환
        FixValues.SAFE_REGEX.sub(norm_str, prefix)  
        .strip("._-")           # 문자열 앞·뒤 의미 없는 구분자 제거
        or prefix_base
    )
    return f"{prefix_norm}{sep}{base}"
    

def btn_type_converter(target: bool, reverse: bool = False):
    """
    streamlit 버튼 타입을 결정하는 함수 (target에 따라 색 변환 목적)

    Args:
        target (bool): 기준 값 (True → primary, False → secondary)
        reverse (bool): True일 경우 target 값을 반전시켜 적용

    Returns:
        str: "primary" 또는 "secondary"

    Raises:
        TypeError: target 또는 reverse가 bool 타입이 아닐 경우 발생
    """
    # target 타입 검증 (bool만 허용)
    if not isinstance(target, bool):
        raise TypeError(f"target must be a boolean, got {type(target).__name__}")

        raise TypeError(f"target must be a boolean, got {type(target).__name__}")
    
    # reverse 타입 검증 (bool만 허용)
    if not isinstance(reverse, bool):
        raise TypeError(f"reverse must be a boolean, got {type(reverse).__name__}")

    # reverse 옵션이 활성화된 경우 target 값을 반전
    if reverse:
        target = not target

    return "primary" if target else "secondary"



class Flash:
    """
    Streamlit에서 일시적인 알림 메시지(Flash Message)를 표시하는 유틸리티 클래스.

    Flash 메시지는 세션에 저장되며, `render()`를 통해 출력된 후 
    'life' 카운트를 기반으로 제거되거나 유지된다.

    사용 예시
    --------
    >>> Flash.push("my_flash", "warning", "잘못된 입력입니다.")
    >>> Flash.render("my_flash")
    """

    # 세션 상태에 저장될 내부 키값 정의 (고정 문자열)
    _LEVEL: Final[str] = "_level"       # 메시지 레벨 (success, warning, error, info)
    _MSG: Final[str] = "_msg"           # 표시할 메시지 내용
    _LIFE: Final[str] = "_life"         # 유지될 생명주기 (렌더링 가능한 횟수)

    @classmethod
    def push(
            cls, 
            flash_key: str,
            level: Literal['success', 'warning', 'error', 'info'],
            msg: str,
            life: int = FixValues.FLASH_LIFE
        ):
        """
        새로운 Flash 메시지를 세션 상태에 저장한다.

        Args:
            flash_key (str): 메시지를 식별할 키
            level (Literal): 메시지 수준 (success, warning, error, info)
            msg (str): 사용자에게 표시할 메시지
            life (int): 해당 메시지를 몇 번까지 렌더링할 수 있는지 설정 (기본값: FLASH_LIFE)
        """
        # 세션에 Flash 추가
        st.session_state[flash_key] = {
            cls._LEVEL:level, 
            cls._MSG:msg, 
            cls._LIFE:life
        }

    @classmethod
    def render(cls, flash_key: str):
        """
        세션에서 flash_key에 해당하는 Flash 메시지를 꺼내어 화면에 표시한다.

        Notes
        -----
        - life가 0이 되면 세션에서 제거된다.
        - Streamlit의 메시지 출력 함수(getattr(st, level))를 활용한다.
        """
        # 세션에서 flash 메시지를 꺼냄 (동시에 pop하여 1회 출력 구조)
        data: Optional[Dict[str, str]] = st.session_state.pop(flash_key, None)

        # 표시할 데이터가 없으면 종료
        if not data:
            return

        # Streamlit의 레벨별 메시지 함수 (예: st.warning, st.success 등)로 출력
        getattr(st, data[cls._LEVEL])(data[cls._MSG])

        # life 자동 감소
        data[cls._LIFE] = int(data.get(cls._LIFE, 1)) - 1

        # life가 남아있으면 다시 세션에 저장하여 다음 렌더링까지 유지
        if data[cls._LIFE] > 0:
            st.session_state[flash_key] = data