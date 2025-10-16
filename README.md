# 프론트엔드 웹서버 - 프로토타입 버전
* Streamlit 기반의 알파 테스트용 프론트엔드.  
* FastAPI 백엔드와 연동되어 로그인/채팅/대시보드 기능을 제공합니다.
> * FastAPI 백엔드는 실제 서비스 단계를 고려합니다.

---

<br>
<br>

# 1. 개요

## A. 프론트엔드 웹서버 역할
* 해당 프론트엔드 웹서버는 MVP(Minimum Viable Product)를 지향합니다
    * Streamlit 기반 페이지 경량화를 목표로 개발됩니다
    * FastAPI 백엔드 API와 통신합니다.
    
* 주요 기능
    1. 로그인 : 사용자 인증 및 상태 유지 - 사용자별 대화 내용 유지
    2. 채팅 : 백엔드 LLM 응답 연동 UI
    3. 데시보드 : 통계 및 주요 지표 시각화
    4. 관리자 페이지 : 사용자 관리 및 로그 확인

* 제외 기능
    1. ORM 기반 로그인 : test_db.json 대신 사용
    2. 프론트엔드 웹서버 보안 기능

## B. 백엔드 웹서버 역할
* 백엔드 웹서버는 LLM 연산 (RAG, MCP 사용 시, DB I/O까지)만 고려합니다
    * 백엔드 웹서버의 LLM 연산은 프론트엔드 웹서버를 통해서만 실행할 수 있습니다

* 보안 기능
    1. 프론트엔드 웹서버와 API 통신만을 이용한 데이터 통신
    2. "API 키"를 입력해야만 API 사용 가능

---

<br>
<br>

# 2. 구조
```text
kha_frontend/
│
├── main.py                     # Streamlit 앱의 메인 진입점
├── README.md                   # 프로젝트 개요 및 사용법 설명서
│
├── app/                        # 프론트엔드의 주요 로직을 담는 소스 디렉토리
│   ├── core/
│   │   ├── api.py              # 백엔드 서버와 통신하는 API 함수 모음
│   │   └── config.py           # API 주소 등 핵심 설정값
│   │
│   ├── routes/
│   │   ├── common.py           # 여러 페이지에서 공통으로 사용하는 UI 컴포넌트
│   │   ├── main.py             # 메인 페이지에 표시될 정적 텍스트
│   │   ├── p1_login.py         # 로그인 페이지의 UI 및 이벤트 처리 로직
│   │   └── p2_chat.py          # 채팅 페이지의 UI 및 이벤트 처리 로직
│   │
│   ├── schema/
│   │   ├── keys.py             # 세션, API 등에서 사용하는 상수 키(key)
│   │   └── pathes.py           # 파일, 페이지 경로 등 상수
│   │
│   └── utils/
│       ├── auth.py             # 사용자 인증(로그인/로그아웃) 관련 함수
│       ├── chat.py             # 채팅 응답 스트리밍 처리 등 채팅 관련 함수
│       └── session.py          # Streamlit 세션 상태 관리 함수
│
├── pages/                      # Streamlit 멀티페이지 앱의 각 페이지
│   ├── 1_login.py              # 로그인 페이지
│   ├── 2_chat.py               # 채팅 페이지
│   ├── 3_dashboard.py          # 대시보드 페이지
│   └── 4_admin.py              # 관리자 페이지
│
└── src/                        # 리소스 파일 (이미지, 데이터 등)
    ├── KTR-icon.ico            # 애플리케이션 아이콘(파비콘)
    └── test_db.json            # 프로토타입용 로컬 사용자 DB
```

---

<br>
<br>

# 3. 실행 방법
* 기본 실행 방법
```bash
streamlit run Main.py
```

<br>

## 3.1. 내부망 사용자들을 위한 네트워크 연결
* 개요
> * wsl 환경
> * 동일 네트워크 내 사내 이용자들만 사용
> * 해당 환경 고려하여, 동일 내 이용자들이 사용할 수 있도록 포트 개방

<br>

### 3.1.1. 단계별 설정 방법
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
    * CMD 또는 PowerShell에서 `ipconfig` 명령어를 실해앟여 Windows PC의 IPv4 주소 확인
* 동일 네트워크 내 다른 장비로 접속
    * `http://[Windows IP 주소]:8501`