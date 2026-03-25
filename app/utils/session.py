"""
Streamlit 세션 상태(`st.session_state`) 관리 유틸리티.

[개요]
- 사용자 상태(로그인, 권한), 페이지 정보, 채팅 스트리밍 상태 등을 중앙 집중식으로 관리.
- 페이지 전환 시 발생하는 리소스 정리(훅) 및 초기화 로직을 담당.

[주요 설계 패턴]
1. 콜백 훅(Callback Hook): 페이지 이탈 시 특정 작업을 수행하도록 훅 등록 (_LEAVE_HOOKS).
2. 역추적(Reverse Lookup): 현재 페이지 키(str)로부터 페이지 번호(Enum)를 찾아 정확한 상태 제어.
3. 관심사의 분리: 세션 기본값(defaults.py)과 API 로직을 분리하여 유지보수성 확보.
"""
import streamlit as st

from app.constants.keys import SessionKey, PageNum, PageKey
from app.constants.defaults import DEFAULT_SESSION
from app.api.p2_chat import get_available_models, get_default_model



class SessControl:
    """
    Streamlit session_state의 핵심 상태 및 생명주기를 관리하는 클래스.

    [역할]
    - 세션 초기값 설정 및 초기화 트리거.
    - 현재 활성화된 페이지 상태 추적 및 페이지 전환 감지.
    - 페이지 이탈(Leave) 시점에 필요한 후처리 로직(예: 스트리밍 중단) 실행.
    """

    # ---------------------------------------------------------
    # 생명주기 훅(Lifecycle Hooks) 설정
    # ---------------------------------------------------------
    # 페이지를 떠날 때(Leave) 실행할 콜백 함수 매핑
    # Key: PageNum(Enum) / Value: 실행할 함수(Callable)
    _LEAVE_HOOKS = {
        PageNum.KHA_CHAT: lambda: SessControl._chat_helper_stop_streaming()
    }

    @classmethod
    def init(cls, force: bool = False) -> None:
        """
        세션 상태 초기화 진입점.

        - LOGGED_IN 키가 없거나 force=True일 때 초기화 수행.
        - 불필요한 초기화를 방지하여 성능을 최적화하고 사용자 상태를 유지함.

        Args:
            force (bool): True일 경우 현재 상태를 무시하고 강제 리셋 (로그아웃 등에서 사용).
        """
        # 현재 세션 내 login을 위한 키가 존재하는지 여부
        mask = SessionKey.LOGGED_IN not in st.session_state

        if force or mask:
            cls._init_action()

    @classmethod
    def _init_action(cls) -> None:
        """
        세션 기본값 실제 설정.

        - app/constants/defaults.py에 정의된 상수 딕셔너리를 사용하여 초기 상태를 구축.
        """
        for key, value in DEFAULT_SESSION.items():
            st.session_state[key] = value

    @classmethod
    def init_model_info(cls) -> None:
        """
        LLM 모델 관련 세션 정보(목록, 기본값) 초기화.

        - 외부 API 호출이 포함되므로 성능을 위해 필요한 시점에 호출하는 것을 권장.
        """
        InitModelInfo.run()

    @classmethod
    def set_page_info(cls, page_num: PageNum) -> None:
        """
        현재 활성화된 페이지 정보를 갱신하고 페이지 전환 훅을 실행.

        [동작 흐름]
        1. 입력받은 page_num의 유효성 검사.
        2. _check_page_changed를 통해 '이전 페이지 번호'와 '변경 여부' 파악.
        3. 세션의 CURRENT_PAGE 값을 새로운 페이지 키로 업데이트.
        4. 페이지가 실제로 변경되었다면, 이전 페이지에 등록된 _LEAVE_HOOKS 실행.

        Args:
            page_num (PageNum): 이동할 대상 페이지의 Enum 값.
        """
        # 잘못된 page_num가 입력되는 것을 방어
        if page_num not in PageKey.P_KEY_DICT:
            raise ValueError(f"정의되지 않은 page_num 입니다: {page_num}")
        
        # 페이지 변경 정보 및 이전 페이지 번호(old_page_num) 획득
        changed, old_page_num, new_page = cls._check_page_changed(page_num=page_num)
        
        # 새로운 페이지 정보로 세션 업데이트
        st.session_state[PageKey.CURRENT_PAGE] = new_page

        # 페이지가 변경된 경우, 이전 페이지를 떠날 때의 로직(Hook) 수행
        # 이전 페이지 기준 메서드 적용
        if changed and old_page_num is not None:
            if leave_fn := cls._LEAVE_HOOKS.get(old_page_num, None):
                leave_fn()

    @classmethod
    def _check_page_changed(cls, page_num: PageNum) -> tuple[bool, PageNum, str]:
        """
        현재 세션 정보와 비교하여 페이지 변경 여부와 이전 페이지 번호를 식별.

        [패턴]
        - 역추적(Reverse Lookup): 문자열 키로부터 Enum(PageNum)을 찾아내어 정확한 훅 실행을 보장.

        Returns:
            tuple: (변경여부(bool), 이전 페이지 번호(PageNum), 신규 페이지 키(str))
        """
        # 세션에 저장된 현재 페이지 키(str) 획득
        old_page: str = st.session_state[PageKey.CURRENT_PAGE]
        
        # 기존 페이지 키를 통해 PageNum(Enum) 역추적 (찾지 못하면 None)
        old_page_num = next((k for k, v in PageKey.P_KEY_DICT.items() if v == old_page), None)
        
        # 이동할 신규 페이지 키 생성
        new_page: str = PageKey.P_KEY_DICT[page_num]
        
        # 페이지 변경 여부 판단 (초기 로딩 시점인 old_page_key=None인 경우는 무시)
        changed = old_page is not None and old_page != new_page

        return changed, old_page_num, new_page

    @classmethod
    def _chat_helper_stop_streaming(cls) -> None:
        """
        채팅 페이지 이탈 시 실행되는 헬퍼 메서드.

        - 현재 LLM 응답이 생성 중이라면 중단 플래그를 설정하고 백엔드 API를 호출함.
        - GPU 자원 회수 및 프론트엔드 상태 무결성을 유지하는 목적.
        """
        # 현재 스트리밍 상태 및 중단 명령 중복 여부 확인
        streaming_flag = st.session_state.get(SessionKey.STREAMING, False)
        stop_streaming_flag = st.session_state.get(SessionKey.STOP_STREAM, False)

        # 스트리밍 중이며 아직 중단 신호를 보내지 않은 경우에만 실행
        if streaming_flag and not stop_streaming_flag:
            
            # 1. 중단 플래그 설정 (Response.main에서 사후 처리를 위해 사용)
            st.session_state[SessionKey.STOP_STREAM] = True
            
            # 2. 스트리밍 상태 즉시 종료 (다른 페이지 UI 보호)
            st.session_state[SessionKey.STREAMING] = False
            
            # 3. 백엔드(GPU 서버)에 실제 중단 요청 전송
            request_id = st.session_state.get(SessionKey.CHAT_REQUEST_ID)
            if request_id:
                # 순환 참조 방지를 위해 로컬 임포트 수행
                from app.api.p2_chat import stop_streaming
                stop_streaming(request_id=request_id)



class InitModelInfo:
    """
    모델 정보 초기화 관리 클래스.

    [역할]
    - 외부 API를 통해 모델 관련 정보를 session_state에 로드

    [초기화 대상]
    - 모델 목록
    - 기본 모델명
    - 기본 모델 인덱스

    [특징]
    - 이미 값이 존재하는 경우 중복 호출을 방지
    """
    @classmethod
    def run(cls) -> None:
        """모델 정보 초기화 전체 실행."""
        # 모델 목록 로드
        cls.model_list_in_session()
        # 디폴트 모델명 로드
        cls.default_model_in_session()
        # 디폴트 모델명 index 로드
        cls.default_model_idx_in_session()

    @classmethod
    def model_list_in_session(cls) -> None:
        """
        모델 목록을 session_state에 저장.

        - MODEL_LIST 키가 없을 경우에만 API 호출 수행
        """
        # 모델 목록이 없는 경우에만 불러온다
        if SessionKey.MODEL_LIST not in st.session_state:
            st.session_state[SessionKey.MODEL_LIST] = get_available_models()

    @classmethod
    def default_model_in_session(cls) -> None:
        """
        기본 모델명을 session_state에 저장.

        - MODEL 키가 없을 경우에만 API 호출 수행
        """
        # default 모델 이름이 없는 경우에만 불러온다
        if SessionKey.MODEL not in st.session_state:
            st.session_state[
                SessionKey.MODEL
            ] = get_default_model()

    @classmethod
    def default_model_idx_in_session(cls) -> None:
        """
        기본 모델의 인덱스를 session_state에 저장.

        - st.selectbox의 index 인자에 사용
        """
        if SessionKey.MODEL_IDX not in st.session_state:
            # dafault 모델 이름 index 로드
            cls.set_model_idx()

    @classmethod
    def set_model_idx(cls) -> None:
        """
        기본 모델명에 해당하는 인덱스를 계산하여 session_state에 저장.

        [예외 처리]
        - 기본 모델명이 모델 목록에 없을 경우:
            → index를 0으로 설정
            → 모델명을 목록의 첫 번째 값으로 보정
        """
        model_list: list[str] = st.session_state[SessionKey.MODEL_LIST]
        model_name: str = st.session_state[SessionKey.MODEL]

        try:
            st.session_state[SessionKey.MODEL_IDX] = model_list.index(model_name)
        except ValueError:
            st.session_state[SessionKey.MODEL_IDX] = 0
            if model_list:
                st.session_state[SessionKey.MODEL] = model_list[0]
