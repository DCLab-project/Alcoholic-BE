import time

from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import (
    RecommendationIngredientDetail,
    RecommendationItem,
    RecommendationScoreBreakdown,
    RecommendationsResponse,
)


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_repository = InventoryRepository(db)
        self.recommendation_repository = RecommendationRepository(db)

    @staticmethod
    def _build_selection_factors(
        *,
        available_count: int,
        missing_count: int,
        rank_hint: int,
        total_required: int,
    ) -> list[str]:
        factors: list[str] = []

        if total_required > 0:
            factors.append(f"핵심 재료 {total_required}개 중 {available_count}개를 현재 재고로 바로 활용할 수 있습니다.")

        if missing_count == 0:
            factors.append("추가 장보기 없이 바로 조리 가능한 레시피입니다.")
        else:
            factors.append(f"부족한 핵심 재료가 {missing_count}개라 준비 부담이 상대적으로 적습니다.")

        if rank_hint >= 90:
            factors.append("기본 주류 페어링 우선순위가 매우 높은 레시피입니다.")
        elif rank_hint >= 80:
            factors.append("현재 주류와 잘 맞는 상위권 페어링 레시피입니다.")
        else:
            factors.append("현재 주류와 무난하게 어울리는 보조 후보 레시피입니다.")

        return factors

    @staticmethod
    def _build_priority_reason(
        *,
        rank: int,
        available_count: int,
        missing_count: int,
        rank_hint: int,
    ) -> str:
        availability_phrase = (
            "현재 재고만으로 바로 조리할 수 있으며"
            if missing_count == 0
            else f"현재 재고에서 {available_count}개 재료를 활용할 수 있고 부족 재료는 {missing_count}개이지만"
        )

        pairing_phrase = (
            "페어링 기본 점수도 높아"
            if rank_hint >= 85
            else "다른 후보와 비교해 전체 균형이 좋아"
        )

        return f"{availability_phrase} {pairing_phrase} {rank}순위로 선정했습니다."

    def get_recommendations(self, liquor: str, refresh: bool) -> RecommendationsResponse:
        normalized = (liquor or "soju").strip().lower() or "soju"
        inventory_counts = {
            item.item_name: item.count
            for item in self.inventory_repository.list_inventory_items()
            if item.count > 0
        }
        candidates = self.recommendation_repository.list_recipe_candidates(normalized, refresh)
        ranked_candidates: list[dict] = []

        for recipe in candidates:
            required_ingredients = [ingredient.ingredient_name for ingredient in recipe.ingredients]
            missing_ingredients = [
                ingredient_name
                for ingredient_name in required_ingredients
                if inventory_counts.get(ingredient_name, 0) <= 0
            ]
            available_count = len(required_ingredients) - len(missing_ingredients)
            score = (available_count * 3) - (len(missing_ingredients) * 2) + recipe.rank_hint
            ingredient_details = [
                RecommendationIngredientDetail(
                    item_name=ingredient.ingredient_name,
                    display_name=ingredient.display_name or ingredient.ingredient_name,
                    amount=ingredient.amount,
                    unit=ingredient.unit,
                    status=(
                        "available"
                        if inventory_counts.get(ingredient.ingredient_name, 0) > 0
                        else "missing"
                    ),
                )
                for ingredient in recipe.ingredients
            ]
            ranked_candidates.append(
                {
                    "score": score,
                    "missing_count": len(missing_ingredients),
                    "rank_hint": recipe.rank_hint,
                    "name": recipe.name,
                    "available_count": available_count,
                    "total_required": len(required_ingredients),
                    "missing_ingredients": missing_ingredients,
                    "ingredient_details": ingredient_details,
                    "recipe": recipe,
                }
            )

        ranked_candidates.sort(
            key=lambda candidate: (
                -candidate["score"],
                candidate["missing_count"],
                -candidate["rank_hint"],
                candidate["name"],
            )
        )
        recommendations: list[RecommendationItem] = []
        for index, candidate in enumerate(ranked_candidates[:3], start=1):
            recipe = candidate["recipe"]
            recommendations.append(
                RecommendationItem(
                    name=recipe.name,
                    reason=recipe.reason,
                    priority_rank=index,
                    priority_reason=self._build_priority_reason(
                        rank=index,
                        available_count=candidate["available_count"],
                        missing_count=candidate["missing_count"],
                        rank_hint=candidate["rank_hint"],
                    ),
                    selection_factors=self._build_selection_factors(
                        available_count=candidate["available_count"],
                        missing_count=candidate["missing_count"],
                        rank_hint=candidate["rank_hint"],
                        total_required=candidate["total_required"],
                    ),
                    score_breakdown=RecommendationScoreBreakdown(
                        available_ingredient_count=candidate["available_count"],
                        missing_ingredient_count=candidate["missing_count"],
                        rank_hint=candidate["rank_hint"],
                        total_score=candidate["score"],
                    ),
                    servings=recipe.servings,
                    cook_time_minutes=recipe.cook_time_minutes,
                    difficulty=recipe.difficulty,
                    ingredient_details=candidate["ingredient_details"],
                    pantry_items=[
                        item for item in recipe.pantry_items_text.splitlines() if item.strip()
                    ],
                    recipe=[step for step in recipe.instructions_text.splitlines() if step],
                    missing_ingredients=candidate["missing_ingredients"],
                    tip=recipe.tip,
                )
            )

        time.sleep(5)
        return RecommendationsResponse(liquor=normalized, recommendations=recommendations)
