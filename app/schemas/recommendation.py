from pydantic import BaseModel, Field


class RecommendationIngredientDetail(BaseModel):
    item_name: str = Field(description="내부 식재료 키 이름")
    display_name: str = Field(description="사용자에게 보여줄 식재료 한글 이름")
    amount: float = Field(description="필요한 식재료 수량")
    unit: str = Field(description="식재료 수량 단위")
    status: str = Field(description="현재 재고 기준 보유 여부")


class RecommendationScoreBreakdown(BaseModel):
    available_ingredient_count: int = Field(description="현재 재고에서 바로 활용 가능한 핵심 재료 수")
    missing_ingredient_count: int = Field(description="추가 구매가 필요한 핵심 재료 수")
    rank_hint: int = Field(description="기본 레시피 우선순위 힌트 값")
    total_score: int = Field(description="현재 추천 정렬에 사용된 총점")


class RecommendationItem(BaseModel):
    name: str = Field(description="추천 안주 이름")
    reason: str = Field(description="해당 안주를 추천하는 이유")
    priority_rank: int = Field(description="현재 추천 결과 내 우선순위")
    priority_reason: str = Field(description="이 안주가 현재 순위로 선택된 이유")
    selection_factors: list[str] = Field(description="우선순위 산정에 반영된 핵심 요인")
    score_breakdown: RecommendationScoreBreakdown = Field(
        description="추천 우선순위 산정에 사용된 점수 구성"
    )
    servings: int = Field(description="기준 인분 수")
    cook_time_minutes: int = Field(description="예상 조리 시간(분)")
    difficulty: str = Field(description="조리 난이도")
    ingredient_details: list[RecommendationIngredientDetail] = Field(
        description="정량화된 재료 목록과 현재 보유 상태"
    )
    pantry_items: list[str] = Field(description="상온에 기본 보유한다고 가정하는 양념/재료")
    recipe: list[str] = Field(description="단계별 조리 순서")
    missing_ingredients: list[str] = Field(description="현재 재고에 없어 추가로 필요한 재료")
    tip: str = Field(description="조리 또는 페어링 팁")


class RecommendationsResponse(BaseModel):
    liquor: str = Field(description="추천 기준이 된 주류 이름")
    recommendations: list[RecommendationItem] = Field(description="안주 추천 결과 목록")
