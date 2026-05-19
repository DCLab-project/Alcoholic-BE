# FE API Contract

이 문서는 프론트엔드가 직접 호출하는 BE API 계약만 정리합니다.
BE와 AI 모듈 사이의 내부 API 명세는 이 문서에 포함하지 않습니다.

## 공통

- Local Base URL: `http://127.0.0.1:8000`
- 날짜/시간: ISO 8601 문자열
- 인증: MVP 단계에서는 없음
- 추천 주류 key: `soju`, `beer`, `red_wine`, `white_wine`, `sparkling_wine`, `whisky`, `sake`
- 추천 응답에서 기존 필드 `name`, `reason`, `ingredient_yes`, `ingredient_no`, `recipe`, `missing_ingredients`는 계속 유지합니다.

## 식재료 Key

FE가 식재료 key를 직접 다룰 때는 아래 30개 기준을 사용합니다.

| key | display |
| --- | --- |
| `beef` | 소고기 |
| `bread` | 빵 |
| `broccoli` | 브로콜리 |
| `butter` | 버터 |
| `cabbage` | 양배추 |
| `carrot` | 당근 |
| `cheese` | 치즈 |
| `chicken` | 닭고기 |
| `cucumber` | 오이 |
| `egg` | 달걀 |
| `eggplant` | 가지 |
| `fish` | 생선살 |
| `garlic` | 마늘 |
| `leek` | 대파 |
| `lettuce` | 상추 |
| `milk` | 우유 |
| `mushroom` | 버섯 |
| `onion` | 양파 |
| `pepper` | 파프리카 |
| `pork` | 돼지고기 |
| `potato` | 감자 |
| `sausage` | 소시지 |
| `tomato` | 토마토 |
| `zucchini` | 애호박 |
| `lemon` | 레몬 |
| `avocado` | 아보카도 |
| `radish` | 무 |
| `tofu` | 두부 |
| `ginger` | 생강 |
| `salmon` | 연어 |

주의:

- `pepper`는 고추가 아니라 파프리카입니다.
- 기존 `green_onion` 입력은 레거시 호환용으로 받을 수 있지만, 신규 기준에서는 `leek`를 대파 key로 사용합니다.
- `fish`는 일반 생선살, `salmon`은 연어입니다.

## Endpoints

| Method | Path | FE 용도 |
| --- | --- | --- |
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/api/v1/inventory` | 저장된 냉장고 식재료 조회 |
| `POST` | `/api/v1/inventory/bulk` | 스캔 결과를 사용자 확인 후 일괄 저장 |
| `POST` | `/api/v1/inventory` | 식재료 직접 추가 |
| `PATCH` | `/api/v1/inventory/quantity` | 식재료 수량 +1/-1 |
| `PATCH` | `/api/v1/inventory/{ingredient_name}` | 식재료 이름 또는 수량 직접 수정 |
| `DELETE` | `/api/v1/inventory/{ingredient_name}` | 식재료 삭제 |
| `POST` | `/api/v1/scan/ingredients/start` | 식재료 스캔 시작 |
| `POST` | `/api/v1/scan/liquor/start` | 주류 스캔 시작 |
| `GET` | `/api/v1/stream/ingredients` | 식재료 인식 SSE 구독 |
| `GET` | `/api/v1/stream/liquor` | 주류 인식 SSE 구독 |
| `GET` | `/api/v1/stream/sensors` | Jetson-Arduino 센서 상태 SSE 구독 |
| `GET` | `/api/v1/recommendations` | 주류 기준 안주 추천 조회 |
| `POST` | `/api/v1/recommendations/refresh` | 고정 추천 제외 재추천 |
| `POST` | `/api/v1/favorite-recipes` | 즐겨찾기 레시피 저장 |
| `GET` | `/api/v1/favorite-recipes` | 즐겨찾기 레시피 목록 조회 |
| `GET` | `/api/v1/favorite-recipes/{favorite_id}` | 즐겨찾기 레시피 상세 조회 |
| `DELETE` | `/api/v1/favorite-recipes/{favorite_id}` | 즐겨찾기 레시피 삭제 |

## Scan And SSE

스캔 시작 API는 요청 접수만 담당합니다. 실제 인식 결과는 SSE로 내려오며, FE는 `scan_request_id`로 요청과 결과를 연결할 수 있습니다.

### POST `/api/v1/scan/ingredients/start`

Request:

```json
{
  "triggered_by": "frontend",
  "device_id": "display-01"
}
```

Response:

```json
{
  "status": "accepted",
  "message": "식재료 스캔을 시작했습니다.",
  "scan_request_id": "ingredient-scan-001"
}
```

### GET `/api/v1/stream/ingredients`

SSE event:

```text
event: ingredient
data: {"ingredient_name":"대파","timestamp":"2026-04-10T17:16:01Z","scan_request_id":"ingredient-scan-001"}
```

FE 동작:

- SSE 결과를 바로 DB에 저장하지 않습니다.
- 먼저 화면에 표시하고 사용자가 확인/수정한 뒤 저장 API를 호출합니다.

### POST `/api/v1/scan/liquor/start`

Response:

```json
{
  "status": "accepted",
  "message": "주류 스캔을 시작했습니다.",
  "scan_request_id": "liquor-scan-001"
}
```

### GET `/api/v1/stream/liquor`

SSE event:

```text
event: liquor
data: {"liquor_name":"소주","timestamp":"2026-04-10T17:20:00Z","scan_request_id":"liquor-scan-001"}
```

FE 동작:

- SSE 수신 후 주류 이름을 표시합니다.
- 같은 주류로 추천 API를 호출합니다.
- 최소 로딩 시간 같은 연출은 FE에서 처리합니다.

## Inventory

### GET `/api/v1/inventory`

Response:

```json
{
  "status": "success",
  "data": [
    {
      "ingredient_name": "대파",
      "quantity": 2,
      "last_updated": "2026-04-27T12:00:00Z"
    }
  ]
}
```

### POST `/api/v1/inventory/bulk`

Request:

```json
{
  "items": ["양파"]
}
```

Response:

```json
{
  "status": "success",
  "message": "보관함에 저장되었습니다.",
  "saved_count": 1
}
```

### POST `/api/v1/inventory`

Request:

```json
{
  "ingredient_name": "마늘",
  "quantity": 3
}
```

Response:

```json
{
  "status": "success",
  "message": "식재료가 추가되었습니다.",
  "ingredient_name": "마늘",
  "current_quantity": 3
}
```

### PATCH `/api/v1/inventory/quantity`

Request:

```json
{
  "ingredient_name": "대파",
  "action": "add"
}
```

`action` 값:

- `add`
- `subtract`

### PATCH `/api/v1/inventory/{ingredient_name}`

Request:

```json
{
  "new_ingredient_name": "다진 마늘",
  "quantity": 5
}
```

Response:

```json
{
  "status": "success",
  "message": "식재료가 수정되었습니다.",
  "ingredient_name": "다진 마늘",
  "current_quantity": 5
}
```

### DELETE `/api/v1/inventory/{ingredient_name}`

Response:

```json
{
  "status": "success",
  "message": "식재료가 삭제되었습니다."
}
```

## Recommendations

### GET `/api/v1/recommendations`

기본 호출:

```text
/api/v1/recommendations?liquor=소주&refresh=false
```

Query:

| name | type | required | note |
| --- | --- | --- | --- |
| `liquor` | string | yes | 주류 한글명 또는 내부 key |
| `refresh` | boolean | no | `true`이면 같은 조건에서 다음 추천 묶음 조회 |
| `available_only` | boolean | no | `true`이면 냉장고 재료만으로 가능한 추천만 조회 |
| `max_missing_count` | number | no | 부족한 핵심 재료 최대 개수 |
| `max_cook_time_minutes` | number | no | 최대 조리 시간(분) |
| `difficulty` | string | no | `easy`, `medium`, `hard` |
| `llm_fallback` | boolean | no | `true`이면 seed 추천이 3개 미만일 때 생성형 추천으로 부족한 추천만 보완 |

필터 예시:

```text
/api/v1/recommendations?liquor=레드와인&available_only=true
/api/v1/recommendations?liquor=소주&max_missing_count=1&max_cook_time_minutes=20&difficulty=easy
/api/v1/recommendations?liquor=소주&available_only=true&llm_fallback=true
```

필터 조건이 강하면 추천이 3개보다 적게 내려올 수 있습니다.
`llm_fallback=true`를 함께 보내면 BE가 먼저 seed 추천을 찾고, 부족한 개수만 생성형 추천으로 보완합니다.
생성형 추천 응답은 BE에서 JSON schema, 식재료 key, 재료 보유 상태, 조리 단계 수를 다시 검증한 뒤 통과한 항목만 내려갑니다.
외부 생성 호출 실패 또는 검증 실패 시 기존 seed 추천 결과만 반환합니다.

Response:

```json
{
  "liquor": "소주",
  "recommendations": [
    {
      "name": "돼지고기 대파 소금구이",
      "reason": "돼지고기와 대파의 구운 향이 소주와 잘 어울립니다.",
      "recommendation_source": "seed",
      "priority_rank": 1,
      "priority_reason": "현재 재고에서 2개 재료를 활용할 수 있고 부족 재료는 1개지만 페어링 기본 점수도 높아서 1순위로 골랐어요.",
      "selection_factors": [
        "핵심 재료 3개 중 2개를 지금 냉장고 재료로 바로 활용할 수 있어요.",
        "부족한 핵심 재료가 1개라 준비 부담이 비교적 적어요."
      ],
      "score_breakdown": {
        "available_ingredient_count": 2,
        "missing_ingredient_count": 1,
        "rank_hint": 95,
        "total_score": 99
      },
      "servings": 1,
      "cook_time_minutes": 15,
      "difficulty": "easy",
      "pairing_knowledge": {
        "flavor_logic": "구운 향과 짭조름한 맛이 소주의 깔끔함과 잘 맞습니다.",
        "ingredient_logic": "대파와 돼지고기를 빠르게 구워 감칠맛을 살립니다.",
        "why_this_liquor": "소주는 기름진 안주의 맛을 정리해주기 좋습니다."
      },
      "ingredient_yes": ["대파", "마늘"],
      "ingredient_no": ["돼지고기"],
      "ingredient_details": [
        {
          "item_name": "pork",
          "display_name": "돼지고기",
          "variant_detail": "구이용 돼지고기",
          "amount": 220,
          "unit": "g",
          "status": "missing"
        }
      ],
      "pantry_items": ["식용유 1큰술", "소금 0.3작은술", "후추 약간"],
      "pantry_item_details": [
        {"name": "식용유", "amount": 1, "unit": "큰술"}
      ],
      "shopping_items": ["돼지고기"],
      "substitution_tips": [
        {
          "missing_ingredient": "돼지고기",
          "suggestion": "소고기 또는 닭고기",
          "note": "고기 종류가 바뀌면 같은 크기로 썰고 중심까지 익혀주세요."
        }
      ],
      "recipe": ["1. 재료를 손질합니다.", "2. 팬에 굽습니다."],
      "recipe_steps": [
        {
          "step_number": 1,
          "title": "재료 손질",
          "instruction": "돼지고기와 대파를 먹기 좋은 크기로 썰어주세요.",
          "time_minutes": 3,
          "heat_level": "없음",
          "success_cue": "재료 크기가 비슷하게 맞으면 좋아요."
        }
      ],
      "missing_ingredients": ["돼지고기"],
      "tip": "팬을 먼저 예열하면 구운 향이 더 잘 살아납니다.",
      "tags": ["구이", "소주"]
    }
  ]
}
```

FE 표시 가이드:

- `recommendation_source`: `seed`이면 검수된 seed DB 추천, `llm_fallback`이면 seed 부족분을 실시간 보완한 추천입니다. FE는 `llm_fallback`일 때 카드에 `실시간 보완` 같은 작은 배지를 표시할 수 있습니다.
- `ingredient_yes`: 재료 체크리스트에서 "냉장고에 있음"
- `ingredient_no`: 재료 체크리스트에서 "부족함"
- `missing_ingredients`: 기존 호환용 부족 재료 목록. `ingredient_no`와 같은 표시명 기준입니다.
- `ingredient_details[].status`: 재료별 `available` 또는 `missing` 상태 표시
- `recipe_steps`: 상세 화면의 구조화된 조리 단계. `recipe`보다 우선 사용 권장
- `shopping_items`: 장보기 목록/구매 필요 영역에 바로 표시
- `substitution_tips`: 부족 재료가 있을 때 대체 재료 또는 구매 안내로 표시
- `priority_rank`, `priority_reason`, `selection_factors`: 추천 근거 표시용
- `score_breakdown`: 디버그/운영 검수용. 사용자 화면에 꼭 노출하지 않아도 됨
- `pantry_items`, `pantry_item_details`: 기본 양념/상온 재료 안내용

## Partial Recommendation Refresh

### POST `/api/v1/recommendations/refresh`

사용자가 추천 3개 중 일부를 고정한 뒤 나머지만 새로 보고 싶을 때 사용합니다.

Request:

```json
{
  "liquor": "소주",
  "keep_recommendations": [
    {
      "name": "두부 김치",
      "reason": "짭조름하고 매콤해 소주와 잘 어울립니다.",
      "ingredient_yes": ["두부", "김치"],
      "ingredient_no": [],
      "recipe": ["1. 두부를 데칩니다.", "2. 김치를 볶습니다."],
      "missing_ingredients": []
    }
  ],
  "refresh_count": 2,
  "llm_fallback": true
}
```

`llm_fallback=true`이면 고정 추천을 제외하고 새로 채워야 하는 개수가 seed만으로 부족할 때 생성형 보완 추천을 사용할 수 있습니다.

Response:

```json
{
  "liquor": "소주",
  "recommendations": [
    {
      "name": "두부 김치",
      "reason": "짭조름하고 매콤해 소주와 잘 어울립니다.",
      "ingredient_yes": ["두부", "김치"],
      "ingredient_no": [],
      "recipe": ["1. 두부를 데칩니다.", "2. 김치를 볶습니다."],
      "missing_ingredients": []
    }
  ]
}
```

## Favorite Recipes

즐겨찾기는 추천 상세 화면의 하트 버튼과 연결합니다. 저장 payload는 추천 응답 객체를 그대로 보내도 되고, 기존 필드만 보내도 됩니다.

### POST `/api/v1/favorite-recipes`

Request:

```json
{
  "liquor": "소주",
  "name": "대파 삼겹살 볶음",
  "reason": "소주와 잘 어울립니다.",
  "ingredient_yes": ["대파"],
  "ingredient_no": ["삼겹살"],
  "recipe": ["1. 대파를 썹니다.", "2. 고기를 굽습니다."],
  "missing_ingredients": ["삼겹살"]
}
```

Response:

```json
{
  "status": "success",
  "message": "즐겨찾기 레시피에 저장되었습니다.",
  "favorite_id": 1
}
```

### GET `/api/v1/favorite-recipes`

Response:

```json
{
  "status": "success",
  "data": []
}
```

### GET `/api/v1/favorite-recipes/{favorite_id}`

Response:

```json
{
  "status": "success",
  "data": {
    "favorite_id": 1,
    "name": "대파 삼겹살 볶음"
  }
}
```

### DELETE `/api/v1/favorite-recipes/{favorite_id}`

Response:

```json
{
  "status": "success",
  "message": "즐겨찾기 레시피에서 삭제되었습니다."
}
```
