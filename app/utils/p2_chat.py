"""
채팅 페이지의 백엔드 연동 유틸리티.

- Response: 사용자 입력을 백엔드 API에 전송하고, 스트리밍 응답을 UI에 실시간 표시.
"""
import streamlit as st

from app.api.p2_chat import streaming_response
from app.constants.keys import SessionKey, StreamLitChatKey

from kha.schema.keys import ChatRoles




class Response:
    """
    채팅 응답 처리 클래스.
    - st.write_stream과 연동해 LLM 답변을 실시간 출력.
    """
    @classmethod
    def main(cls):
        """응답 생성부터 표시, 세션 저장까지 전체 처리."""

        # 1. payload 생성
        txt_dict = cls._convert_to_txt_dict()
        payload = cls._make_payload(txt_dict)

        # 2. 스트리밍 표시
        with st.chat_message(ChatRoles.ASSISTANT):
                
            # 스트리밍 응답 실시간 렌더링 - streaming_response 제너레이터가 yield하는 텍스트 조각
            full_response = st.write_stream(streaming_response(payload=payload))

        # 3. full_response가 있다면 저장
        if full_response is not None and str(full_response).strip() != "":
            cls._save_response(full_response)

        # 4. 상태 정리
        st.session_state[SessionKey.STREAMING] = False      # 사용자 입력창 재활성화
        st.session_state[SessionKey.STOP_STREAM] = False
        st.rerun()

    @classmethod
    def _convert_to_txt_dict(cls) -> dict[str, str]:
        """
        세션의 마지막 사용자 메시지를 txt_dict 형태로 변환.

        현재는 마지막 메시지만 전송.
        TODO: 멀티턴 대화를 위해 전체 대화 기록 전송으로 확장 필요.

        Returns:
            dict[str, str]: Chat API 요청 형식의 txt_dict.
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
            txt_dict: dict[str, str]
        ) -> dict[str, str]:
        """
        Chat API 요청 payload 생성.

        Args:
            prompt (dict[str, str]): 대화형 메시지
            ex) {
                    'system':'너는 훌륭한 인공지능 비서야',
                    'user':'안녕! 반가워'
                }
        Returns:
            dict[str, str]: 백엔드 웹서버 chat 라우터 내 API들의 페이로드
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
