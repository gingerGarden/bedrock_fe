import streamlit as st
from app.tools.t00_common import ToolCommon



class Main:

    @classmethod
    def UI(cls):
        ToolCommon.back_button()
        st.title("이미지 다운스케일링 처리기")
        st.write("---")

