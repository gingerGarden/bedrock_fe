from typing import Tuple, List, Dict, Union, Optional
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np

from app.api.p7_admin import get_all_user_records
from app.constants.values import AdminUserTable, UsersRecord
from app.constants.messages import AdminMsg
from app.constants.keys import AdminViews


# API로부터 전달받는 Record 객체
Record = Dict[str, Union[str, int, bool, datetime, None]]



# ==============================
# 공용 유틸
# ==============================
def view_changer(view_name: str):
    """
    로그인 뷰 상태 전환 후 즉시 rerun.

    매개변수
    --------
    view_name : str
        이동할 뷰 이름 (LoginViews.*)

    동작
    ----
    - 세션 상태(LoginViews.KEY)를 새로운 뷰로 변경
    - 곧바로 st.rerun() 호출로 UI 재렌더링
    """
    # View 변경
    st.session_state[AdminViews.KEY] = view_name
    # UI를 새로 그림
    st.rerun()




class UserTable:
    """
    Admin Users Table 전처리 파이프라인
    - 외부 의존: get_all_user_records() -> (mask: bool, msg: str, records: List[Record])
    - 출력: (mask, msg, df)  # 실패 시 df=None
    """

    @classmethod
    def all(cls) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        전체 유저 조회
        """
        # table을 DB에서 조회한다
        mask, msg, records = get_all_user_records()

        # 정상 조회되지 않았거나 조회되었으나 데이터가 없는 경우
        if not mask or not records:
            return mask, msg, None
        
        # 프로세스 진행
        try:
            df = cls._all_process(records=records)
            return mask, msg, df
        # 전처리 실패 시 오류 반환 - 관리자 페이지이므로, 오류를 그대로 출력
        except Exception as e:
            return False, AdminMsg.DATA_HANDLING_FAIL.format(e=e), None

    # ----------------- 내부 파이프라인 -----------------
    @classmethod
    def _all_process(cls, records: List[Record]) -> pd.DataFrame:

        # records를 DataFrame으로 변환
        df = pd.DataFrame.from_records(records)

        # 컬럼 무결성 확인
        Checker.user_record_column_names(df=df)

        # ---- 시간 처리: deleted_at 기준 정지일수 계산 ----
        deleted_at_df = TimeHandler.interval_time(df, time_col="deleted_at")
        
        # ---- Role 처리: 임의 개수의 role 컬럼 가중합 → 문자열 라벨 ----
        role_df = FormatHandler.role_handler(df)

        # ---- 원본 필요컬럼 + 시간/권한 컬럼 병합 ----
        out = (
            df.loc[:, AdminUserTable.RESULT_ORIGIN_COLUMNS]
            .merge(deleted_at_df, on=UsersRecord.idx, how="left")
            .merge(role_df, on=UsersRecord.idx, how="left")
        )
        # ---- 가독성을 위한 데이터 전처리 ----
        # 컬럼명 변경
        out = out.rename(columns=AdminUserTable.RESULT_NEW_COLUMN_NAMES)
        # 정렬
        out = out.sort_values(
            AdminUserTable.RESULT_COLUMN_SORT,
            ascending=AdminUserTable.RESULT_COLUMN_SORT_ASCENDING,
            kind="stable"
        ).reset_index(drop=True)
        # idx 컬럼 제외
        out = FormatHandler.remove_idx_column(out)

        return out



class TimeHandler:
    """
    시간 파싱 및 '현 시점 - 특정 시간컬럼' 간격 계산
    """
    @classmethod
    def interval_time(
            cls, 
            df: pd.DataFrame, 
            time_col: str
        ) -> pd.DataFrame:
        """
        지정된 time_col이 AdminUserTable.DT_COLUMNS 내에 있어야 함.
        반환: [UsersRecord.idx, f"{time_col}_interval"] 로 구성된 DF
        """
        # time_col이 사전 정의한 datetime 컬럼에 해당하는지 확인
        if time_col not in AdminUserTable.DT_COLUMNS:
            raise ValueError(
                    f"{time_col}은 Users Table에서 반환하는 값에 해당하지 않습니다!"
                )
        # 시간 간격 연산
        t_df = df[[UsersRecord.idx, time_col]].copy()
        t_df = cls._t_df_handler(t_df=t_df, time_col=time_col)
        return t_df

    @classmethod
    def _t_df_handler(
            cls, 
            t_df: pd.DataFrame, 
            time_col: str
        ) -> pd.DataFrame:

        # 신규 생성 컬럼명 반환
        dt_col, interval_col = cls._get_time_column_names(time_col)

        # str(datetime) datetime으로 변환
        t_df[dt_col] = pd.to_datetime(t_df[time_col], utc=True, errors="coerce")

        # 시간 간격 계산 (UTC 기준)
        t_df[interval_col] = pd.Timestamp.now(tz="UTC") - t_df[dt_col]

        # 표시 형식(일자 int or Timedelta) 통일
        t_df[interval_col] = cls._interval_format(s=t_df[interval_col])

        # 주요 컬럼만 반환
        return t_df[[UsersRecord.idx, interval_col]]
    
    @classmethod
    def _interval_format(
            cls, 
            s: pd.Series
        ) -> pd.Series:
        """
        AdminUserTable.DT_SHOW_ONLY_DATE == True: 일 단위(Int64)로 변환, 결측은 0
        False: Timedelta 유지, 결측은 0초
        """
        # 마이크로초 제거
        s = s.dt.floor("s")

        # cls.show_only_date에 따른 시간 표시 수준 변경
        if AdminUserTable.DT_SHOW_ONLY_DATE:
            # '3 days 04:12:10' → 3 (int)
            s = s.dt.days
            # 결측값 0
            return s.astype("Int64").fillna(0)
        else:
            # Timedelta 유지, 결측값 0초
            return s.fillna(pd.Timedelta(0))

    @classmethod
    def _get_time_column_names(
            cls, 
            time_col: str
        ) -> Tuple[str, str]:
        """
        time_col에 대한 dt_col, interval_col 반환
        """
        # datetime 변수명 (dtype = datetime)
        dt_col = AdminUserTable.DT_ADD_COL.format(col=time_col)
        # 현재 시간까지 datetime 간격 변수명
        interval_col = AdminUserTable.DT_INTERVAL_COL.format(col=time_col)
        return dt_col, interval_col



class FormatHandler:
    """
    권한/표시 등 포맷팅
    """
    @classmethod
    def role_handler(
            cls, 
            df: pd.DataFrame
        ) -> pd.DataFrame:
        # role column을 가지고 온다
        role_columns: List[str] = cls._get_role_column_list()

        # role 관련 컬럼만 추출
        r_df: pd.DataFrame = df[[UsersRecord.idx] + role_columns].copy()

        # role 숫자로 변경
        r_df = cls._make_role_number_column(role_columns, r_df)

        # role num 컬럼 합침
        r_df = cls._plus_role_number_columns(role_columns, r_df)

        # role num 컬럼 문자열 변환
        r_df = cls._total_role_number_convert_to_string(r_df)
        
        return r_df[[UsersRecord.idx, AdminUserTable.ROLE_STRING_COL]]

    @classmethod
    def _get_role_column_list(cls) -> List[str]:
        # role 관련 컬럼 추출
        stack  = []
        for key, value in AdminUserTable.ROLE_COL_DICT.items():
            if value != 0:
                stack.append(key)
        return stack

    @classmethod
    def _make_role_number_column(
            cls,
            role_columns: List[str],
            r_df: pd.DataFrame
        ) -> pd.DataFrame:
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
            cls,
            role_columns: List[str],
            r_df: pd.DataFrame
        ) -> pd.DataFrame:
        # 두 number 컬럼을 합친다
        r_df[AdminUserTable.ROLE_NUM_TOTAL_COL] = r_df[
            AdminUserTable.ROLE_NUM_COL.format(col=role_columns[0])
        ] + r_df[
            AdminUserTable.ROLE_NUM_COL.format(col=role_columns[1])
        ]
        return r_df
    
    @classmethod
    def _total_role_number_convert_to_string(
            cls,
            r_df: pd.DataFrame
        ) -> pd.DataFrame:
        # 0과 1인 경우, 지정된 값을 배정하고 그 외엔 admin을 배정한다
        # kay value 역전 dict
        reverse_dict = {
            value:key for key, value in AdminUserTable.ROLE_COL_DICT.items()
        }
        # 숫자별로 그에 대한 문자열 삽입
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
    def remove_idx_column(
            cls, 
            df: pd.DataFrame
        ) -> pd.DataFrame:

        # idx 컬럼 제외
        if AdminUserTable.RESULT_EXCLUDE_IDX:
            column_list = df.columns.to_list()
            column_list.remove(UsersRecord.idx)
            return df[column_list]
        
        return df
            


class Checker:
    
    @classmethod
    def user_record_column_names(
            cls, df: pd.DataFrame
        ):
        # UsersRecord에 있는 컬럼명들 조회
        expected_cols = [
            v for k, v in UsersRecord.__dict__.items()
            if not k.startswith("__") and isinstance(v, str)   # <-- 추가
        ]
        # 컬럼이 부족한 경우
        missing_column = list(set(expected_cols) - set(df.columns))
        if missing_column:
            raise KeyError(f"Users Record에 다음 컬럼이 누락됨: {missing_column}")

        # 컬럼이 추가로 들어온 경우
        extra_column = list(set(df.columns) - set(expected_cols))
        if extra_column:
            raise KeyError(f"[Warning] 예상 외 컬럼 존재: {extra_column}")