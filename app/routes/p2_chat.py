"""
채팅 페이지(`pages/2_chat.py`) UI 및 로직 정의.

- Chat: 페이지 전체 UI(사이드바 + 메인 채팅창) 구성
- SideBar: 모델 선택, 대화 초기화 등 채팅 설정 UI
- TxtBar: 대화 기록 표시, 사용자 입력 처리
"""
import streamlit as st

from app.constants.keys import SessionKey
from app.routes.common import InitModelInfo
from app.utils.p2_chat import Response

from kha.schema.keys import ChatRoles



class Chat:
    """채팅 페이지 전체 UI 구성 클래스."""
    @classmethod
    def UI(cls):
        """사이드바와 메인 채팅창 렌더링."""
        SideBar.main()
        TxtBar.main()



class TxtBar:
    """메인 채팅 영역(대화 기록, 입력창) 관리."""

    # 사용자 입력창에 표시될 기본 메시지(placeholder)
    DEFAULT_PROMPT ="무엇을 도와드릴까요?"

    @classmethod
    def main(cls):
        """채팅 영역 UI 실행 흐름."""
        # 1. 현재까지의 대화 기록을 화면에 표시합니다.
        cls.show_session_messages()

        # 2. 현재 LLM이 응답을 생성(스트리밍)하는 중인지 확인합니다.
        if st.session_state.get(SessionKey.STREAMING, False):
            # 3a. 스트리밍 중이라면: 사용자 입력을 막고, `Response` 클래스를 통해
            #     백엔드 응답을 받아 화면에 실시간으로 표시합니다.
            Response.main()
        else:
            # 3b. 스트리밍 중이 아니라면: 사용자 입력을 받을 준비를 합니다.
            cls.user_input()

    @classmethod
    def show_session_messages(cls):
        """세션에 저장된 모든 대화(user, assistant)를 순회하며 화면에 렌더링합니다."""
        for msg in st.session_state[SessionKey.MESSAGE]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    @classmethod
    def user_input(cls):
        """
        사용자로부터 새로운 질문을 입력받는 `st.chat_input` 위젯을 생성하고,
        입력 시 처리 로직을 담당합니다.
        """
        if raw_content := st.chat_input(
            cls.DEFAULT_PROMPT,
            # 현재 대화가 생성중이면 채팅 입력이 되지 않는다
            disabled=st.session_state.get(SessionKey.STREAMING, False)
        ):
            # 세션에 사용자 메시지 저장
            st.session_state[SessionKey.MESSAGE].append(
                {"role": ChatRoles.USER, "content": raw_content}
            )
            # 화면에 표시
            with st.chat_message(ChatRoles.USER):
                st.markdown(raw_content)

            # 스트리밍 상태로 전환하고 즉시 UI 갱신
            st.session_state[SessionKey.STREAMING] = True
            st.rerun()

        

class SideBar:
    """채팅 페이지 사이드바 UI 관리."""
    
    @classmethod
    def main(cls):
        """사이드바 요소 렌더링."""
        with st.sidebar:
            st.info("지능형 ChatBot : KHA")
            # --------- 버튼 추가 ---------
            # 모델명 드롭박스
            cls.models_dropbox()
            # 대화 내용 초기화
            cls.clear()

    @classmethod
    def models_dropbox(cls):
        """LLM 모델 선택 드롭다운."""

        # selectbox 표시    
        selected = st.selectbox(
            "추론 모델 선택",
            st.session_state[SessionKey.MODEL_LIST],
            index=st.session_state[SessionKey.MODEL_IDX],
            # 현재 대화가 생성중이면 채팅 입력이 되지 않는다
            disabled=st.session_state[SessionKey.STREAMING]
        )
        # 모델 선택
        if selected != st.session_state[SessionKey.MODEL]:
            st.session_state[SessionKey.MODEL] = selected
            # MODEL_IDX 변경
            InitModelInfo.set_model_idx()
            
    @classmethod
    def clear(cls):
        """대화 내용 초기화 버튼."""
        if st.button(
            "대화 내용 초기화",
            use_container_width=True, 
            type="primary",
            # 현재 대화가 생성중이면 채팅 입력이 되지 않는다
            disabled=st.session_state[SessionKey.STREAMING]
        ):
            st.session_state[SessionKey.MESSAGE] = []
            st.rerun()

