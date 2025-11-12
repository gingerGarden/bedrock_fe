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