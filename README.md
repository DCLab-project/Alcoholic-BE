# Alcoholic-BE

## 1. 저장소 목적
이 저장소는 술안주 추천 AI 냉장고 프로젝트의 백엔드 서버를 담당합니다.

현재 백엔드는 아래 역할을 중심으로 구현을 진행하고 있습니다.

- 식재료 재고 조회, 일괄 저장, 수량 수동 조절
- 식재료/주류 실시간 감지 결과 스트리밍(SSE)
- 프론트 UI 테스트를 위한 mock 추천 결과 제공
- 이후 AI, DB, 추천 로직, LLM 연계를 위한 서버 구조 준비

## 2. 현재 구현된 기능
현재 실제로 동작 확인이 끝난 기능은 아래와 같습니다.

### 재고 관리
- `GET /api/v1/inventory`
- `POST /api/v1/inventory/bulk`
- `PATCH /api/v1/inventory/quantity`

### 실시간 스트림(SSE)
- `GET /api/v1/stream/ingredients`
- `GET /api/v1/stream/liquor`
- `GET /api/v1/stream/recommendations`

### 내부 입력용 API
아래 API는 Jetson/AI가 백엔드로 인식 결과를 보내는 내부용 API입니다.
Swagger 문서에는 숨겨져 있습니다.

- `POST /api/v1/recognitions/ingredients`
- `POST /api/v1/recognitions/liquor`

### 추천 API
- `GET /api/v1/recommendations?liquor=soju&refresh=false`

현재 추천 API는 **프론트 UI 테스트를 위한 mock 추천 결과**를 반환합니다.
실제 DB 점수화 로직, Gemini 연계, 추천 고도화는 아직 구현 전입니다.

## 3. 현재 동작 흐름
현재 구현 기준 흐름은 아래와 같습니다.

### 식재료
1. Jetson/AI가 식재료 인식 결과를 내부 API로 전송
2. 백엔드가 식재료 SSE 스트림으로 프론트에 실시간 전달
3. 프론트는 임시 리스트에 표시
4. 사용자가 저장 버튼을 누르면 `inventory/bulk`로 최종 저장

### 주류
1. Jetson/AI가 주류 인식 결과를 내부 API로 전송
2. 백엔드가 `liquor` SSE 스트림으로 주류 이름을 즉시 전달
3. 약간의 지연 후 `recommendation` SSE 스트림으로 추천 결과를 전달

즉 현재 프론트는 **SSE를 구독만 하고 있어도** 술 이름과 추천 결과를 순차적으로 받을 수 있습니다.

## 4. 권장 구조
```text
app/
  api/
    routes/
  config/
  domain/
  repositories/
  schemas/
  services/
```

각 계층 역할은 다음과 같습니다.

- `api/`: 요청/응답 라우팅
- `schemas/`: 요청/응답 스키마, validation
- `services/`: 실제 비즈니스 로직
- `repositories/`: DB 접근
- `domain/`: SQLAlchemy 모델
- `config/`: 설정값 관리

## 5. 실행 방법
### 1. 가상환경 생성
```bash
python -m venv .venv
```

### 2. 가상환경 활성화
Windows PowerShell 기준:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 파일 생성
```powershell
Copy-Item .env.example .env
```

### 5. 서버 실행
로컬 단독 테스트:

```bash
uvicorn app.main:app --reload
```

같은 네트워크의 다른 PC에서 프론트가 붙어야 할 때:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Swagger 문서
서버 실행 후 아래 주소에서 Swagger 문서를 확인할 수 있습니다.

- 로컬: `http://127.0.0.1:8000/docs`
- 같은 네트워크 테스트 시: `http://<내_IP>:8000/docs`

Swagger에는 **프론트가 직접 사용하는 API 중심**으로 문서를 노출합니다.
Jetson/AI 내부 입력용 API는 문서에서 숨깁니다.

## 7. 주요 API 요약
### 상태 확인
- `GET /health`

### 재고 관리
- `GET /api/v1/inventory`
- `POST /api/v1/inventory/bulk`
- `PATCH /api/v1/inventory/quantity`

### 실시간 스트림
- `GET /api/v1/stream/ingredients`
- `GET /api/v1/stream/liquor`
- `GET /api/v1/stream/recommendations`

### 추천
- `GET /api/v1/recommendations?liquor=soju&refresh=false`

### 내부 입력용
- `POST /api/v1/recognitions/ingredients`
- `POST /api/v1/recognitions/liquor`

## 8. 데이터 저장 관련
현재 기본 설정은 빠른 개발을 위해 SQLite를 사용합니다.

- 기본값: `sqlite:///./alcoholic.db`

향후 팀 기준 운영 흐름에 맞춰 MySQL로 전환할 예정입니다.
현재 코드 구조는 SQLAlchemy 계층을 분리해 두었기 때문에 MySQL 전환이 가능하도록 작성되어 있습니다.

## 9. 현재 mock 상태인 부분
아래는 아직 실제 구현이 아니라 테스트용 mock 또는 임시 흐름입니다.

- 추천 결과 3종
- 추천 이유
- 레시피 단계
- 부족 재료 목록
- 주류 인식 후 추천 결과 자동 전달 흐름의 세부 정책

즉 현재 추천 파트는 **프론트 UI와 통신 흐름 검증용**입니다.

## 10. 다음 개발 우선순위
다음 우선순위는 아래와 같습니다.

1. CORS 설정 추가
2. MySQL 전환
3. 재고/이벤트 구조 안정화
4. 추천 로직 DB 우선 + 점수화 구조 반영
5. Gemini structured output 연계
6. Jetson 실제 추론 결과와 완전 연동

## 11. 주의 사항
- 현재 카메라/AI 인식 결과는 영어 key 기준으로 통일합니다.
  - 예: `green_onion`, `onion`, `soju`
- 프론트 화면 표시 한글은 FE에서 매핑하는 방식을 권장합니다.
- raw 데이터, 체크포인트, 로그, 산출물은 Git에 올리지 않습니다.
