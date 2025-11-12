from typing import Tuple, List, Dict, Union, Optional, Literal
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np

from app.api.p9_admin import get_all_user_records
from app.constants.values import AdminUserTable
from app.constants.keys import UsersRecord, AdminUserModify
from app.constants.messages import AdminMsg


# API로부터 전달받는 단일 레코드 타입
Record = Dict[str, Union[str, int, bool, datetime, None]]


# ==============================
# 데이터 조회
# ==============================
class UserTable:
    """
    Admin Users Table 전처리 파이프라인.

    외부 의존
    --------
    get_all_user_records() -> Tuple[bool, str, List[Record]]
        - DB/백엔드에서 사용자 목록을 가져오는 함수.

    출력
    ----
    Tuple[bool, str, Optional[pd.DataFrame]]
        - mask : 처리 성공 여부
        - msg  : 상태/오류 메시지
        - df   : 전처리된 테이블 (실패 시 None)

    Notes
    -----
    - 전처리 결과는 FE(AgGrid) 표시 최적화를 위해 문자열화가 포함된다.
    - 세션에 보안/UX 방어용 인덱스 목록(AdminUserModify.*_IDX_LIST)도 함께 기록한다.
    """
    @classmethod
    def all(cls) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        전체 유저 목록을 조회하고, 관리자 화면에 맞춰 전처리한 DataFrame을 반환한다.

        처리 개요
        --------
        1) get_all_user_records()로 원시 records 조회
        2) 비정상/빈 응답 방어
        3) _all_process()로 컬럼 검증, 시간/권한 가공, 정렬/리네이밍
        4) 실패 시 관리자 메시지로 예외 내용을 포함해 반환
        """
        # 1) DB/백엔드 조회
        mask, msg, records = get_all_user_records()

        # 2) 비정상 또는 빈 결과 방어
        if not mask or not records:
            return mask, msg, None
        # 3) 전처리 파이프라인 실행
        try:
            df = cls._all_process(records=records)
            return mask, msg, df
        # 4) 전처리 중 예외 발생 시: 관리자 페이지 특성상 오류 그대로 노출
        except Exception as e:
            return False, AdminMsg.DATA_HANDLING_FAIL.format(e=e), None

    # ----------------- 내부 파이프라인 -----------------
    @classmethod
    def _all_process(cls, records: List[Record]) -> pd.DataFrame:
        """
        원시 records를 받아 결과 테이블로 가공한다.

        처리 단계
        --------
        - DataFrame 변환 및 컬럼 무결성 검증(누락/초과)
        - 시간 처리: deleted_at·signup_at 기준 경과 시간 계산(+ 정지여부 파생)
        - 권한 처리: 복수 role 컬럼 → 가중합 → 최종 문자열 라벨
        - 필요한 원본 컬럼 + 파생 컬럼 병합
        - 컬럼명 리네이밍, 전체 문자열화, idx zero-padding 등 표시 정리
        """
        # records → DataFrame
        df = pd.DataFrame.from_records(records)

        # 필수/허용 컬럼 검증 (부족/초과 모두 감지)
        Checker.user_record_column_names(df=df)

        # ---- 시간 처리: 경과 시간/정지여부 파생 ----
        deleted_at_df = TimeHandler.interval_time(df, time_col="deleted_at")
        signup_at_df = TimeHandler.interval_time(df, time_col="signup_at")
        
        # ---- 권한 처리: 임의 개수의 role 컬럼 가중합 → 문자열 라벨 ----
        role_df = FormatHandler.role_handler(df)

        # ---- 원본 필요컬럼 + 시간/권한 컬럼 병합 ----
        out: pd.DataFrame = (
            df.loc[:, AdminUserTable.RESULT_ORIGIN_COLUMNS]
            .merge(signup_at_df, on=UsersRecord.idx, how="left")
            .merge(deleted_at_df, on=UsersRecord.idx, how="left")
            .merge(role_df, on=UsersRecord.idx, how="left")
        )
        # ---- AgGrid/FE 표시를 위한 후처리 ----
        out = FormatHandler.df_final_cleaner(df=out)

        # --- FE 방어를 위한 주요 idx 추출(세션 저장) ---
        cls._key_idxes_add_to_session(df=out)
        return out
    
    @classmethod
    def _key_idxes_add_to_session(cls, df: pd.DataFrame):
        """
        FE 조작 방어/UX를 위한 인덱스 목록을 세션에 저장한다.

        - ADMIN_IDX_LIST : '관리자' 계정 idx(수정 금지)
        - BLOCK_IDX_LIST : '정지된' 계정 idx(하드삭제 허용 대상)
        """
        # [목적] 관리자 유저는 관리자 페이지에서 수정 불가
        st.session_state[AdminUserModify.ADMIN_IDX_LIST] = \
            df[df['권한'] == "admin"]["idx"].to_list()
        
        # [목적] Hard-delete는 Soft-delete가 된 유저만 허가
        st.session_state[AdminUserModify.BLOCK_IDX_LIST] = \
            df[df['정지여부'] == "True"]["idx"].to_list()



class TimeHandler:
    """
    시간 파싱 및 '현 시점 - 특정 시간컬럼' 간격 계산 유틸리티.

    설계 원칙
    --------
    - 입력이 문자열/datetime 혼재여도 안전하게 파싱 (errors='coerce')
    - 기준 시각은 UTC (서버/클라이언트 표준화)
    - AdminUserTable.DT_SHOW_ONLY_DATE 설정에 따라
      '일 단위 Int' 또는 'Timedelta'로 표준화하여 출력

    주의
    ----
    - NaT(파싱 실패/결측)는 '현재 - NaT'가 NaT가 되므로,
      DT_SHOW_ONLY_DATE=True일 때 .dt.days가 NA가 될 수 있다.
      (현 구현은 그대로 노출; 필요시 fillna 정책을 추가 고려)
    """

    @classmethod
    def interval_time(
            cls, 
            df: pd.DataFrame, 
            time_col: Literal['created_at', 'signup_at', 'updated_at', 'deleted_at']
        ) -> pd.DataFrame:
        """
        지정된 time_col에 대한 경과 시간을 계산한다.

        Parameters
        ----------
        df : pd.DataFrame
            원본 데이터프레임
        time_col : {'created_at','signup_at','updated_at','deleted_at'}
            경과 시간을 계산할 datetime 컬럼명(사전정의된 허용 목록)

        Returns
        -------
        pd.DataFrame
            [UsersRecord.idx, f"{time_col}_interval"] (+ '정지여부'@deleted_at)로 구성.

        Raises
        ------
        ValueError
            time_col이 허용 목록(AdminUserTable.DT_COLUMNS)에 없을 때
        """
        # time_col의 유효성 검증
        if time_col not in AdminUserTable.DT_COLUMNS:
            raise ValueError(
                    f"{time_col}은 Users Table에서 반환하는 값에 해당하지 않습니다!"
                )
        # deleted_at인 경우, '정지여부' 파생
        if time_col == 'deleted_at':
            df['정지여부'] = ~df["deleted_at"].isna()
            column_list = [UsersRecord.idx, '정지여부', time_col]
        else:
            column_list = [UsersRecord.idx, time_col]

        # 계산 대상 최소 컬럼만 추출
        t_df = df[column_list].copy()

        # 내부 처리
        t_df = cls._t_df_handler(t_df=t_df, time_col=time_col)
        return t_df

    @classmethod
    def _t_df_handler(cls, t_df: pd.DataFrame, time_col: str) -> pd.DataFrame:
        """
        단일 datetime 컬럼에 대해 UTC 기준 경과 시간을 계산하고 표준 포맷으로 변환한다.

        Steps
        -----
        1) 문자열/None → datetime(UTC) 변환(errors='coerce'로 NaT 허용)
        2) now(UTC) - 대상시각 → Timedelta 계산
        3) AdminUserTable.DT_SHOW_ONLY_DATE 정책에 맞춰 포맷 통일
        """
        # 신규 생성 컬럼명 (원본 문자열 파싱 결과, 경과 시간)
        dt_col, interval_col = cls._get_time_column_names(time_col)

        # 문자열/None → datetime(UTC) 안전 파싱 (파싱 실패 시 NaT)
        t_df[dt_col] = pd.to_datetime(t_df[time_col], utc=True, errors="coerce")

        # 경과 시간 = '현재(UTC) - 대상시각(UTC)'
        t_df[interval_col] = pd.Timestamp.now(tz="UTC") - t_df[dt_col]

        # 표준 포맷으로 통일 (일 Int 또는 Timedelta)
        t_df[interval_col] = cls._interval_format(s=t_df[interval_col])

        # 최소 컬럼만 반환
        if time_col == 'deleted_at':
            return t_df[[UsersRecord.idx, '정지여부', interval_col]]
        return t_df[[UsersRecord.idx, interval_col]]
    
    @classmethod
    def _interval_format(cls, s: pd.Series) -> pd.Series:
        """
        경과 시간 Series를 표준 포맷으로 변환한다.

        규칙
        ----
        - 마이크로초 절삭(초 단위로 고정)
        - DT_SHOW_ONLY_DATE=True  → .dt.days(Int64, NA 가능)
        - False → Timedelta 유지(결측은 NaT 기반; 필요 시 별도 fill 정책 고려)
        """
        # 마이크로초 제거 (초 단위 정렬)
        s = s.dt.floor("s")

        if AdminUserTable.DT_SHOW_ONLY_DATE:
            # 예: '3 days 04:12:10' → 3
            # (Int64로 두어 NA 유지; 필요 시 .fillna(0) 등 정책 적용 가능)
            return s.dt.days
        
        # Timedelta 유지(표시 목적; 필요 시 .fillna(pd.Timedelta(0)) 고려)
        return s

    @classmethod
    def _get_time_column_names(cls, time_col: str) -> Tuple[str, str]:
        """
        time_col에 대응하는 파생 컬럼명 쌍(dt_col, interval_col)을 생성한다.

        Returns
        -------
        dt_col : str
            파싱된 datetime 저장 컬럼명
        interval_col : str
            현 시점까지의 경과 시간 저장 컬럼명
        """
        # datetime 변수명 (dtype = datetime)
        dt_col = AdminUserTable.DT_ADD_COL.format(col=time_col)
        # 현재 시간까지 datetime 간격 변수명
        interval_col = AdminUserTable.DT_INTERVAL_COL.format(col=time_col)
        return dt_col, interval_col



class FormatHandler:
    """
    권한/표시 등 테이블 포맷팅 유틸리티.
    - role 관련 컬럼의 가중합을 통해 통합 라벨(user/developer/admin)을 생성한다.

    주의
    ----
    - 현재 구현은 '역할 컬럼이 2개'라는 전제를 둔 단순 가중합 방식.
      (AdminUserTable.ROLE_COL_DICT에서 값이 0이 아닌 항목 2개 가정)
    - 역할 컬럼이 추가될 가능성이 있다면 sum(...) 기반으로 일반화 필요.
    """

    @classmethod
    def role_handler(
            cls, 
            df: pd.DataFrame
        ) -> pd.DataFrame:
        """
        역할 관련 원본 컬럼들 → 가중합 숫자 → 최종 문자열 라벨로 변환한다.

        Returns
        -------
        pd.DataFrame
            [UsersRecord.idx, AdminUserTable.ROLE_STRING_COL] 만 포함
        """
        # 1) 역할 컬럼 목록 수집 (가중치가 0이 아닌 것만)
        role_columns: List[str] = cls._get_role_column_list()

        # 2) 최소 컬럼만 추출 (role 관련)
        r_df: pd.DataFrame = df[[UsersRecord.idx] + role_columns].copy()

        # 3) 역할 True/False → 가중치 숫자 컬럼으로 치환
        r_df = cls._make_role_number_column(role_columns, r_df)

        # 4) 숫자 컬럼 합산 (※ 현재 2개 컬럼 전제)
        r_df = cls._plus_role_number_columns(role_columns, r_df)

        # 5) 합산 숫자 → 문자열 라벨(user/developer/admin)
        r_df = cls._total_role_number_convert_to_string(r_df)
        
        return r_df[[UsersRecord.idx, AdminUserTable.ROLE_STRING_COL]]

    @classmethod
    def _get_role_column_list(cls) -> List[str]:
        """
        ROLE_COL_DICT에서 가중치가 0이 아닌 역할 컬럼명만 추출.

        Returns
        -------
        List[str]
            표시/합산 대상 역할 컬럼 리스트
        """
        stack  = []
        for key, value in AdminUserTable.ROLE_COL_DICT.items():
            if value != 0:
                stack.append(key)
        return stack

    @classmethod
    def _make_role_number_column(
            cls, role_columns: List[str], r_df: pd.DataFrame
        ) -> pd.DataFrame:
        """
        각 역할 컬럼을 대응 가중치 숫자로 치환하여
        '{ROLE_NUM_COL.format(col=...)}' 이름의 새 컬럼에 저장한다.
        """
        for column in role_columns:
            # 대상 role 컬럼 Series
            s = r_df[column]
            # role_columns_dict에 배정되어 있는 값으로 치환
            r_df[AdminUserTable.ROLE_NUM_COL.format(col=column)] = np.where(
                s, AdminUserTable.ROLE_COL_DICT[column], 0
            )
        return r_df
    
    @classmethod
    def _plus_role_number_columns(
            cls, role_columns: List[str], r_df: pd.DataFrame
        ) -> pd.DataFrame:
        """
        숫자 역할 컬럼들을 합산하여 AdminUserTable.ROLE_NUM_TOTAL_COL 에 저장한다.

        현재 구현은 'role_columns가 정확히 2개'라는 전제 하에 동작한다.
        (예: developer, admin 두 축)

        Notes
        -----
        - 역할 종류 확장 시: sum([...]) 형태로 일반화 필요
        """
        # 두 number 컬럼을 합친다
        r_df[AdminUserTable.ROLE_NUM_TOTAL_COL] = (
            r_df[AdminUserTable.ROLE_NUM_COL.format(col=role_columns[0])] + 
            r_df[AdminUserTable.ROLE_NUM_COL.format(col=role_columns[1])]
        )
        return r_df
    
    @classmethod
    def _total_role_number_convert_to_string(
            cls,
            r_df: pd.DataFrame
        ) -> pd.DataFrame:
        """
        합산된 숫자 역할값을 최종 문자열 라벨로 변환한다.

        규칙(예시)
        ----------
        - 0 → "user"
        - 1 → "developer"
        - 그 외(>=2) → "admin"

        ※ ROLE_COL_DICT의 가중치 체계가 바뀌면 본 규칙도 함께 조정해야 한다.
        """
        # 0과 1인 경우, 지정된 값을 배정하고 그 외엔 admin을 배정한다
        r_df[AdminUserTable.ROLE_STRING_COL] = np.where(
            r_df[AdminUserTable.ROLE_NUM_TOTAL_COL].values == 0, 
            "user",
            np.where(
                r_df[AdminUserTable.ROLE_NUM_TOTAL_COL].values == 1, 
                "developer", 
                "admin"
            )
        )
        return r_df
    
    @classmethod
    def df_final_cleaner(
            cls, 
            df: pd.DataFrame
        ) -> pd.DataFrame:
        """
        FE 표시 최적화를 위한 후처리.

        Steps
        -----
        - 컬럼명 일괄 리네이밍
        - (정렬은 FE에 위임; 필요 시 주석 해제)
        - 모든 컬럼 문자열화(AgGrid/Streamlit 렌더 안정성)
        - idx zero-padding(문자열 정렬시 시각적 정렬 유지)
        """

        # 컬럼명 변경
        df = df.rename(columns=AdminUserTable.RESULT_NEW_COLUMN_NAMES)
        
        # 정렬 - FE 자체 정렬 기능에 맡김
        # df = df.sort_values(
        #     AdminUserTable.RESULT_COLUMN_SORT,
        #     ascending=AdminUserTable.RESULT_COLUMN_SORT_ASCENDING,
        #     kind="stable"
        # ).reset_index(drop=True)
        
        # idx 컬럼 zero-padding 기준 계산(자릿수 고정)
        idx_max_size = len(str(df[UsersRecord.idx].max()))

        # 모든 컬럼 문자열 변환 - Streamlit 렌더링/정렬에 유리
        df = cls._all_column_convert_to_string(df)

        # idx zero-padding 적용 (문자열 정렬시 '1, 2, 10' 깨짐 방지)
        df[UsersRecord.idx] = [
            i.zfill(idx_max_size) for i in df[UsersRecord.idx]
        ]
        return df

    @classmethod
    def _all_column_convert_to_string(
            cls, 
            df: pd.DataFrame
        ) -> pd.DataFrame:
        """
        모든 컬럼을 문자열(str)로 변환한다.

        Notes
        -----
        - FE 렌더 안정성을 높이고, 혼합 dtype으로 인한 필터/정렬 이슈를 줄인다.
        - 숫자/날짜의 본래 dtype은 잃지만, 이 테이블은 '표시 용도'임을 전제로 한다.
        """
        for column in df.columns:
            df[column] = df[column].astype('str')

        return df
    
            


class Checker:
    """
    입력 DataFrame의 컬럼 무결성 검증 유틸리티.

    검증 항목
    --------
    - 누락 컬럼: UsersRecord 정의 대비 부족한 컬럼 탐지 → KeyError
    - 초과 컬럼: 예상 외 컬럼 존재 시 경고성 KeyError (정책적으로 허용/무시할지 선택)
    """

    @classmethod
    def user_record_column_names(
            cls, df: pd.DataFrame
        ):
        """
        UsersRecord에 정의된 컬럼 집합과 DataFrame의 컬럼 집합을 비교해
        누락/초과를 감지한다.

        Raises
        ------
        KeyError
            - required 컬럼 누락
            - 예상 외 컬럼 초과
        """
        # UsersRecord의 문자열 속성만 필수 컬럼으로 간주
        expected_cols = [
            v for k, v in UsersRecord.__dict__.items()
            if not k.startswith("__") and isinstance(v, str)
        ]

        # 누락 컬럼 체크
        missing_column = list(set(expected_cols) - set(df.columns))
        if missing_column:
            raise KeyError(f"Users Record에 다음 컬럼이 누락됨: {missing_column}")

        # 초과 컬럼 체크 (정책적으로 경고를 예외로 처리)
        extra_column = list(set(df.columns) - set(expected_cols))
        if extra_column:
            raise KeyError(f"Users Record에 예상 외 컬럼 존재: {extra_column}")