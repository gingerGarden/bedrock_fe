from typing import Optional, List, Tuple
from pydantic import BaseModel

import streamlit as st
import pandas as pd

from st_aggrid import (
    AgGrid, GridOptionsBuilder, GridUpdateMode, 
    DataReturnMode, JsCode
)
from app.api.p9_admin import (
    modify_bulk_block, modify_bulk_signup, 
    modify_bulk_delete, modify_single_password
)
from app.constants.keys import (
    AdminViews, AdminUserModify, UsersRecord, FlashKeys
)
from app.constants.values import AdminUserTable, Ratio
from app.constants.messages import AdminMsg
from app.utils.p9_df_handler import UserTable
from app.utils.utils import Flash
from app.schemas.p1_login import Password


# ============================================================
#  Pydantic 단일 필드 검증기
# ============================================================
class PasswordCheck(BaseModel):
    """
    비밀번호 단일 필드 형식 검증용 모델.
    - UI 단에서 간단히 Password 스키마 정책(길이/문자군 등)을 재검증한다.
    - 실패 시 ValidationError가 발생하며, 호출부에서 메시지로 변환한다.
    """
    pwd: Password


# ============================================================
#  공용 유틸
# ============================================================
def view_changer(view_name: str):
    """
    화면의 '뷰 상태'를 전환하고 즉시 재렌더링한다.

    Parameters
    ----------
    view_name : str
        이동할 뷰 식별자 (예: AdminViews.ALL, AdminViews.SIGNUP ...)

    Notes
    -----
    - st.session_state[AdminViews.KEY] 를 변경한 뒤 st.rerun()으로 즉시 UI를 갱신한다.
    - 사이드바 버튼/탭 클릭 등에서 공통 사용.
    """
    # View 변경
    st.session_state[AdminViews.KEY] = view_name
    # UI를 새로 그림 (즉시 반영)
    st.rerun()



# ============================================================
#  Dialog (Modal)
#  - 하드 삭제는 되돌릴 수 없으므로 사용자 확인을 반드시 거친다.
#  - 모달 내부에서 API를 호출하고, 성공/실패 Flash 후 즉시 rerun.
#  - SidebarAction.delete()에서 idxes를 인자로 전달해 띄운다.
# ============================================================
@st.dialog(
    "정말 삭제할까요?", 
    width="small", 
    dismissible=False,         # 바깥 클릭/ESC로 닫히지 않도록(의도치 않은 닫힘 방지)
    on_dismiss="ignore"        # 모달 dismiss 이벤트를 특별히 처리하지 않음
)
def delete_confirm_dialog(idxes: List[int]):
    """
    하드 삭제 확인 모달.

    Parameters
    ----------
    idxes : List[int]
        삭제 대상으로 선택된 사용자 idx 리스트.

    UX
    --
    - '취소' 클릭: 변경 없이 Flash만 띄우고 종료(재렌더).
    - '삭제' 클릭: API 호출 → Flash → DB 재조회 → 재렌더.
    """
    # 모달 표시
    _n = len(idxes)
    st.write(f"선택된 항목 {_n}건이 완전 삭제됩니다. 되돌릴 수 없습니다.")

    # 중복 제출 방지 플래그
    if AdminUserModify.DELETE_WAIT not in st.session_state:
        st.session_state[AdminUserModify.DELETE_WAIT] = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "취소", 
            use_container_width=True, 
            disabled=st.session_state[AdminUserModify.DELETE_WAIT]
        ):
            # 사용자 취소 안내 후 리런
            SideBarAction.interupt_flash_msg(msg=AdminMsg.CANCEL_MODIFY)

    with col2:
        if st.button(
            "삭제", 
            use_container_width=True, 
            type="primary", 
            disabled=st.session_state[AdminUserModify.DELETE_WAIT]
        ):
            st.session_state[AdminUserModify.DELETE_WAIT] = True
            with st.spinner("삭제 중..."):
                # API 전달
                mask, msg, _ = modify_bulk_delete(idxes=idxes)
            # disabled 해제
            st.session_state[AdminUserModify.DELETE_WAIT] = False
            SideBarAction.after_modify(mask, msg)



# ============================================================
#  Table 조회 - DB 통신 및 DF 조작
# ============================================================
class GetTable:
    """
    Users Table 조회/가공 유틸 클래스.
    - API → DataFrame 변환 → 뷰별 하위 DF 분리 → session_state 저장
    """

    @classmethod
    def base(cls):
        """
        전체 Users DF를 조회하여 세션에 캐싱하고, 뷰별 하위 DF를 생성한다.

        Flow
        ----
        1) UserTable.all() 로 전체 DF 조회
        2) 실패 시 st.error
        3) 성공 시:
           - AdminViews.TABLE_ALL
           - AdminViews.TABLE_SIGNUP (승인여부 == False)
           - AdminViews.TABLE_BLOCK  (정지여부 == True)
           - AdminViews.TABLE_DEVELOPER (권한 == 'developer')
           를 세션에 저장한다.
        """
        # 전체 DB 조회
        mask, msg, df = UserTable.all()
        
        # DB 정상 조회 실패 또는 DB에 데이터가 없는 경우 경고 출력
        if not mask:
            st.error(msg)
            return
        
        # 정상 데이터 조회 시, 출력할 Table들 모두 생성
        st.session_state[AdminViews.TABLE_ALL] = df
        st.session_state[AdminViews.TABLE_SIGNUP] = df[df["승인여부"] == "False"]
        st.session_state[AdminViews.TABLE_BLOCK] = df[df["정지여부"] == "True"]
        st.session_state[AdminViews.TABLE_DEVELOPER] = df[df["권한"] == "developer"]
        # Clear는 조회될 수 없는 값을 조회하여, 선택된 행을 취소하는 방법을 사용
        st.session_state[AdminViews.TABLE_CLAER] = df[df["idx"].isna()]
            
    @classmethod
    def one_user(cls, user_id: Optional[str]):
        """
        특정 user_id 단일 조회.

        Requirements
        ------------
        - AdminViews.TABLE_ALL 이 선행 조회되어 있어야 한다.

        Behavior
        --------
        - 조건 미충족 시 에러 안내.
        - 조건 충족 시 필터링된 DF를 AdminViews.TABLE_USER_ID 에 저장.
        """
        # 렌더링 대상을 아직 조회하지 않은 경우
        if AdminViews.TABLE_ALL not in st.session_state:
            st.error('"DB 조회"를 먼저 하십시오.')
            return
        
        # user_id 조회
        df: pd.DataFrame = st.session_state[AdminViews.TABLE_ALL]
        # 조회 결과에 따른 출력 - 결과가 없더라도 비어있는 df가 출력되므로 괜찮음
        st.session_state[AdminViews.TABLE_USER_ID] = df[df["ID"] == user_id].copy()



class ShowTable:
    """
    AgGrid 렌더링 및 부가정보 출력.
    - 선택된 행의 idx 리스트를 session_state[AdminUserModify.INDEX_LIST]에 반영.
    """

    @classmethod
    def rendering(cls, key: str):
        """
        주어진 key의 DF를 AgGrid로 렌더링하고 선택 상태를 세션에 저장.

        Parameters
        ----------
        key : str
            렌더링할 세션 키 (AdminViews.TABLE_*)
        """

        # 대상이 아닌 key를 입력했는지 확인 - 코드 레벨
        cls._key_checker(key)
        
        # 렌더링 대상을 아직 조회하지 않은 경우
        if AdminViews.TABLE_ALL not in st.session_state:
            st.error('"DB 조회"를 먼저 하십시오.')
            return
        
        # 현재 세션에 저장된 대상 DF을 꺼내온다
        df: pd.DataFrame = st.session_state[key]
        grid_respons = cls._table_rendering_inner(df)       # AgGrid 렌더링

        # 선택된 행들의 원본 record dict 리스트 → DataFrame → idx 리스트 추출
        selected_records: pd.DataFrame= grid_respons["selected_rows"]
        if selected_records is not None:
            st.session_state[AdminUserModify.INDEX_LIST] = selected_records['idx'].to_list()

        # 추가 기능 - 행 크기, 선택 index 출력
        cls.utils(df)

    @classmethod
    def _key_checker(cls, key: str):
        """
        유효한 테이블 key인지 검증. (개발 실수 방지용)
        """
        if key not in [
                AdminViews.TABLE_ALL,
                AdminViews.TABLE_SIGNUP,
                AdminViews.TABLE_BLOCK,
                AdminViews.TABLE_DEVELOPER,
                AdminViews.TABLE_USER_ID,
                AdminViews.TABLE_CLAER
            ]:
            raise ValueError("잘못된 key를 입력했습니다.")

    @classmethod
    def _table_rendering_inner(cls, df: pd.DataFrame):
        """
        AgGrid 설정을 구성하고 표를 렌더링한다.

        Returns
        -------
        grid_response : dict-like
            선택된 행 정보 등을 포함.
        """
        gb_option = cls._grid_option(df)
        grid_response = AgGrid(
            df,
            gridOptions=gb_option,
            height=Ratio.ADMIN_TABLE_SIZE,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,    # 필터/정렬 반영한 데이터 반환
            update_mode=GridUpdateMode.SELECTION_CHANGED,           # 선택 변경 시에만 rerun 트리거
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,                               # JsCode 사용 시 필요
            key="users_aggrid"                                      # 키 고정으로 상태 안정
        )
        return grid_response

    @classmethod
    def _grid_option(cls, df: pd.DataFrame) -> GridOptionsBuilder:
        """
        AgGrid 옵션 구성.
        - 멀티선택(체크박스 + 클릭 토글) 활성화
        - getRowId는 문자열 반환으로 안정화
        - (표가 넓어져 idx 숨김은 현재 비활성)
        """
        # Option 구성
        gb = GridOptionsBuilder.from_dataframe(df)
        # 컬럼 넓이 자동 맞춤
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        # 체크박스 보이게 + 행 클릭만으로도 멀티 선택 토글 허용
        gb.configure_selection(
            selection_mode="multiple",
            use_checkbox=True,
            rowMultiSelectWithClick=True
        )
        # 행 클릭 선택 허용 (suppress = False)
        gb.configure_grid_options(
            suppressRowClickSelection=False,
            rowSelection="multiple",
            # getRowId는 문자열 반환이 더 안정적
            getRowId=JsCode("function(params) { return String(params.data.idx); }"),
        )
        # 특정 컬럼 숨기기 (idx는 내부 식별용으로 두고 표시 숨김) - 표가 넓어져서 하지 않음
        if not AdminUserTable:
            gb.configure_column(UsersRecord.idx, hide=True)
        return gb.build()
    
    @classmethod
    def utils(cls, df: pd.DataFrame):
        """
        표 하단 보조 정보(총 행 수, 선택 idx)를 출력.
        """
        # Table 주요 정보 출력
        col1, col2 = st.columns([1, 1])

        # 선택된 index
        selected_idxes = st.session_state.get(AdminUserModify.INDEX_LIST, [])

        with col1:
            st.caption(f"총 행: {len(df):,}")
            st.caption(f"선택 행: {len(selected_idxes):,}")

        with col2:
            st.caption(f"선택 index: {selected_idxes}")
    


# ============================================================
#  사이드바 액션 (승인/정지/삭제/비밀번호변경)
#  - 각 액션은 공통으로: 입력 검증 → API 호출 → after_modify()
# ============================================================
class SideBarAction:
    """
    사이드바 버튼 동작을 담당하는 액션 모음.
    - 입력 무결성 검사(_idxes_handler/_idx_handler/_password_checker)
    - API 호출
    - 결과 Flash 및 테이블 재조회(after_modify)
    """

    @classmethod
    def signup(cls, way: bool):
        """
        선택된 사용자에 대해 승인/승인해제 처리.

        Parameters
        ----------
        way : bool
            True → 승인 / False → 승인해제
        """
        # 선택된 index 정보를 가지고 온다
        idxes, msg = cls._idxes_handler()
        if idxes is None:
            cls.interupt_flash_msg(msg=msg)
            return
        
        # idxes에 대하여 API 통신
        # - idx_dict을 API에서 message로 이미 만들었으므로, 조작안함
        mask, msg, _ = modify_bulk_signup(idxes=idxes, way=way)
        # 수정 후 액션
        cls.after_modify(mask, msg)

    @classmethod
    def block(cls, way: bool):
        """
        선택된 사용자에 대해 정지/복원 처리.

        Parameters
        ----------
        way : bool
            True → 정지 / False → 복원
        """
        # 선택된 index 정보를 가지고 온다
        idxes, msg = cls._idxes_handler()
        if idxes is None:
            cls.interupt_flash_msg(msg=msg)
            return
        
        # idxes에 대하여 API 통신
        # - idx_dict을 API에서 message로 이미 만들었으므로, 조작안함
        mask, msg, _ = modify_bulk_block(idxes=idxes, way=way)
        # 수정 후 액션
        cls.after_modify(mask, msg)

    @classmethod
    def delete(cls):
        """
        선택된 사용자에 대해 '하드 삭제'를 수행.
        - 실제 삭제는 모달에서 최종 확인을 거친 뒤 진행한다.
        - 여기서는 idxes 검증 후 모달을 띄우는 역할만 한다.
        """

        # 선택된 index 정보를 가지고 온다
        idxes, msg = cls._idxes_handler(is_delete=True)
        if idxes is None:
            cls.interupt_flash_msg(msg=msg)
            return
        
        # 확인 모달 실행(모달 내부에서 API 호출/후처리까지 수행)
        delete_confirm_dialog(idxes=idxes)
 
    @classmethod
    def modify_password(cls, new_pwd: str):
        """
        단일 계정의 비밀번호 변경.

        Flow
        ----
        1) 선택 idx가 정확히 1개인지 검사(_idx_handler)
        2) 비밀번호 형식 검사(_password_checker)
        3) API 호출 → Flash → 재조회
        """
        # 선택된 index에 대한 무결성 검사
        t_idx, msg = cls._idx_handler()
        if t_idx is None:
            cls.interupt_flash_msg(msg=msg)
            return
        
        # Password에 대한 형식 확인
        checked_pwd, msg = cls._password_checker(password=new_pwd)
        if checked_pwd is None:
            cls.interupt_flash_msg(msg=msg)
            return 
        
        # idx에 대하여 API 통신
        mask, msg, _ = modify_single_password(idx=t_idx, new_pwd=checked_pwd)

        # Flush에 입력 및 후속 액션
        cls.after_modify(mask=mask, msg=msg)

    # ------------------------------
    # 입력 무결성 검사기
    # ------------------------------
    @classmethod
    def _idxes_handler(
            cls, is_delete: bool = False
        ) -> Tuple[Optional[List[int]], Optional[str]]:
        """
        선택된 다중 idx 리스트의 무결성 검사 및 변환.

        Rules
        -----
        - 최소 1개 이상 선택
        - 관리자 계정이 포함된 경우 거부(AdminUserModify.ADMIN_IDX_LIST)
        - 삭제의 경우: soft-delete(정지) 상태인 계정만 허용 (실수 방지)
        - 모든 idx는 int로 변환되어 반환

        Returns
        -------
        (idxes, msg)
            idxes: 정상 시 int 리스트 / 실패 시 None
            msg:   실패 사유 메시지
        """
        # session에 저장된 index 정보 반환
        idx_list: List[str] =  st.session_state.get(AdminUserModify.INDEX_LIST, [])

        # 비어있거나, 내부에 이상한 값(정수 변환이 안되는)이 있는지 확인
        if len(idx_list) == 0:
            return None, AdminMsg.NO_IDX_ENTER
        
        # 관리자 계정이 포함되어 있는 경우 방어
        admin_idxes = st.session_state.get(AdminUserModify.ADMIN_IDX_LIST)
        if len(set(idx_list) & set(admin_idxes)) > 0:
            return None, AdminMsg.DEFENCE_ADMIN_MODIFY

        # [delete] Hard-delete를 Soft-delete를 하기 전에 하려고 하는지 확인
        if is_delete:
            blocked_idxes = st.session_state.get(AdminUserModify.BLOCK_IDX_LIST)
            # 삭제는 '정지된 사용자'만 허용: 선택된 전체가 BLOCK 목록에 포함되어야 함
            # idx_list와 bloced_idxes의 교집합은 idx_list와 일치해야함
            if set(idx_list) & set(blocked_idxes) != set(idx_list):
                return None, AdminMsg.NOT_BLOCKED_USER_DELETE

        # 위 문제가 다 해결된 경우 정수로 idx를 변환함
        try:
            return [int(i) for i in idx_list], None
        except:
            return None, AdminMsg.WEIRD_IDX_ENTER

    @classmethod
    def _idx_handler(
            cls
        ) -> Tuple[
            Optional[int],  # idx: (int) 정상 출력시 / (None) 비정상 출력시
            Optional[str]   # msg: (None) 정상 출력시 / (str) 비정상 출력시
        ]:
        """
        단일 idx 무결성 검사.
        - 정확히 1개 선택
        - 관리자 계정 방어
        - int 캐스팅 성공

        Returns
        -------
        (idx, msg)
            idx: 정상 시 int / 실패 시 None
            msg: 실패 사유 메시지
        """
        # session에 저장된 index 정보 반환
        idx_list: List[str] =  st.session_state.get(AdminUserModify.INDEX_LIST, [])

        # idx가 하나도 선택되지 않은 경우
        if len(idx_list) == 0:
            return None, AdminMsg.NO_IDX_ENTER

        # idx가 하나인지 확인
        if len(idx_list) != 1:
            return None, AdminMsg.TOO_MUCH_IDX_ENTER
        
        # idx_list 단위에서 idx로 프로세스 진행
        idx_str: str = idx_list[0]

        # 관리자 계정을 선택한 경우 방어
        if idx_str in st.session_state[AdminUserModify.ADMIN_IDX_LIST]:
            return None, AdminMsg.DEFENCE_ADMIN_MODIFY
        
        try:
            return int(idx_str), None
        except:
            return None, AdminMsg.WEIRD_IDX_ENTER

    @classmethod
    def _password_checker(cls, password: str) -> Tuple[Optional[str], Optional[str]]:
        """
        비밀번호 문자열의 기초 무결성/형식 검사.

        Steps
        -----
        1) str 여부 및 strip()
        2) 빈 문자열 방어
        3) Pydantic Password 스키마로 형식 검증

        Returns
        -------
        (pwd, msg)
            pwd: 정상 시 원문 문자열 / 실패 시 None
            msg: 실패 메시지
        """
        # 비밀번호의 문자열 확인 - 앞뒤 공백 제거
        if isinstance(password, str):
            password = password.strip()
        else:
            return None, AdminMsg.WEIRD_PWD_ENTER

        # 비어있는 비밀번호 입력 시
        if not password:
            return None, AdminMsg.NOT_ENTER_PWD
        
        # 비밀번호 형식 확인
        try:
            _PWC = PasswordCheck(pwd=password)
            return _PWC.pwd, None
        except:
            return None, AdminMsg.WRONG_FORMAT_PWD
        
    # ------------------------------
    # 공통 후처리 / 인터럽트 메시지
    # ------------------------------
    @classmethod
    def after_modify(cls, mask: bool, msg: str):
        """
        공통 후처리:
        - Flash 메시지 저장
        - DB 재조회(GetTable.base)
        - 선택 초기화
        - 전체 화면 갱신(st.rerun)
        """
        # 사용자 피드백 - 플래시 저장 (다음 렌더 사이클에 표시)
        if mask is True:
            Flash.push(flash_key=FlashKeys.ADMIN_TABLE, level="success", msg=msg)
        elif mask is False:
            Flash.push(flash_key=FlashKeys.ADMIN_TABLE, level="warning", msg=msg)
        else:
            Flash.push(flash_key=FlashKeys.ADMIN_TABLE, level="error", msg=msg)

        # DB 재조회: ALL 기준으로 DB 재조회 -> 현재 뷰 유지
        GetTable.base()
        # 선택된 idxes 정보 초기화
        st.session_state[AdminUserModify.INDEX_LIST] = []
        # 화면 갱신
        st.rerun()

    @classmethod
    def interupt_flash_msg(cls, msg: str):
        """
        조작 전단계 방어/검증 실패 등으로 액션을 중단할 때,
        사용자에게 경고성 Flash를 남기고 화면을 다시 그린다.
        """
        # 사용자 피드백 - 플래시 저장 (다음 렌더 사이클에 표시)
        Flash.push(flash_key=FlashKeys.ADMIN_TABLE,level="warning", msg=msg)
        # 화면 갱신
        st.rerun()