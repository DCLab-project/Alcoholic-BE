from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import FavoriteRecipe


class FavoriteRecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, favorite: FavoriteRecipe) -> FavoriteRecipe:
        self.db.add(favorite)
        self.db.flush()
        return favorite

    def list_all(self) -> list[FavoriteRecipe]:
        stmt = select(FavoriteRecipe).order_by(FavoriteRecipe.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get(self, favorite_id: int) -> FavoriteRecipe | None:
        stmt = select(FavoriteRecipe).where(FavoriteRecipe.id == favorite_id)
        return self.db.scalar(stmt)

    def delete(self, favorite: FavoriteRecipe) -> None:
        self.db.delete(favorite)
        self.db.flush()
