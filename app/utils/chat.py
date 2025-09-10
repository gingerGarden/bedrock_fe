"""
채팅 페이지의 백엔드 연동 유틸리티.

- Response: 사용자 입력을 백엔드 API에 전송하고, 스트리밍 응답을 UI에 실시간 표시.
"""
from typing import Dict

import streamlit as st

from app.core.api import streaming_response
from app.schema.keys import (
    SessionKey, StreamLitChatKey
)
from kha.schema.keys import ChatRoles




class Response:
    """
    채팅 응답 처리 클래스.
    - st.write_stream과 연동해 LLM 답변을 실시간 출력.
    """
    @classmethod
    def main(cls):
        """응답 생성부터 표시, 세션 저장까지 전체 처리."""
        # 1. 백엔드 API로 전송할 요청 데이터(payload)를 생성합니다.
        txt_dict = cls._convert_to_txt_dict()
        payload = cls._make_payload(txt_dict)

        # 2. `st.chat_message`를 사용해 AI의 답변 영역을 UI에 준비합니다.
        #   스트리밍 응답을 실시간으로 UI에 표시
        with st.chat_message(ChatRoles.ASSISTANT):
                
            # 3. `st.write_stream`을 통해 스트리밍 응답을 실시간으로 렌더링합니다.
            #    `streaming_response` 제너레이터가 yield하는 텍스트 조각을 받아옵니다.
            full_response = st.write_stream(
                streaming_response(payload=payload)
            )
            
        # 4. 전체 응답이 완료되면, 대화 기록(message) 세션에 저장합니다.
        cls._save_response(full_response)

        # 5. 스트리밍 상태를 False로 변경하고, `st.rerun`으로 UI를 즉시 갱신하여
        #    사용자 입력창을 다시 활성화합니다.
        st.session_state[SessionKey.STREAMING] = False
        st.rerun()

    @classmethod
    def _convert_to_txt_dict(cls) -> Dict[str, str]:
        """
        세션의 마지막 사용자 메시지를 txt_dict 형태로 변환.

        현재는 마지막 메시지만 전송.
        TODO: 멀티턴 대화를 위해 전체 대화 기록 전송으로 확장 필요.

        Returns:
            Dict[str, str]: Chat API 요청 형식의 txt_dict.
        """
        # 세션의 대화 기록에서 가장 마지막 메시지(사용자 입력)를 가져옵니다.
        current_msg = st.session_state[SessionKey.MESSAGE][-1]

        # TODO: 현재는 마지막 메시지만 전달. 추후 전체 대화 목록을 전달하도록 확장 가능.
        return {
            current_msg[StreamLitChatKey.ROLE]:\
            current_msg[StreamLitChatKey.CONTENT]
            }

    @classmethod
    def _make_payload(
            cls,
            txt_dict: Dict[str, str]
        ) -> Dict[str, str]:
        """
        Chat API 요청 payload 생성.

        Args:
            prompt (Dict[str, str]): 대화형 메시지
            ex) {
                    'system':'너는 훌륭한 인공지능 비서야',
                    'user':'안녕! 반가워'
                }
        Returns:
            Dict[str, str]: 백엔드 웹서버 chat 라우터 내 API들의 페이로드
            - api_chat, web_chat, web_chat_with_metadata
        """
        return {
            "txt":None,
            "txt_dict":txt_dict,
            "model_name":st.session_state[SessionKey.MODEL]
        }

    @classmethod
    def _save_response(cls, full_response: str):
        """
        LLM 응답을 세션 대화 기록에 저장.

        Args:
            full_response (str): st.write_stream이 반환한 전체 응답 문자열.
        """
        st.session_state[SessionKey.MESSAGE].append(
            {
                "role": ChatRoles.ASSISTANT, 
                "content": full_response
            }
        )