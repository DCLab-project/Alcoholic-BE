# FE API Contract

이 문서는 FE 공유 API 시트에 옮기기 위한 BE 계약입니다. 기존 필드는 유지하고, 새 필드는 optional 또는 additive 방식으로만 추가합니다.

## 공통

- Base URL local: `http://127.0.0.1:8000`
- JSON 날짜/시간: ISO 8601 UTC 문자열
- 인증: MVP 단계에서는 없음
- 추천 주류 key: `soju`, `beer`, `red_wine`, `white_wine`, `sparkling_wine`, `whisky`, `sake`
- 추천 응답 필수 체크리스트 필드: `ingredient_yes`, `ingredient_no`, `missing_ingredients`, `ingredient_details[].status`

## 재료 Key

| key | display |
| --- | --- |
| `bacon` | 베이컨 |
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
| `fish` | 생선 |
| `garlic` | 마늘 |
| `green_onion` | 대파 |
| `lettuce` | 상추 |
| `milk` | 우유 |
| `mushroom` | 버섯 |
| `onion` | 양파 |
| `pepper` | 파프리카 |
| `pork` | 돼지고기 |
| `potato` | 감자 |
| `sausage` | 소시지 |
| `spinach` | 시금치 |
| `tomato` | 토마토 |
| `yogurt` | 요거트 |
| `zucchini` | 애호박 |

주의:

- `pepper`는 고추가 아니라 파프리카입니다.
- `leek`, `scallion`, `spring_onion`은 BE에서 `green_onion`으로 정규화합니다.
- `ginger`는 AI label에는 있을 수 있지만 추천 seed core ingredient에는 사용하지 않습니다.
- `fish`, `mushroom`, `cheese`는 broad key라서 FE는 세부 품종을 단정하지 않습니다.

## Endpoints

| Method | Path | FE 용도 |
| --- | --- | --- |
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/api/v1/inventory` | 현재 저장된 냉장고 재료 조회 |
| `POST` | `/api/v1/inventory/bulk` | AI 감지 후보를 사용자가 확정 저장 |
| `PATCH` | `/api/v1/inventory/quantity` | 재료 수량 +1/-1 |
| `GET` | `/api/v1/stream/ingredients` | 식재료 감지 SSE 구독 |
| `GET` | `/api/v1/stream/liquor` | 주류 감지 SSE 구독 |
| `GET` | `/api/v1/stream/recommendations` | 추천 결과 SSE 구독 |
| `POST` | `/api/v1/scan/liquor/start` | 수동 주류 스캔 fallback 시작 |
| `GET` | `/api/v1/recommendations` | 주류 기준 추천 3개 조회 |

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
  "items": ["대파", "green_onion", "양파"]
}
```

Response:

```json
{
  "status": "success",
  "message": "보관함에 저장되었습니다.",
  "saved_count": 3
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

Response:

```json
{
  "status": "success",
  "ingredient_name": "대파",
  "current_quantity": 3
}
```

## SSE

SSE는 `text/event-stream`으로 연결합니다. 이벤트 payload는 JSON 문자열입니다.

### GET `/api/v1/stream/ingredients`

Example event data:

```json
{
  "ingredient_name": "대파",
  "timestamp": "2026-04-27T12:00:00Z"
}
```

### GET `/api/v1/stream/liquor`

Example event data:

```json
{
  "liquor_name": "소주",
  "timestamp": "2026-04-27T12:00:05Z"
}
```

### GET `/api/v1/stream/recommendations`

Event data shape is the same as `GET /api/v1/recommendations`.

## FE Sheet Additions

The following endpoints are additive and keep the existing response fields stable.

### POST `/api/v1/scan/ingredients/start`

Starts a manual ingredient scan and returns `scan_request_id`. The ingredient SSE payload includes the same `scan_request_id` so FE can connect the button request to the streamed result.

### Inventory CRUD

- `POST /api/v1/inventory`: manually add one item with `ingredient_name` and `quantity`.
- `PATCH /api/v1/inventory/{ingredient_name}`: rename an item and/or set quantity directly.
- `DELETE /api/v1/inventory/{ingredient_name}`: delete one item.

### Favorite Recipes

- `POST /api/v1/favorite-recipes`: save a recommendation payload.
- `GET /api/v1/favorite-recipes`: list saved recipes.
- `GET /api/v1/favorite-recipes/{favorite_id}`: get one saved recipe.
- `DELETE /api/v1/favorite-recipes/{favorite_id}`: remove one saved recipe.

### POST `/api/v1/recommendations/refresh`

Keeps `keep_recommendations` and fills the remaining slots up to 3 recommendations. Existing recommendation fields such as `name`, `reason`, `ingredient_yes`, `ingredient_no`, `recipe`, and `missing_ingredients` are preserved. Expanded fields such as `ingredient_details`, `recipe_steps`, `priority_rank`, `selection_factors`, `score_breakdown`, and `pantry_items` are also returned when BE selects new recommendations.

## Manual Liquor Scan

### POST `/api/v1/scan/liquor/start`

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
  "message": "주류 스캔을 시작했습니다.",
  "scan_request_id": "liquor-scan-20260427120000000"
}
```

## Recommendations

### GET `/api/v1/recommendations?liquor=soju&refresh=false`

Query:

| name | type | required | note |
| --- | --- | --- | --- |
| `liquor` | string | yes | 주류 key 또는 한국어 표시명 |
| `refresh` | boolean | no | `true`면 같은 조건에서 다음 추천 묶음 조회 |

Response 핵심 필드:

```json
{
  "liquor": "소주",
  "recommendations": [
    {
      "name": "돼지고기 대파 소금구이",
      "reason": "소주와 잘 맞는 이유를 설명합니다.",
      "priority_rank": 1,
      "priority_reason": "현재 재료와 점수 기준으로 선택된 이유입니다.",
      "selection_factors": ["필수 재료 3개 중 2개를 사용할 수 있어요."],
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
        "flavor_logic": "맛 관점 설명",
        "ingredient_logic": "재료 관점 설명",
        "why_this_liquor": "이 주류와 맞는 이유"
      },
      "ingredient_yes": ["대파", "상추"],
      "ingredient_no": ["돼지고기"],
      "ingredient_details": [
        {
          "item_name": "pork",
          "display_name": "돼지고기",
          "variant_detail": "구이용 목살 또는 앞다리살",
          "amount": 220,
          "unit": "g",
          "status": "missing"
        }
      ],
      "pantry_items": ["식용유 1큰술"],
      "pantry_item_details": [
        {"name": "식용유", "amount": 1, "unit": "큰술"}
      ],
      "recipe": ["1. 재료를 손질합니다."],
      "recipe_steps": [
        {
          "step_number": 1,
          "title": "재료 손질",
          "instruction": "초보자도 따라할 수 있게 수량과 시간을 포함합니다.",
          "time_minutes": 3,
          "heat_level": "없음",
          "success_cue": "재료 표면 물기가 거의 없으면 좋아요."
        }
      ],
      "missing_ingredients": ["돼지고기"],
      "tip": "조리 팁",
      "tags": ["팬구이", "소주"]
    }
  ]
}
```

