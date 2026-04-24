from typing import Final, Literal



# 해당 tool의 고유 key
TOOL_KEY: Final[str] = "t01"


# 장비 정보
EQUIPMENTS = {
    "e1":{"key":"e1_cbc", "name":"혈액 분석기"},
    "e2":{"key":"e2_chem", "name":"생화학 분석기"},
    "e3":{"key":"e3_coag", "name":"응고 분석기"},
    "e4":{"key":"e4_urin", "name":"요 분석기"}
}
EQ_KEYS = Literal["e1", "e2", "e3", "e4"]


# Data_key 정의
type DATA_KEY = Literal[
    "e01-혈액분석기", "e02-생화학분석기", "e03-응고분석기", "e04-요분석기"
]


# t01의 주요 session key 값
class SessionKeys:

    # t01의 view key
    CURRENT_VIEW: Final[str] = f"{TOOL_KEY}_config_view"

    # --- 데이터 ---
    # 데이터의 session 값
    DATA1_CBC: Final[str] = f"{TOOL_KEY}_data_{EQUIPMENTS["e1"]["key"]}"
    DATA2_CHEM: Final[str] = f"{TOOL_KEY}_data_{EQUIPMENTS["e2"]["key"]}"
    DATA3_COAG: Final[str] = f"{TOOL_KEY}_data_{EQUIPMENTS["e3"]["key"]}"
    DATA4_URIN: Final[str] = f"{TOOL_KEY}_data_{EQUIPMENTS["e4"]["key"]}"

    # 전체 실험 설정 - dict
    CONFIG_EXP_SET: Final[str] = f"{TOOL_KEY}_config_exp"

    # 분석기별 설정 - dict
    CONFIG_COLUMN_SET: Final[str] = f"{TOOL_KEY}_config_column_set"

    # 업로드된 파일에 대한 세션 id
    LAST_LOADED_FILE_ID: Final[str] = f"{TOOL_KEY}_last_loaded_file_id"

    # --- Widget 초기화를 위한 세션 키 ---
    # message 저장용 세션 키
    ERROR_MESSAGE: Final[str] = f"{TOOL_KEY}_messages"
    # 에러 대상 위젯 정보
    ERROR_TARGET_WIDGET: Final[str] = f"{TOOL_KEY}_error_target_widget"
    # 개별 위젯 초기화 카운터 - dict {widget_key: count}
    WIDGET_RESET_DICT: Final[str] = f"{TOOL_KEY}_widget_reset_dict"


# 위잿의 key 값
class WidgetKeys:
    U1: Final[str] = f"{TOOL_KEY}_widget_u1"
    U2: Final[str] = f"{TOOL_KEY}_widget_u2"
    U3: Final[str] = f"{TOOL_KEY}_widget_u3"
    U4: Final[str] = f"{TOOL_KEY}_widget_u4"


# 데이터 키와 위젯 키 매핑 (에러 발생 시, 초기화 대상 탐색 목적)
DATA_TO_WIDGET: Final[dict[DATA_KEY, str]] = {
    "e01-혈액분석기":WidgetKeys.U1,
    "e02-생화학분석기":WidgetKeys.U2,
    "e03-응고분석기":WidgetKeys.U3,
    "e04-요분석기":WidgetKeys.U4
}


# 필수 입력값 여부
class Check:
    EXP_SETUP: Final[str] = f"{TOOL_KEY}_check_exp_setup"
    COLUMN_SETUP: Final[str] = f"{TOOL_KEY}_check_column_setup"


# View에 대한 값
class View:
    MAIN: Final[str] = f"{TOOL_KEY}_main"
    EXP_SETUP: Final[str] = f"{TOOL_KEY}_exp_setup"
    COLUMN_SETUP: Final[str] = f"{TOOL_KEY}_column_setup"


# Title
class Titles:

    # --- 메인 화면 ---
    MAIN_TITLE: Final[str] = "임상병리 데이터 처리기"
    MAIN_UPLOAD: Final[str] = "데이터 업로드"
    MAIN_SETUP: Final[str] = "시험 설정"
    MAIN_ACTION: Final[str] = "데이터 처리"

    # --- 시험 설정 --- 
    EXP_SETUP: Final[str] = "실험 설정"

    # --- 컬럼 설정 ---
    COLUMN_SETUP: Final[str] = "변수 설정"


class Buttons:

    BACK_TO_MAIN: Final[str] = "임상병리 데이터 처리기 메인 화면으로 이동"