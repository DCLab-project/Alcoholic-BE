# Gemini Recommendation Fallback

## 목적

기본 추천은 검수된 seed DB를 우선 사용합니다.
Gemini는 seed 추천이 부족하거나 사용자가 더 다양한 추천을 원할 때만 보조 생성기로 사용합니다.

## 동작 흐름

1. BE가 현재 주류와 냉장고 재고를 기준으로 seed 추천을 먼저 조회합니다.
2. 필터 조건 때문에 추천이 3개보다 적고 `llm_fallback=true`이면 부족한 개수만 Gemini에 요청합니다.
3. Gemini는 정해진 JSON schema에 맞춰 후보 레시피를 반환합니다.
4. BE가 응답을 다시 검증합니다.
   - 허용된 30개 식재료 key만 사용하는지 확인
   - `ingredient_details[].status`를 현재 DB 재고 기준으로 재계산
   - `ingredient_yes`, `ingredient_no`, `missing_ingredients`, `shopping_items`를 같은 표시명 기준으로 맞춤
   - 조리 단계가 6-9단계인지 확인
   - `외 N가지` 같은 모호한 문구를 차단
5. 검증을 통과한 후보만 FE 응답에 포함합니다.
6. Gemini 호출 실패 또는 검증 실패 시 기존 seed 추천 결과만 반환합니다.

## FE 호출

```text
GET /api/v1/recommendations?liquor=소주&available_only=true&llm_fallback=true
```

`llm_fallback`을 보내지 않으면 기존 seed 추천 방식만 사용합니다.

## 환경 변수

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_TIMEOUT_SECONDS=12
```

API 키는 `.env`에만 저장하고 GitHub에 커밋하지 않습니다.

## 보고서용 요약

본 프로젝트는 레시피 품질과 응답 안정성을 위해 검수된 seed DB를 1차 추천 지식으로 사용한다.
다만 현재 보유 재료와 필터 조건에 맞는 seed가 부족한 경우에는 Gemini API를 fallback 생성기로 호출하여 부족한 추천 수만 보완한다.
생성 결과는 백엔드에서 JSON schema와 도메인 규칙으로 재검증한 뒤 프론트엔드에 전달하므로, LLM 응답을 그대로 노출하는 방식보다 안정적이다.
