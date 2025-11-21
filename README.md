# KHA 프론트엔드 (Streamlit)
FastAPI 백엔드와 연동되는 KHA 알파 버전의 Streamlit 멀티페이지 앱입니다. 로그인/채팅/관리자 기능을 제공하며, 일부 연구 기능 페이지는 스켈레톤 상태로 남겨두었습니다.

- **주요 기술**: Python, Streamlit, requests, pandas, st-aggrid, pydantic
- **백엔드 연동**: GPU 웹(LLM)·WEB(계정/관리) API 엔드포인트는 `app/core/config.py`, `app/constants/api_urls.py`에 정의
- **사내 패키지 의존성**: `bedrock_core`, `kha` 모듈을 사용합니다(사내 패키지 설치 필요).

---

<br>

## 폴더 구조
```text
.
├── Main.py                  # Streamlit 진입점
├── README.md                # 기존 문서(보존)
├── README_new.md            # 신규 작성 문서(본 파일)
├── app/
│   ├── core/config.py       # 백엔드 URL/버전, 보호 스위치
│   ├── constants/           # 키, 메시지, 경로, API URL, 상수
│   ├── api/                 # 로그인/채팅/관리자 API 클라이언트
│   ├── routes/              # 페이지별 UI 구성 로직
│   ├── schemas/             # pydantic 스키마
│   └── utils/               # 세션/채팅/관리자 테이블/공용 유틸
├── pages/                   # Streamlit 멀티페이지 엔트리
│   ├── 1_Login.py
│   ├── 2_KHA_chat.py
│   ├── 3_FloraGenesis.py    # TODO placeholder
│   ├── 4_PANCDR.py          # TODO placeholder
│   ├── 5_Dashboard.py       # TODO placeholder
│   └── 9_Admin.py
└── src/
    ├── KTR-icon.ico         # 파비콘
    └── test_db.json         # 프로토타입용 로컬 DB
```


---

<br>

## 페이지/기능 개요
- **메인(Main.py)**  
  공통 UI 설정(`basic_ui`), 서비스 소개, 세션 초기화(`init_session`), 모델 목록 초기 로드(`InitModelInfo.run`).

- **로그인(Login)** (`pages/1_Login.py`)  
  - 로그인/회원가입/개인정보 동의/비밀번호 분실/계정 정지 뷰 전환(`LoginViews`).  
  - 회원가입 시 `SignUpUniqueKeys`로 ID·사번·이메일 중복 검사 → `verify_unique_key` API 호출.  
  - `SignUpAction`이 입력 검증 후 `add_new_user` 호출, 개인정보 미동의 방지.  
  - 로그인 후에는 `AfterLogin`, 정보 수정(`EditAction`+`self_update`), 계정 정지(`SoftDeleteAction`+`self_block`) 제공.

- **채팅(Chat)** (`pages/2_KHA_chat.py`, `app/routes/utils`)  
  - 모델 목록/기본 모델은 10분 캐시(`st.cache_data`).  
  - 사이드바에서 모델 선택, 대화 초기화.  
  - `Response`가 마지막 사용자 메시지를 `streaming_response`로 전송해 SSE 스트림을 `st.write_stream`으로 표시, 완료 후 세션에 저장.

- **연구 기능 Placeholder**  
  - FloraGenesis, PANCDR, Dashboard는 현재 `TODO` 문구만 노출.

- **관리자(Admin)** (`pages/9_Admin.py`, `app/routes/utils`)  
  - 비관리자 접근 시 차단 안내.  
  - `st_aggrid` 기반 사용자 테이블 조회/필터링: 전체, 승인 대기, 정지, 개발자, 단일 ID.  
  - 일괄 승인/승인 해제/정지/정지 해제/하드 삭제(스위치에 따라 차단 가능), 단일 비밀번호 초기화.  
  - `UserTable`이 백엔드 응답을 pandas DataFrame으로 전처리하고, 경과 시간·권한 파생 컬럼 및 방어용 인덱스 저장.

---

## 개발 시 참고
- **세션 초기화**: 각 페이지 진입 시 `init_session()`과 `InitModelInfo.run()`을 호출해 로그인 상태/모델 정보를 준비합니다. `SessionKey`, `LoginViews`, `AdminViews`는 `app/constants/keys.py`에 정의되어 있습니다.
- **API 통신 패턴**: `bedrock_core.data.api.APIResponseHandler`를 통해 공통 예외/파싱을 처리하고, `Status200` 클래스가 엔드포인트별 정상 응답을 검증합니다.
- **모델 선택 상태**: 선택된 모델명과 인덱스는 세션에 저장되며, 사이트 전역에서 공유됩니다.
- **플래시 메시지**: `app/utils/utils.py`의 `Flash` 유틸을 통해 일시적 안내/경고를 노출합니다.
- **하드 삭제 방지**: `app/core/config.py`의 `KILL_HARD_DELETE_SWITCH`를 True로 두면 관리자 페이지에서 하드 삭제 버튼을 무력화할 수 있습니다.

---

## 빠른 문제 해결 체크리스트
- 백엔드 연결 오류: `app/core/config.py` URL/포트, 방화벽/포트포워딩, 백엔드 서버 기동 여부 확인.
- 모델 목록이 비어있음: GPU 백엔드의 `/base/model_list` 응답 확인, 캐시(`st.cache_data`) 초기화를 위해 Streamlit 재기동.
- 관리자 테이블이 비어있음: `GET /admin/search_all` 응답 구조가 `App.schemas.p9_admin`와 일치하는지 확인.
- 로그인/회원가입 입력 실패: `app/schemas/p1_login.py`에 정의된 패턴(아이디/비밀번호/이메일)을 따른 값인지 검증.


---

<br>

## 실행 방법
* 기본 실행 방법
```bash
streamlit run Main.py
```

<br>

### 내부망 사용자들을 위한 네트워크 연결
* 개요
> * wsl 환경
> * 동일 네트워크 내 사내 이용자들만 사용
> * 해당 환경 고려하여, 동일 내 이용자들이 사용할 수 있도록 포트 개방

<br>

### 단계별 설정 방법
#### A. Streamlit 웹서버 실행

```bash
streamlit run Main.py --server.address=0.0.0.0
```
  * WSL 내부의 8501번 포트를 모든 IP 주소에 대해 개방

<br>

#### B. WSL 포트 포워딩 설정
  * WSL의 8501 포트를 Windows 호스트로 전달 [Windows PowerShell에서 수행]

1. WSL의 IP 주소 확인
    * `hostname -I` 등으로 현재 IP 주소 확인
2. 포트 포워딩 규칙 추가 (Power Shell)
    * PowerShell을 관리자 권한으로 실행 후, 아래 명령어를 입력하여 포트 포워딩 규칙을 추가합니다.

```powershell
# listenaddress=0.0.0.0 : Windows의 모든 IP에서 8501 포트를 수신
# connectaddress=[WSL IP] : 위에서 확인한 WSL의 IP 주소로 전달
# 예시: netsh interface portproxy add v4tov4 listenport=8501 listenaddress=0.0.0.0 connectport=8501 connectaddress=172.21.48.118

netsh interface portproxy add v4tov4 listenport=8501 listenaddress=0.0.0.0 connectport=8501 connectaddress=[WSL IP 주소]
```

* 포트 포워딩 규칙은 영구적으로 적용 됨.
    * 위에서 추가한 `netsh` 포트 포워딩 규칙은 한 번 설정 시, PC를 재부팅해도 계속 유지
    * 나중에 이 규칙이 왜 있는지 헷갈릴 수 있으므로, 확인 및 삭제 방법을 알면 좋음

```powershell
# 모든 포트 포워딩 규칙 확인
netsh interface portproxy show all

# 설정한 규칙 삭제 (더 이상 사용하지 않을 경우 - 0.0.0.0:8501 에 대한 규칙 제거)
netsh interface portproxy delete v4tov4 listenport=8501 listenaddress=0.0.0.0
```

<br>

#### C. Windows 방화벽 인바운드 규칙 추가
* 외부 기기들이 Windows의 8501번 포트에 접속할 수 있도록 Windows 방화벽 개방
   1. Windows 검색에서 "고급 보안이 포함된 Windows Defender 방화벽"을 검색하여 실행합니다.
   2. 왼쪽 패널에서 인바운드 규칙을 선택합니다.
   3. 오른쪽 작업 패널에서 새 규칙...을 클릭합니다.
   4. 규칙 종류에서 포트를 선택하고 다음을 클릭합니다.
   5. 프로토콜 및 포트에서 TCP를 선택하고, 특정 로컬 포트에 8501을 입력한 후 다음을 클릭합니다.
   6. 작업에서 연결 허용을 선택하고 다음을 클릭합니다.
   7. 프로필에서 개인과 공용을 모두 체크하고 다음을 클릭합니다. (보안이 중요하다면 '개인'만 체크하여 같은 사설망에서만 허용할 수 있습니다.)
   8. 이름에 "Streamlit WSL"과 같이 식별하기 쉬운 이름을 입력하고 마침을 클릭합니다.

<br>

#### C.1. Windows 네트워크 설정 확인
1. 현재 네트워크 프로필 확인하기

    * Win 키 + I를 눌러 Windows 설정을 엽니다.
    * 네트워크 및 인터넷으로 이동합니다.
    * 현재 연결된 네트워크(Wi-Fi 또는 이더넷)의 속성을 클릭합니다.
    * 네트워크 프로필 섹션에서 '공용'과 '개인' 중 어떤 것에 체크되어 있는지 확인합니다.

2. 네트워크 프로필 변경하기

    * 만약 위 화면에서 '공용'으로 설정되어 있다면, '개인'으로 변경해 주세요.
    * 이 설정을 '개인'으로 바꾸는 순간, 이전에 만드셨던 '개인' 프로필용 방화벽 규칙이 활성화되면서 다른 PC에서도 접속이 가능해질 것입니다.

<br>

#### D. 외부에서 접속
* Windows의 IP 주소 확인
    * CMD 또는 PowerShell에서 `ipconfig` 명령어를 실행하여 Windows PC의 IPv4 주소 확인
* 동일 네트워크 내 다른 장비로 접속
    * `http://[Windows IP 주소]:8501`