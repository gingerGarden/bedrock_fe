import streamlit as st
from .utils import ToolUtils
from .config import View, Titles, Buttons


class Common:

    @staticmethod
    def back_to_main():
        """t01의 메인 화면으로 view 전환"""
        if st.button(Buttons.BACK_TO_MAIN, type="primary"):
            ToolUtils.set_view(View.MAIN)
            st.rerun()



class EXPSetup:

    def UI():
        # 뒤로가기 버튼
        Common.back_to_main()

        st.title(Titles.EXP_SETUP)
        


class ColumnsSetup:

    def UI():

        # 뒤로가기 버튼
        Common.back_to_main()

        st.title(Titles.COLUMN_SETUP)
