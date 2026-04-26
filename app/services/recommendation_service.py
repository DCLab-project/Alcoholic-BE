import json
import time
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import (
    RecommendationIngredientDetail,
    RecommendationItem,
    RecommendationPairingKnowledge,
    RecommendationPantryItem,
    RecommendationRecipeStep,
    RecommendationScoreBreakdown,
    RecommendationsResponse,
)
from app.services.name_mapping import (
    ingredient_display_name,
    liquor_display_name,
    normalize_ingredient_key,
    normalize_liquor_key,
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
            factors.append(f"핵심 재료 {total_required}개 중 {available_count}개를 지금 냉장고 재료로 바로 활용할 수 있어요.")

        if missing_count == 0:
            factors.append("추가 장보기 없이 바로 만들기 좋은 레시피예요.")
        else:
            factors.append(f"부족한 핵심 재료가 {missing_count}개라 준비 부담이 비교적 적어요.")

        if rank_hint >= 90:
            factors.append("이 주류와의 기본 페어링 점수가 아주 높은 후보예요.")
        elif rank_hint >= 80:
            factors.append("현재 고른 술과 잘 맞는 상위권 페어링 레시피예요.")
        else:
            factors.append("현재 고른 술과 편하게 곁들이기 좋은 보조 후보예요.")

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
            "현재 재고만으로 바로 만들 수 있고"
            if missing_count == 0
            else f"현재 재고에서 {available_count}개 재료를 활용할 수 있고 부족 재료는 {missing_count}개지만"
        )

        pairing_phrase = (
            "페어링 기본 점수도 높아서"
            if rank_hint >= 85
            else "다른 후보와 비교해 전체 균형이 좋아서"
        )

        return f"{availability_phrase} {pairing_phrase} {rank}순위로 골랐어요."

    @staticmethod
    def _load_json_list(value: str | None) -> list[Any]:
        if not value:
            return []

        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return []

        return loaded if isinstance(loaded, list) else []

    @classmethod
    def _build_pantry_item_details(cls, recipe) -> list[RecommendationPantryItem]:
        details: list[RecommendationPantryItem] = []
        for item in cls._load_json_list(recipe.pantry_item_details_text):
            if not isinstance(item, dict):
                continue
            details.append(
                RecommendationPantryItem(
                    name=str(item.get("name") or ""),
                    amount=float(item.get("amount") or 0),
                    unit=str(item.get("unit") or ""),
                )
            )
        return details

    @classmethod
    def _build_recipe_steps(cls, recipe) -> list[RecommendationRecipeStep]:
        structured_steps: list[RecommendationRecipeStep] = []
        for item in cls._load_json_list(recipe.recipe_steps_text):
            if not isinstance(item, dict):
                continue
            structured_steps.append(
                RecommendationRecipeStep(
                    step_number=int(
                        item.get("step_number") or len(structured_steps) + 1
                    ),
                    title=str(item.get("title") or f"{len(structured_steps) + 1}단계"),
                    instruction=str(item.get("instruction") or ""),
                    time_minutes=int(item.get("time_minutes") or 0),
                    heat_level=str(item.get("heat_level") or "없음"),
                    success_cue=str(item.get("success_cue") or ""),
                )
            )

        if structured_steps:
            return structured_steps

        legacy_steps = [
            step for step in recipe.instructions_text.splitlines() if step.strip()
        ]
        return [
            RecommendationRecipeStep(
                step_number=index,
                title=f"{index}단계",
                instruction=step,
                time_minutes=0,
                heat_level="없음",
                success_cue="설명한 상태가 되면 다음 단계로 넘어가면 좋아요.",
            )
            for index, step in enumerate(legacy_steps, start=1)
        ]

    @staticmethod
    def _build_pairing_knowledge(recipe) -> RecommendationPairingKnowledge:
        return RecommendationPairingKnowledge(
            flavor_logic=recipe.pairing_flavor_logic or recipe.reason,
            ingredient_logic=recipe.pairing_ingredient_logic or "",
            why_this_liquor=recipe.pairing_why_this_liquor or "",
        )

    @classmethod
    def _build_tags(cls, recipe) -> list[str]:
        return [
            str(tag)
            for tag in cls._load_json_list(recipe.tags_text)
            if isinstance(tag, str) and tag.strip()
        ]

    def get_recommendations(self, liquor: str, refresh: bool) -> RecommendationsResponse:
        normalized = normalize_liquor_key(liquor or "soju") or "soju"
        inventory_counts: dict[str, int] = {}
        for item in self.inventory_repository.list_inventory_items():
            if item.count <= 0:
                continue
            ingredient_key = normalize_ingredient_key(item.item_name)
            inventory_counts[ingredient_key] = (
                inventory_counts.get(ingredient_key, 0) + item.count
            )
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
                    variant_detail=ingredient.variant_detail or "",
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
                    pairing_knowledge=self._build_pairing_knowledge(recipe),
                    ingredient_details=candidate["ingredient_details"],
                    pantry_items=[
                        item for item in recipe.pantry_items_text.splitlines() if item.strip()
                    ],
                    pantry_item_details=self._build_pantry_item_details(recipe),
                    recipe=[step for step in recipe.instructions_text.splitlines() if step],
                    recipe_steps=self._build_recipe_steps(recipe),
                    missing_ingredients=[
                        ingredient_display_name(ingredient_name)
                        for ingredient_name in candidate["missing_ingredients"]
                    ],
                    tip=recipe.tip,
                    tags=self._build_tags(recipe),
                )
            )

        time.sleep(5)
        return RecommendationsResponse(
            liquor=liquor_display_name(normalized),
            recommendations=recommendations,
        )
