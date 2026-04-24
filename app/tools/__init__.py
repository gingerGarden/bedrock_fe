from typing import Callable
import streamlit as st

from app.constants.keys import ToolsViews

# 메인 UI
from app.tools.t01.main import Main as T01Main
from app.tools.t02_image_downscaler import Main as T02Main

# session key 초기화 메서드
from app.tools.t01.utils import ToolUtils as t01utils


# page_key와 해당 도구의 UI 함수를 매핑
TOOL_ROUTER: dict[str, Callable] = {
    "tool_a00001": T01Main.UI,
    # "tool_a00002": T02Main.UI,
}

# session 초기화 함수 매핑
TOOL_INIT: dict[str, Callable] = {
    "tool_a00001": t01utils.init_session,
    # "tool_a00002": t01utils.init_session,
}

class ToolSessionManager:
    @staticmethod
    def clear_all_tool_sessions():
        """모든 등록된 도구의 세션을 강제로 초기화(기본값으로 리셋)"""
        # tool 페이지 뷰어 초기화
        st.session_state[ToolsViews.KEY] = ToolsViews.MAIN

        # tool 세부 도구 초기화
        for _, init_fn in TOOL_INIT.items():
            try:
                # 각 도구의 init_session(force=True)를 호출
                init_fn(force=True)
            except TypeError:
                # force 인자가 없는 함수 대응
                init_fn()


