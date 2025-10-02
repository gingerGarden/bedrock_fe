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
from typing import List, Dict

import streamlit as st
import requests

from app.constants.api_urls import ChatAPIKeys

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
    

def streaming_response(payload: Dict[str, str]):
    """
    백엔드 채팅 API에 POST 요청을 보내고, 스트리밍 응답을 순차적으로 반환합니다.

    동작:
        - stream=True로 연결을 유지하며 데이터 조각(chunk)을 순차 수신합니다.
        - 각 chunk는 SSE(Server-Sent Events) 형식이므로 SSEConverter를 사용해 텍스트만 추출합니다.
        - 추출된 텍스트를 yield하여 UI에서 실시간으로 출력할 수 있게 합니다.

    Args:
        payload (Dict[str, str]): 요청 데이터 (예: {"txt": "안녕", "model_name": "gemma:2b"})

    Yields:
        str: 모델이 생성한 텍스트 조각.
             연결 오류 발생 시 에러 메시지를 한 번 yield.
    """
    try:
        with requests.post(
            ChatAPIKeys.CHAT, 
            json=payload, 
            stream=True,
            timeout=300         # 5분 타임아웃
        ) as r:
            # HTTP 상태 코드가 200-299 범위가 아니면 예외 발생
            r.raise_for_status()
            # 응답을 라인 단위로 순회하며 SSE 형식 파싱
            for chunk in r.iter_content(chunk_size=None):
                txt = SSEConverter.sse_to_txt(chunk)
                if txt:
                    yield txt

    except requests.exceptions.RequestException as e:
        yield f"백엔드 연결 오류: {e}"