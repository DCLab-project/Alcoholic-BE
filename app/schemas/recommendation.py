from typing import Any

from pydantic import BaseModel, Field


RECOMMENDATIONS_RESPONSE_EXAMPLE = {
    "liquor": "소주",
    "recommendations": [
        {
            "name": "돼지목살 대파 소금구이",
            "reason": "돼지목살의 고소한 육향과 구운 대파의 단맛을 살린 소주와 잘 어울리는 집 안주예요.",
            "priority_rank": 1,
            "priority_reason": "현재 재고만으로 바로 만들 수 있고 페어링 기본 점수도 높아서 1순위로 골랐어요.",
            "selection_factors": [
                "핵심 재료 3개 중 2개를 지금 냉장고 재료로 바로 활용할 수 있어요.",
                "부족한 핵심 재료가 1개라 준비 부담이 비교적 적어요.",
                "이 주류와의 기본 페어링 점수가 아주 높은 후보예요.",
            ],
            "score_breakdown": {
                "available_ingredient_count": 2,
                "missing_ingredient_count": 1,
                "rank_hint": 95,
                "total_score": 99,
            },
            "servings": 1,
            "cook_time_minutes": 15,
            "difficulty": "easy",
            "pairing_knowledge": {
                "flavor_logic": "돼지목살의 고소한 육향과 구운 대파의 단맛이 소주의 깔끔한 목넘김과 잘 어울려요.",
                "ingredient_logic": "돼지고기와 대파를 팬구이 방식으로 조리해 구운 향과 단맛을 살렸어요.",
                "why_this_liquor": "소주는 기름진 고기 안주의 끝맛을 가볍게 정리해주기 좋아요.",
            },
            "ingredient_yes": ["대파", "상추"],
            "ingredient_no": ["돼지고기"],
            "ingredient_details": [
                {
                    "item_name": "pork",
                    "display_name": "돼지고기",
                    "variant_detail": "구이용 돼지목살 또는 앞다리살",
                    "amount": 220,
                    "unit": "g",
                    "status": "missing",
                },
                {
                    "item_name": "leek",
                    "display_name": "대파",
                    "variant_detail": "굵은 대파",
                    "amount": 1,
                    "unit": "대",
                    "status": "available",
                },
                {
                    "item_name": "lettuce",
                    "display_name": "상추",
                    "variant_detail": "쌈용 상추",
                    "amount": 4,
                    "unit": "장",
                    "status": "available",
                },
            ],
            "pantry_items": [
                "식용유 1큰술",
                "소금 0.3작은술",
                "후추 0.2작은술",
            ],
            "pantry_item_details": [
                {"name": "식용유", "amount": 1, "unit": "큰술"},
                {"name": "소금", "amount": 0.3, "unit": "작은술"},
                {"name": "후추", "amount": 0.2, "unit": "작은술"},
            ],
            "shopping_items": ["돼지고기"],
            "substitution_tips": [
                {
                    "missing_ingredient": "돼지고기",
                    "suggestion": "소고기 또는 닭고기",
                    "note": "고기 종류가 바뀌면 같은 크기로 썰고 중심까지 익혀주세요.",
                }
            ],
            "recipe": [
                "1. 재료 손질: 돼지고기, 대파, 상추를 먹기 좋은 크기로 준비하고, 물기가 있는 재료는 키친타월로 가볍게 눌러주세요.",
                "2. 밑간하기: 돼지고기에 소금과 후추를 가볍게 뿌려주세요.",
                "3. 굽기: 달군 팬에 돼지고기를 올려 앞뒤로 노릇하게 구워주세요.",
                "4. 대파 굽기: 돼지고기 기름에 대파를 넣고 구운 향이 나도록 익혀주세요.",
                "5. 담아내기: 상추와 함께 접시에 담아 바로 곁들여주세요.",
            ],
            "recipe_steps": [
                {
                    "step_number": 1,
                    "title": "재료 손질",
                    "instruction": "돼지고기, 대파, 상추를 먹기 좋은 크기로 준비하고, 물기가 있는 재료는 키친타월로 가볍게 눌러주세요.",
                    "time_minutes": 3,
                    "heat_level": "없음",
                    "success_cue": "재료 크기가 비슷하고 표면 물기가 많지 않으면 좋아요.",
                },
                {
                    "step_number": 2,
                    "title": "밑간하기",
                    "instruction": "돼지고기에 소금과 후추를 가볍게 뿌려주세요.",
                    "time_minutes": 2,
                    "heat_level": "없음",
                    "success_cue": "고기 표면에 간이 얇게 고르게 붙어 있으면 좋아요.",
                },
                {
                    "step_number": 3,
                    "title": "굽기",
                    "instruction": "달군 팬에 돼지고기를 올려 앞뒤로 노릇하게 구워주세요.",
                    "time_minutes": 6,
                    "heat_level": "중강불",
                    "success_cue": "겉면에 노릇한 구운 자국이 생기면 좋아요.",
                },
                {
                    "step_number": 4,
                    "title": "대파 굽기",
                    "instruction": "돼지고기 기름에 대파를 넣고 구운 향이 나도록 익혀주세요.",
                    "time_minutes": 3,
                    "heat_level": "중불",
                    "success_cue": "대파 가장자리가 갈색이고 단향이 올라오면 좋아요.",
                },
                {
                    "step_number": 5,
                    "title": "담아내기",
                    "instruction": "상추와 함께 접시에 담아 바로 곁들여주세요.",
                    "time_minutes": 1,
                    "heat_level": "없음",
                    "success_cue": "고기는 따뜻하고 상추는 숨이 죽지 않은 상태면 좋아요.",
                },
            ],
            "missing_ingredients": ["돼지고기"],
            "tip": "고기를 올리기 전 팬을 충분히 예열하면 물이 덜 나오고 구운 향이 선명해져요.",
            "tags": ["팬구이", "돼지고기", "대파", "소주"],
        }
    ],
}


class RecommendationIngredientDetail(BaseModel):
    item_name: str = Field(description="내부 식재료 키 이름")
    display_name: str = Field(description="사용자에게 보여줄 식재료 한글 이름")
    variant_detail: str = Field(default="", description="재료의 구체적인 종류 또는 손질 상태")
    amount: float = Field(description="필요한 식재료 수량")
    unit: str = Field(description="식재료 수량 단위")
    status: str = Field(description="현재 재고 기준 보유 여부")


class RecommendationPantryItem(BaseModel):
    name: str = Field(description="기본 양념 또는 상온 재료 이름")
    amount: float = Field(description="필요한 양")
    unit: str = Field(description="수량 단위")


class RecommendationSubstitutionTip(BaseModel):
    missing_ingredient: str = Field(description="부족한 핵심 재료 이름")
    suggestion: str = Field(description="대체 후보 또는 구매 권장 안내")
    note: str = Field(description="대체할 때 FE에 보여줄 짧은 주의 문구")


class RecommendationRecipeStep(BaseModel):
    step_number: int = Field(description="조리 단계 번호")
    title: str = Field(description="단계 제목")
    instruction: str = Field(description="초보자도 따라할 수 있는 조리 설명")
    time_minutes: int = Field(description="해당 단계 예상 시간(분)")
    heat_level: str = Field(description="없음|약불|중불|중강불|센 불 중 하나")
    success_cue: str = Field(description="단계가 잘 진행됐는지 확인하는 기준")


class RecommendationPairingKnowledge(BaseModel):
    flavor_logic: str = Field(description="맛과 향 관점의 페어링 논리")
    ingredient_logic: str = Field(description="재료와 조리법 관점의 페어링 논리")
    why_this_liquor: str = Field(description="이 주류와 특히 잘 맞는 이유")


class RecommendationScoreBreakdown(BaseModel):
    available_ingredient_count: int = Field(description="현재 재고에서 바로 활용 가능한 핵심 재료 수")
    missing_ingredient_count: int = Field(description="추가 구매가 필요한 핵심 재료 수")
    rank_hint: int = Field(description="기본 레시피 우선순위 힌트 값")
    total_score: int = Field(description="현재 추천 정렬에 사용된 총점")


class RecommendationItem(BaseModel):
    name: str = Field(description="추천 안주 이름")
    reason: str = Field(description="해당 안주를 추천하는 이유")
    recommendation_source: str = Field(
        default="seed",
        description="추천 출처입니다. seed 또는 llm_fallback 값을 사용합니다.",
    )
    priority_rank: int = Field(description="현재 추천 결과 내 우선순위")
    priority_reason: str = Field(description="이 안주가 현재 순위로 선택된 이유")
    selection_factors: list[str] = Field(description="우선순위 산정에 반영된 핵심 요인")
    score_breakdown: RecommendationScoreBreakdown = Field(
        description="추천 우선순위 산정에 사용된 점수 구성"
    )
    servings: int = Field(description="기준 인분 수")
    cook_time_minutes: int = Field(description="예상 조리 시간(분)")
    difficulty: str = Field(description="조리 난이도")
    pairing_knowledge: RecommendationPairingKnowledge = Field(
        description="주류 페어링 지식"
    )
    ingredient_yes: list[str] = Field(
        description="현재 재고에 있어 바로 사용할 수 있는 필요 재료의 한글 이름"
    )
    ingredient_no: list[str] = Field(
        description="현재 재고에 없어 추가로 필요한 필요 재료의 한글 이름"
    )
    ingredient_details: list[RecommendationIngredientDetail] = Field(
        min_length=1,
        max_length=30,
        description="정량화된 재료 목록과 현재 보유 상태입니다. 레시피에 따라 1개부터 30개까지 내려갈 수 있습니다.",
    )
    pantry_items: list[str] = Field(description="상온에 기본 보유한다고 가정하는 양념/재료")
    pantry_item_details: list[RecommendationPantryItem] = Field(
        description="정량화된 기본 양념 목록"
    )
    shopping_items: list[str] = Field(
        default_factory=list,
        description="장보기 UI에 바로 표시할 부족 핵심 재료 목록",
    )
    substitution_tips: list[RecommendationSubstitutionTip] = Field(
        default_factory=list,
        description="부족 핵심 재료별 대체 또는 구매 안내",
    )
    recipe: list[str] = Field(description="단계별 조리 순서")
    recipe_steps: list[RecommendationRecipeStep] = Field(description="구조화된 단계별 조리 순서")
    missing_ingredients: list[str] = Field(description="현재 재고에 없어 추가로 필요한 재료의 한글 이름")
    tip: str = Field(description="조리 또는 페어링 팁")
    tags: list[str] = Field(description="레시피 태그")


class RecommendationsResponse(BaseModel):
    liquor: str = Field(description="추천 기준이 된 주류 한글 이름")
    recommendations: list[RecommendationItem] = Field(description="안주 추천 결과 목록")

    model_config = {
        "json_schema_extra": {
            "example": RECOMMENDATIONS_RESPONSE_EXAMPLE,
        }
    }


class RecommendationRefreshRequest(BaseModel):
    liquor: str = Field(min_length=1, max_length=100)
    keep_recommendations: list[dict[str, Any]] = Field(default_factory=list)
    refresh_count: int = Field(default=1, ge=0, le=3)
    llm_fallback: bool = Field(
        default=False,
        description="true이면 seed 추천이 부족할 때 생성형 추천으로 부족한 추천만 보완합니다.",
    )


class RecommendationRefreshResponse(BaseModel):
    liquor: str
    recommendations: list[dict[str, Any]]
