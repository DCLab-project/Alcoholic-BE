import time

from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import (
    RecommendationIngredientDetail,
    RecommendationItem,
    RecommendationsResponse,
)


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_repository = InventoryRepository(db)
        self.recommendation_repository = RecommendationRepository(db)

    def get_recommendations(self, liquor: str, refresh: bool) -> RecommendationsResponse:
        normalized = (liquor or "soju").strip().lower() or "soju"
        inventory_counts = {
            item.item_name: item.count
            for item in self.inventory_repository.list_inventory_items()
            if item.count > 0
        }
        candidates = self.recommendation_repository.list_recipe_candidates(normalized, refresh)
        ranked_recommendations: list[tuple[int, int, int, RecommendationItem]] = []

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
            ranked_recommendations.append(
                (
                    score,
                    len(missing_ingredients),
                    recipe.rank_hint,
                    RecommendationItem(
                        name=recipe.name,
                        reason=recipe.reason,
                        servings=recipe.servings,
                        cook_time_minutes=recipe.cook_time_minutes,
                        difficulty=recipe.difficulty,
                        ingredient_details=ingredient_details,
                        pantry_items=[
                            item for item in recipe.pantry_items_text.splitlines() if item.strip()
                        ],
                        recipe=[step for step in recipe.instructions_text.splitlines() if step],
                        missing_ingredients=missing_ingredients,
                        tip=recipe.tip,
                    ),
                )
            )

        ranked_recommendations.sort(
            key=lambda candidate: (-candidate[0], candidate[1], -candidate[2], candidate[3].name)
        )
        recommendations = [candidate[3] for candidate in ranked_recommendations[:3]]

        time.sleep(5)
        return RecommendationsResponse(liquor=normalized, recommendations=recommendations)
