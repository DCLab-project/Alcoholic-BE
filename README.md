# Alcoholic-BE

## 운영 준비 문서
FE 연동 확인 이후 가상환경 정리, DB 초기화, MySQL 전환, seed 확장 절차는 아래 문서에 정리합니다.

- `docs/operations_readiness.md`
- `scripts/initialize_database.py`

## 1. 저장소 목적
이 저장소는 술안주 추천 AI 냉장고 프로젝트의 백엔드 서버를 담당합니다.

현재 백엔드는 프론트와 AI/Jetson 사이의 연결 지점을 먼저 안정적으로 만드는 데 초점을 두고 있습니다.
즉, 지금 단계의 목표는 다음 3가지를 실제로 동작시키는 것입니다.

- 재고 저장, 조회, 수량 조절
- 식재료 / 주류 실시간 SSE 스트림
- 주류 인식 후 추천 결과 전달 흐름

## 2. 현재 구현된 기능

### 재고 관리 API
- `GET /api/v1/inventory`
- `POST /api/v1/inventory/bulk`
- `PATCH /api/v1/inventory/quantity`

### 실시간 스트림 API
- `GET /api/v1/stream/ingredients`
- `GET /api/v1/stream/liquor`
- `GET /api/v1/stream/recommendations`

### 주류 수동 스캔 요청 API
- `POST /api/v1/scan/liquor/start`

### 추천 API
- `GET /api/v1/recommendations?liquor=soju&refresh=false`

### 내부 입력용 API
아래 API는 Jetson/AI가 백엔드로 인식 결과를 넣을 때 사용하는 내부용 API입니다.
프론트 Swagger 문서에서는 숨겨져 있습니다.

- `POST /api/v1/recognitions/ingredients`
- `POST /api/v1/recognitions/liquor`

## 3. 현재 추천 시스템 구조
현재 추천은 더 이상 단순 하드코딩 리스트만 반환하지 않습니다.
아래 구조로 동작합니다.

1. seed 레시피 데이터를 DB에 적재
2. 현재 재고(`inventory_items`) 조회
3. 주류별 후보 레시피 조회
4. 현재 재고 기준으로 부족 재료 계산
5. 재고 매칭 점수와 기본 페어링 점수로 상위 3개 추천 반환

즉 현재 추천은 **DB seed + 재고 기반 점수화 추천의 첫 버전**입니다.
실시간 LLM이 매번 새 레시피를 만드는 구조가 아니라, 검수된 seed 후보 중 현재 상황에 가장 잘 맞는 안주를 고르는 방식입니다.

Gemini / LLM은 기본 추천 경로가 아니라 **보조 fallback**으로 사용합니다.
`GET /api/v1/recommendations` 호출 시 `llm_fallback=true`를 보내면 BE가 먼저 검수된 seed DB에서 추천을 찾고, 필터 조건 때문에 추천이 3개보다 적을 때 부족한 개수만 Gemini로 생성합니다.
Gemini 응답은 바로 반환하지 않고 JSON schema, 허용 식재료 key, 부족 재료 계산, 조리 단계 수를 다시 검증한 뒤 통과한 항목만 응답에 포함합니다.
Gemini 호출 실패 또는 검증 실패 시에는 기존 seed 추천 결과만 반환합니다.

아직 아래는 구현 전입니다.

- 운영 중 Gemini 생성 레시피 영구 저장
- 추천 히스토리 저장

## 4. 레시피 seed 데이터
현재 추천 후보 레시피 seed 데이터는 아래 파일에 들어 있습니다.

- `seeds/recommendations.json`

이 파일은 LLM이나 사람이 만든 후보 레시피를 검수한 뒤 넣는 기본 레시피 DB입니다.
추천 지식 설계 원칙, seed 선정 기준, 점수 정책은 아래 문서에 정리합니다.

- `docs/recommendation_knowledge.md`
- `docs/recommendation_policy.md`

현재는 아래 7개 주류에 대해 각 30개씩, 총 210개 seed가 들어 있습니다.

- `soju`
- `beer`
- `red_wine`
- `white_wine`
- `sparkling_wine`
- `whisky`
- `sake`

각 레시피에는 아래 정보가 저장됩니다.

- 추천 대상 주류
- 추천 이름
- 추천 이유
- 기준 인분 수
- 예상 조리 시간
- 조리 난이도
- 정량화된 재료 목록
- 상온 기본 양념 목록
- 단계별 조리 순서
- 조리 팁
- refresh용 보조 세트 구분값

추천 점수는 아래 공식으로 계산합니다.

```text
total_score = available_ingredient_count * 3
            - missing_ingredient_count * 2
            + rank_hint
```

즉 기본 페어링 점수(`rank_hint`)가 높아도, 현재 냉장고에 재료가 거의 없으면 우선순위가 내려갑니다.
반대로 지금 재고로 바로 만들 수 있는 안주는 더 위로 올라옵니다.

seed를 다시 생성하거나 정리할 때는 아래 스크립트를 사용합니다.

- `scripts/build_recommendation_seeds.py`
- `scripts/polish_recommendation_seeds.py`

seed 레시피를 사람이 한 번에 검수하기 좋은 문서로 내보내려면 아래 스크립트를 사용합니다.

- `scripts/export_recipe_catalog.py`

생성 파일:

- `docs/recipe_catalog.md`

이 문서에는 술별 레시피 수, 추천 이유, 핵심 재료, 상온 양념, 조리 순서, 팁이 정리되어 있어 육안 검수에 바로 사용할 수 있습니다.

로컬 FE 테스트용으로 냉장고 재고를 넉넉하게 채우고 싶을 때는 아래 스크립트를 사용합니다.

- `scripts/seed_demo_inventory.py`

이 스크립트는 현재 추천 후보와 식재료 클래스를 기준으로 로컬 SQLite 재고를 한 번에 채웁니다.

## 5. 현재 동작 흐름

### 식재료 인식 흐름
1. Jetson/AI가 식재료 인식 결과를 내부 API로 전송
2. 백엔드가 `ingredient` SSE를 발행
3. 프론트는 임시 리스트 UI에 식재료를 쌓음
4. 사용자가 저장 버튼을 누르면 `inventory/bulk`로 최종 저장

### 자동 주류 인식 흐름
1. Jetson/AI가 주류 인식 결과를 내부 API로 전송
2. 백엔드가 `liquor` SSE를 먼저 발행
3. 그 뒤 추천 로직이 실행됨
4. 추천 결과가 준비되면 `recommendation` SSE를 발행

### 수동 주류 스캔 fallback 흐름
1. 프론트가 `POST /api/v1/scan/liquor/start` 호출
2. 백엔드가 `accepted`와 `scan_request_id`를 먼저 반환
3. mock 수동 스캔 흐름이 약 3초 뒤 `soju`를 인식한 것으로 처리
4. `liquor` SSE를 발행
5. 이후 추천 로직을 실행하고 `recommendation` SSE를 발행

즉 현재 프론트는 자동 인식 실패 시에도 버튼 기반 fallback UI를 먼저 테스트할 수 있습니다.

## 6. 추천 응답 형식
현재 프론트와 맞춰진 추천 응답 형식은 아래와 같습니다.

```json
{
  "liquor": "소주",
  "recommendations": [
    {
      "name": "대파 삼겹살 볶음",
      "reason": "소주의 알싸한 맛과 기름진 돼지고기 풍미가 잘 맞고, 대파가 느끼함을 깔끔하게 눌러줍니다.",
      "priority_rank": 1,
      "priority_reason": "현재 재고만으로 바로 조리할 수 있으며 페어링 기본 점수도 높아 1순위로 선정했습니다.",
      "selection_factors": [
        "핵심 재료 3개 중 3개를 현재 재고로 바로 활용할 수 있습니다.",
        "추가 장보기 없이 바로 조리 가능한 레시피입니다.",
        "기본 주류 페어링 우선순위가 매우 높은 레시피입니다."
      ],
      "score_breakdown": {
        "available_ingredient_count": 3,
        "missing_ingredient_count": 0,
        "rank_hint": 95,
        "total_score": 104
      },
      "servings": 1,
      "cook_time_minutes": 15,
      "difficulty": "easy",
      "ingredient_yes": ["대파", "상추"],
      "ingredient_no": ["돼지고기", "마늘"],
      "ingredient_details": [
        {
          "item_name": "green_onion",
          "display_name": "대파",
          "amount": 1,
          "unit": "대",
          "status": "available"
        },
        {
          "item_name": "pork",
          "display_name": "돼지고기",
          "amount": 180,
          "unit": "g",
          "status": "missing"
        }
      ],
      "pantry_items": [
        "식용유 1큰술",
        "소금 약간",
        "후추 약간"
      ],
      "recipe": [
        "1: 대파 1대는 4~5cm 길이로 썬다, 돼지고기 180g은 한입 크기로 손질한다, 마늘 2쪽은 편썬다.",
        "2: 팬에 기름을 두르고 돼지고기 180g을 먼저 2~3분 볶는다.",
        "3: 대파, 마늘을 넣고 1~2분 더 볶아 간을 맞춘다.",
        "4: 대파 삼겹살 볶음은 센 불에서 빠르게 마무리해 낸다."
      ],
      "missing_ingredients": ["돼지고기", "마늘"],
      "tip": "볶음류는 센 불에서 짧게 끝내야 재료 식감이 살아 있고 물이 덜 생깁니다."
    }
  ]
}
```

이 구조 덕분에 프론트는 아래 UI를 바로 구성할 수 있습니다.

- 추천 카드 3개
- 추천 이유 표시
- 추천 우선순위 설명
- 추천 선택 요인 표시
- 조리 시간 / 난이도 표시
- 재료 체크리스트 UI
- 상온 기본 양념 안내
- 조리 순서 펼침 UI
- 부족 재료 표시
- 상세 레시피 모달 또는 상세 페이지

## 7. 권장 구조
```text
app/
  api/
    routes/
  config/
  domain/
  repositories/
  schemas/
  services/
  seeds/
seeds/
  recommendations.json
```

역할은 아래처럼 나누고 있습니다.

- `api/`: FastAPI 라우트
- `schemas/`: 요청/응답 스키마
- `services/`: 비즈니스 로직
- `repositories/`: DB 접근
- `domain/`: SQLAlchemy 모델
- `app/seeds/`: seed 적재 코드
- `seeds/`: 레시피 seed 원본 데이터

## 8. 실행 방법

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

추천 API는 기본값 기준으로 인위적인 지연 없이 바로 응답합니다.
로컬 데모에서 로딩 상태를 일부러 보여주고 싶을 때만 `.env`에서 아래 값을 초 단위로 조절합니다.

```env
RECOMMENDATION_RESPONSE_DELAY_SECONDS=0
```

### 5. 서버 실행
로컬 테스트:

```bash
uvicorn app.main:app --reload
```

같은 네트워크의 다른 PC에서 프론트가 붙을 때:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 9. Swagger 문서
서버 실행 후 아래 주소에서 Swagger 문서를 확인할 수 있습니다.

- 로컬: `http://127.0.0.1:8000/docs`
- 같은 네트워크 테스트: `http://<내_IP>:8000/docs`

Swagger에는 **프론트가 직접 사용하는 API 중심**으로 문서가 보이도록 정리해두었습니다.
Jetson/AI 내부 입력용 API는 문서에서 숨겨져 있습니다.

## 10. 데이터베이스
현재 기본 설정은 SQLite입니다.

- 기본값: `sqlite:///./alcoholic.db`

즉 지금은 빠른 개발과 프론트 연동 테스트를 위해 파일 DB를 사용합니다.
이후 팀 기준 구조에 맞춰 MySQL로 전환할 예정입니다.

현재 코드는 SQLAlchemy 계층을 분리해두었기 때문에, 다음 단계에서 MySQL 전환이 가능하도록 준비돼 있습니다.

## 11. 현재 구현 상태에서 정직하게 말할 것
현재 구현은 “기초 통합 테스트가 되는 상태”입니다.

이미 되는 것:
- 재고 조회 / 일괄 저장 / 수량 조절
- 식재료 SSE
- 주류 SSE
- 추천 SSE
- 수동 주류 스캔 fallback
- 로컬 FE(CORS) 연동
- seed DB 기반 추천 3개 반환

아직 안 된 것:
- 실제 Gemini / LLM 추천 생성
- 실제 Jetson 모델 실행을 통한 수동 스캔
- 대규모 레시피 DB 자동 구축
- 추천 결과 이력 저장
- MySQL 전환

## 12. 다음 우선순위
다음 개발 우선순위는 아래와 같습니다.

1. MySQL 전환
2. 레시피 후보 DB 확장
3. LLM으로 레시피 후보 대량 생성 후 seed 정리
4. Gemini structured output 연계
5. 상세 레시피 전용 FE 화면/모달 연동
6. Jetson 실제 인식 결과 연동

## 13. 주의 사항
- 내부 key는 영어 기준으로 통일합니다.
  - 예: `green_onion`, `onion`, `soju`
- 프론트 화면 표시는 필요할 때 별도 한글 매핑으로 처리하는 방식을 권장합니다.
- 추천 이유(`reason`)와 조리 순서(`recipe`)는 DB seed에 포함되며, 사용자가 확인할 수 있도록 응답에서 유지합니다.
