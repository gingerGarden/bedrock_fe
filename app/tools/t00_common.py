import streamlit as st
import pandas as pd
from app.constants.keys import ToolsViews


class ToolCommon:
    """
    도구(Tools) 상세 화면에서 공통적으로 사용되는 UI 컴포넌트 모음.
    """

    @classmethod
    def back_button(cls):
        """도구 목록 화면으로 돌아가는 버튼"""
        if st.button("⬅️ 도구 목록으로 돌아가기", type="primary"):
            from app.tools import ToolSessionManager
            # 퇴장 시 모든 도구 세션 강제 초기화
            ToolSessionManager.clear_all_tool_sessions()
            # 뒤로 가기
            st.session_state[ToolsViews.KEY] = ToolsViews.MAIN
            st.rerun()

    @classmethod
    def dummy_ui(cls, page_key: str, tool_info: pd.Series):
        """
        아직 구현되지 않은 도구를 위한 더미 UI.
        이곳에서 '개발 예정'임을 알리고, 기존 정보를 보여줍니다.
        """
        st.title(f"🛠️ {tool_info['도구명']}")
        st.info(f"이 도구(**{tool_info['도구명']}**, Key: {page_key})는 현재 **개발 준비 중**입니다.")
        
        st.markdown("---")
        st.markdown("### 📋 도구 상세 정보")
        st.write(f"**설명:** {tool_info['설명']}")
        st.write(f"**태그:** {', '.join(tool_info['Tag'])}")
        st.write(f"**버전:** {tool_info['버전']}")
        
        st.markdown("---")
        st.warning("곧 새로운 기능으로 찾아뵙겠습니다!")
