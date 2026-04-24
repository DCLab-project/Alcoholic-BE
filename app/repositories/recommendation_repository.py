from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Recipe


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_recipe_candidates(self, liquor_name: str, refresh: bool) -> list[Recipe]:
        normalized_liquor = liquor_name.strip().lower() or "soju"
        refresh_group = 1 if refresh else 0

        recipes = self._fetch_candidates(normalized_liquor, refresh_group)
        if recipes:
            return recipes

        if refresh_group == 1:
            recipes = self._fetch_candidates(normalized_liquor, 0)
            if recipes:
                return recipes

        if normalized_liquor != "soju":
            recipes = self._fetch_candidates("soju", refresh_group)
            if recipes:
                return recipes
            return self._fetch_candidates("soju", 0)

        return []

    def _fetch_candidates(self, liquor_name: str, refresh_group: int) -> list[Recipe]:
        stmt = (
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .where(
                Recipe.liquor_name == liquor_name,
                Recipe.refresh_group == refresh_group,
            )
            .order_by(Recipe.rank_hint.desc(), Recipe.id.asc())
        )
        return list(self.db.scalars(stmt).all())
