"""
KHA-Frontend 메인 진입점(Entrypoint)

이 모듈은 Streamlit 기반 프론트엔드 애플리케이션의 시작점입니다.
- 전역 UI 설정(페이지 제목, 아이콘, 레이아웃) 초기화
- 메인 페이지(첫 화면) 구성
- 모든 페이지에서 공유할 세션 상태 및 모델 정보 초기 로드

실행:
    $ streamlit run main.py
"""

import streamlit as st

from app.utils.session import init_session
from app.routes.common import basic_ui, InitModelInfo
from app.constants.messages import MAIN_INTRO



# ---------------------------------------------------------
# 전역 UI 설정
# ---------------------------------------------------------
# 페이지 제목, 아이콘, 레이아웃 등 앱 전역 설정을 적용합니다.
basic_ui()



# ---------------------------------------------------------
# 메인 페이지 UI
# ---------------------------------------------------------
st.title("KHA에 오신 것을 환영합니다!")
st.markdown("## (KHA: KTR Healthcare Assistant)")
st.markdown("---")
st.info(MAIN_INTRO)        # 서비스 소개 텍스트



# ---------------------------------------------------------
# 전역 상태 초기화
# ---------------------------------------------------------
# 모든 페이지에서 공통으로 사용할 세션 정보 및 모델 정보를 초기 로드합니다.
init_session()          # 로그인 상태, 대화 기록 등 사용자 세션 초기화
InitModelInfo.run()     # 백엔드에서 모델 목록 및 기본 모델명 불러오기