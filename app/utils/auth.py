"""
사용자 인증 관련 유틸리티.

- 프로토타입 단계에서는 test_db.json을 간이 DB로 사용하여 사용자 정보 로드 및 검증 수행.
"""
from typing import Tuple, Optional, List, Dict, Any
import json
import streamlit as st

from app.schema.pathes import DB_PATH
from app.schema.keys import LoginKey


@st.cache_data
def load_test_db() -> List[Dict[str, Any]]:
    """
    test_db.json에서 사용자 목록 로드.

    - 캐싱(@st.cache_data)으로 불필요한 파일 I/O 방지.
    - 파일이 없거나 JSON이 잘못되면 오류 메시지 출력 후 빈 리스트 반환.

    Returns:
        List[Dict[str, Any]]: 사용자 정보 딕셔너리 목록.
    """
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)[LoginKey.USER]
    except FileNotFoundError:
        st.error(f"Error: {DB_PATH} 파일을 찾을 수 없습니다.")
        return []
    except json.JSONDecodeError:
        st.error(f"Error: {DB_PATH} 파일의 JSON 형식이 올바르지 않습니다.")
        return []
    

def verify_user(
        id: str, 
        passwd: str
    ) -> Tuple[bool, Optional[str]]:
    """
    입력 ID와 비밀번호를 test_db.json의 정보와 비교.

    Args:
        id (str): 입력한 ID.
        passwd (str): 입력한 비밀번호.

    Returns:
        Tuple[bool, Optional[str]]:
            - 성공: (True, role)
            - 실패: (False, None)
    """
    users = load_test_db()
    for user in users:
        if user[LoginKey.ID] == id and user[LoginKey.PASSWD] == passwd:
            return True, user[LoginKey.ROLE]
    return False, None