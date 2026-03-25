from app.constants.keys import SessionKey, LoginViews, PageNum, PageKey


DEFAULT_SESSION = {
    # Login 관련 정보 초기화
    SessionKey.LOGGED_IN: False,
    SessionKey.ID: None,
    SessionKey.USER_NAME: None,
    SessionKey.KTR_ID: None,
    SessionKey.EMAIL: None,

    # 권한 정보
    SessionKey.IS_DEVELOPER: None,
    SessionKey.IS_ADMIN: None,

    # 채팅 및 스트리밍 상태
    SessionKey.MESSAGE: [],
    SessionKey.STREAMING: False,
    SessionKey.STOP_STREAM: False,
    SessionKey.TEMP_RESPONSE: "",

    # View 초기화
    LoginViews.KEY: LoginViews.LOGIN_BEFORE,

    # 페이지 상태
    PageKey.CURRENT_PAGE: PageKey.P_KEY_DICT[PageNum.LOGIN]
}