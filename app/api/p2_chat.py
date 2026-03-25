"""
백엔드 API 호출 및 응답 처리 유틸리티.

- 모델 목록 및 기본 모델명 조회:
    get_available_models(), get_default_model()
    → Streamlit 캐싱(@st.cache_data)으로 네트워크 호출 최소화.

- 채팅 스트리밍 응답 처리:
    streaming_response()
    → 백엔드의 Chat API에 요청을 보내고 SSE(Server-Sent Events) 형식의
      응답을 실시간으로 파싱하여 UI에 전달.
"""
from typing import List

import streamlit as st
import requests

from app.constants.api_urls import ChatAPIKeys
from app.constants.keys import SessionKey
from app.constants.values import FixValues
from app.constants.messages import ChatMsg
from app.core.config import CHAT_WITH_META

from bedrock_core.data.sse import SSEConverter




@st.cache_data(ttl=600) # 10분 동안 API 응답을 캐싱하여 불필요한 호출 방지
def get_available_models() -> List[str]:
    """
    백엔드에서 사용 가능한 모델 목록을 가져옵니다.

    동작:
        - ChatAPIKeys.MODEL_LIST 엔드포인트에 GET 요청을 전송합니다.
        - 응답을 10분간 캐싱하여 반복 호출 시 네트워크 부하를 줄입니다.

    예외 처리:
        - 요청 실패 시 st.error로 사용자에게 알리고, 오류 메시지가 담긴 리스트를 반환합니다.

    Returns:
        List[str]: 모델 이름 목록. 오류 발생 시 ["목록을 불러오지 못했습니다"] 반환.
    """
    try:
        response = requests.get(ChatAPIKeys.MODEL_LIST, timeout=5)
        response.raise_for_status()     # 200 OK가 아니면 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"모델 목록 로딩 실패: {e}")
        return ["목록을 불러오지 못했습니다"]


@st.cache_data(ttl=600) # 10분 동안 API 응답을 캐싱하여 불필요한 호출 방지
def get_default_model() -> str:
    """
    백엔드에서 설정된 기본 모델명을 가져옵니다.

    동작:
        - APIKey.DEFAULT_MODEL 엔드포인트에 GET 요청을 전송합니다.
        - 응답을 10분간 캐싱하여 불필요한 호출을 방지합니다.

    예외 처리:
        - 요청 실패 시 st.error로 사용자에게 알리고, 빈 문자열("")을 반환합니다.

    Returns:
        str: 기본 모델명. 오류 발생 시 "" 반환.
    """
    try:
        response = requests.get(ChatAPIKeys.DEFAULT_MODEL, timeout=5)
        response.raise_for_status()     # 200 OK가 아니면 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"디폴트 모델명 로딩 실패: {e}")
        return ""


def stop_streaming(request_id: str):
    """
    백엔드(GPU 서버)에 현재 진행 중인 스트리밍 응답 생성을 중단하도록 요청

    사용자가 '응답 생성 중단' 버튼을 눌렀을 때 호출되며, 백엔드에서 해당 request_id와
    연결된 LLM 추론 태스크를 즉시 종료시켜 GPU 자원 낭비를 방지하는 역할을 함

    Args:
        request_id (str): 중단하고자 하는 스트리밍 요청의 고유 식별자
        - make_request_id()를 통해 생성되어 payload에 포함된 값

    Note:
        - HTTP POST 요청을 통해 백엔드의 ChatAPIKeys.STOP_STREAMLING 엔드포인트에 접속
        - 네트워크 오류 등으로 요청이 실패하더라도 프론트엔드 흐름을 방해하지 않도록 예외 캡처
    """
    try:
        # 백엔드에 자연어 생성 중단 신호 전송
        requests.post(
            ChatAPIKeys.STOP_STREAMING,
            json={"request_id": request_id},
            timeout=5
        )
    except requests.exceptions.RequestException as e:
        print(f"백엔드 스트리밍 중단 API 호출 실패: {e}")


def streaming_response(payload: dict[str, str]):
    """
    실시간 채팅 스트리밍의 통합 진입점.
    - ChatStyle 클래스를 통해 설정(with_meta)에 따른 스트리밍을 실행합니다.
    - 제너레이터를 반환하여 Streamlit UI에서 실시간 출력이 가능하게 합니다.
    """
    yield from ChatStyle.run(payload=payload)


class ChatStyle:
    """
    스트리밍 응답 스타일 및 로직 제어 클래스.
    - CHAT_WITH_META 설정에 따라 일반 텍스트 모드와 메타데이터 포함 모드 전환
    - 백엔드 통신 및 데이터 파싱 로직 캡슐화
    """
    with_meta: bool = CHAT_WITH_META

    @classmethod
    def run(cls, payload: dict[str, str]):
        """
        스트리밍 실행 컨트롤러.
        - 요청 전 중단 플래그를 확인하고, 적절한 백엔드 엔드포인트를 선택하여 호출

        Args:
            payload (dict): 백엔드로 보낼 요청 데이터 (txt, model_name, request_id 등)
        """
        # 1. 중단 플래그 체크: 요청 시작 전 사용자가 '중단'을 눌렀는지 확인
        # 요청 시작 전 중단 플래그가 켜져 있다면 아예 요청을 보내지 않음 
        # (대화 중만 누를 수 있게 되어 있으나 방어를 위해 존재)
        if st.session_state.get(SessionKey.STOP_STREAM, False):
            yield ChatMsg.INTERRUPT
            return
        
        try:
            # 2. 설정에 따른 엔드포인트 결정
            # - True: 텍스트 + 마지막에 JSON 메타데이터 포함 (/web_with_meta)
            # - False: 순수 텍스트 조각만 전송 (/web)
            endpoint = ChatAPIKeys.CHAT_WITH_META if cls.with_meta else ChatAPIKeys.CHAT

            # 3. 실제 스트리밍 로직 실행 및 결과 전파
            yield from cls._internal_chat_stream(endpoint=endpoint, payload=payload)
            
        except requests.exceptions.RequestException as e:
            # 네트워크 장애 및 API 호출 실패 예외 처리
            yield f"백엔드 연결 오류: {e}"

    @classmethod
    def _internal_chat_stream(cls, endpoint: str, payload: dict[str, str]):
        """
        백엔드 통신 및 SSE 데이터 파싱을 담당하는 핵심 내부 메서드.
        - HTTP 스트림을 유지하며 데이터를 수신하고, SSE 규격에 맞춰 파싱

        Args:
            endpoint (str): 백엔드 API 주소
            payload (dict): 요청 데이터
        """
        with requests.post(
            endpoint,
            json=payload,
            stream=True,
            timeout=FixValues.CHAT_TIME_OUT
        ) as r:
            # HTTP 상태 코드 확인 : 200~299 범위가 아니면 예외 발생
            r.raise_for_status()

            # 대화 내용 생성
            # iter_content + Buffer 방식
            # SSE 메시지 수신 및 파싱을 위한 버퍼 초기화
            buffer: str = ""
            # chunk_size 단위로 데이터를 점진적으로 읽어들임
            for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):

                # 1. 루프 내부 중단 체크: 생성 중 사용자가 '중단'을 누르면 즉시 연결 종료
                if st.session_state.get(SessionKey.STOP_STREAM, False):
                    r.close()
                    return
                
                if not chunk: continue

                # 2. SSE 메시지 조립 및 파싱 로직 (Fragmented Packet 대응)
                buffer += chunk
                while "\n\n" in buffer:
                    # SSE 메시지 구분자(\n\n)를 기준으로 개별 이벤트 분리
                    message, buffer = buffer.split("\n\n", 1)
                    # SSEConverter를 통해 원본 데이터(dict 또는 str) 추출
                    contents = SSEConverter.sse_to_txt(message)

                    if not contents: continue

                    # 3. 데이터 타입별 처리 로직
                    # 메타데이터인 경우(dict)
                    if isinstance(contents, dict):
                        # [Case A] 메타데이터(Dictionary)인 경우
                        # - 백엔드가 전송한 마지막 정보(토큰 수, 소요시간 등)를 처리
                        if contents.get('done', False):
                            # TODO: 세션에 메타데이터 저장 및 DB 로깅 로직 추가 가능
                            metadata = contents.get('metadata', {})

                        # 딕셔너리 내부의 실제 텍스트 내용물(content) 추출
                        # API 로직상, 가장 마지막만 dictionary로 전달됨
                        txt = contents.get('content', "")
                    else:
                        # [Case B] 일반 스트리밍 텍스트(str)인 경우
                        txt = contents

                    # 4. 결과 누적 및 UI 전파
                    if txt:
                        # 전체 응답 내용을 세션 상태에 누적 기록 (Rerun 시 UI 복원용)
                        st.session_state[SessionKey.TEMP_RESPONSE] += txt
                        # 현재 텍스트 조각을 즉시 UI로 전달 (타이핑 효과)
                        yield txt
