from typing import Final, Tuple



# API TIME OUT
API_TIMEOUT = (
    3.0,                # Connect timeout
    5.0                 # Read timeout
)


class Role:
    
    DEVELOPER: Final[str] = "developer"
    ADMIN: Final[str] = "admin"



class Ratio:
    # 로그인 View에서 text_bar, btn의 크기 비율
    LOGIN_BAR_N_BTN: Final[Tuple[int, int]] = [3, 1]


