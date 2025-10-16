def string_space_converter(value: str) -> str:
    """
    문자열 내 존재하는 공백을 "_" 로 변환한다.
    대상이 문자열이 아닌 경우, 그대로 반환한다

    Args:
        value (str): 대상 문자열 (해당 코드는 문자열을 대상으로 하는 경우)

    Returns:
        str: 공백이 "_"로 변경된 문자열
    """
    if isinstance(value, str):
        # value 앞, 뒤 공백 제거
        value = value.strip()
        # value가 빈 문자열이 아닌 경우, 공백을 _로 변경
        if value != "":
            return value.replace(" ", "_")
        else:
            return value
    return value