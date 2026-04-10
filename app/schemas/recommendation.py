from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    name: str = Field(description="추천 안주 이름")
    reason: str = Field(description="해당 안주를 추천하는 이유")
    recipe: list[str] = Field(description="간단한 조리 순서 목록")
    missing_ingredients: list[str] = Field(description="현재 재고에 없어서 추가로 필요한 재료 목록")


class RecommendationsResponse(BaseModel):
    liquor: str = Field(description="추천 기준이 된 주류 이름")
    recommendations: list[RecommendationItem] = Field(description="안주 추천 결과 목록")
