import streamlit as st
import pandas as pd

from typing import Final
from streamlit.runtime.uploaded_file_manager import UploadedFile

from .config import (
    SessionKeys, View, Check, WidgetKeys, 
    EQ_KEYS, DATA_KEY, DATA_TO_WIDGET
)
from bedrock_tools.tools.t01_clinic_table.data import Rawdata



class Data:

    file_dict = {
        "e01-혈액분석기":SessionKeys.DATA1_CBC,
        "e02-생화학분석기":SessionKeys.DATA2_CHEM,
        "e03-응고분석기":SessionKeys.DATA3_COAG,
        "e04-요분석기":SessionKeys.DATA4_URIN,
    }
    @classmethod
    def get(cls, file: UploadedFile, data_key: DATA_KEY):
        
        # 파일이 없는 경우 처리
        if file is None:
            st.session_state[SessionKeys.LAST_LOADED_FILE_ID] = None
            return
        
        # 해당 위젯이 에러 상태라면 중복 실행 방지
        # 다이얼로그 확인을 누르기 전까지는 다시 검사하지 않음
        target_widget = DATA_TO_WIDGET.get(data_key)
        if st.session_state.get(SessionKeys.ERROR_TARGET_WIDGET) == target_widget:
            return

        # 파일이 변경되었을 때만 로드하도록 세션 체크
        file_id = f"file_{data_key}_{file.name}_{file.size}"
        if st.session_state.get(SessionKeys.LAST_LOADED_FILE_ID) == file_id:
            return
        
        # 데이터 조회
        data, msg = Rawdata.get(data_input=file, data_key=data_key)
        if data is None:
            st.session_state[SessionKeys.ERROR_MESSAGE] = msg
            # 에러에 해당하는 위젯 키 세션에 저장
            st.session_state[SessionKeys.ERROR_TARGET_WIDGET] = \
                DATA_TO_WIDGET.get(data_key)
            st.rerun()
        else:
            # data 저장
            st.session_state[cls.file_dict[data_key]] = data
            # 혈액분석기인 경우, 실험 설정이 가능하게 정의
            if data_key == "e01-혈액분석기":
                st.session_state[Check.EXP_SETUP] = True
            # 세션 내 file_id 갱신
            st.session_state[SessionKeys.LAST_LOADED_FILE_ID] = file_id



class ToolUtils:

    keys_init_values: Final[dict[str, View | None]] = {
        # 데이터 초기화
        SessionKeys.DATA1_CBC: None,
        SessionKeys.DATA2_CHEM: None,
        SessionKeys.DATA3_COAG: None,
        SessionKeys.DATA4_URIN: None,

        # 위젯 상태 초기화
        SessionKeys.ERROR_MESSAGE: None,
        SessionKeys.ERROR_TARGET_WIDGET: None,
        SessionKeys.WIDGET_RESET_DICT: {
            WidgetKeys.U1: 0,
            WidgetKeys.U2: 0,
            WidgetKeys.U3: 0,
            WidgetKeys.U4: 0,
        },

        # View
        SessionKeys.CURRENT_VIEW: View.MAIN,
        SessionKeys.CONFIG_EXP_SET: None,
        SessionKeys.CONFIG_COLUMN_SET: None,

        # Check
        Check.EXP_SETUP: False,
        Check.COLUMN_SETUP: False,

        # 기타 정보
        SessionKeys.LAST_LOADED_FILE_ID: None
    }

    data_keys: Final[dict[EQ_KEYS, str]] = {
        "e1":SessionKeys.DATA1_CBC,
        "e2":SessionKeys.DATA2_CHEM,
        "e3":SessionKeys.DATA3_COAG,
        "e4":SessionKeys.DATA4_URIN
    }

    @classmethod
    def init_session(cls, force: bool =False):
        # 모든 세션 키에 대하여 초기값이 없으면 먼저 설정
        for k, v in cls.keys_init_values.items():
            if k not in st.session_state:
                if isinstance(v, dict):
                    st.session_state[k] = v.copy()
                else:
                    st.session_state[k] = v

        if force:
            # 강제 초기화 시 카운트를 올려서 모든 위젯의 Key를 변형시킴
            reset_dict = st.session_state.get(SessionKeys.WIDGET_RESET_DICT, {})
            for key in reset_dict:
                reset_dict[key] += 1
            st.session_state[SessionKeys.WIDGET_RESET_DICT] = reset_dict

            # 나머지 데이터들을 초기값으로 덮어씀
            for k, v in cls.keys_init_values.items():
                if k == SessionKeys.WIDGET_RESET_DICT: continue
                st.session_state[k] = v

    @classmethod
    def get_data(cls, eq_key: EQ_KEYS):
        target_data_key = cls.data_keys.get(eq_key)
        data = st.session_state.get(target_data_key)
        if data is None:
            return None
        else:
            return data
        
    @classmethod
    def get_wkey(cls, key: str) -> str :
        """
        위젯의 고유 Key 생성
        """
        # WIDGET_RESET_DICT의 개별 카운터 리셋
        reset_dict = st.session_state.get(SessionKeys.WIDGET_RESET_DICT, {})
        count = reset_dict.get(key, 0)
        return f"{key}_{count}"
    
    @classmethod
    def reset_widget(cls, widget_key: str):
        """특정 위젯의 카운터만 올려서 해당 파일 업로더만 초기화"""
        reset_dict = st.session_state.get(SessionKeys.WIDGET_RESET_DICT, {})
        if widget_key in reset_dict:
            reset_dict[widget_key] += 1

        st.session_state[SessionKeys.WIDGET_RESET_DICT] = reset_dict
        # 에러 상태 초기화
        st.session_state[SessionKeys.ERROR_MESSAGE] = None
        st.session_state[SessionKeys.ERROR_TARGET_WIDGET] = None

    @staticmethod
    def set_view(view_value: View):
        st.session_state[SessionKeys.CURRENT_VIEW] = view_value