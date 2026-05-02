import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models import FavoriteRecipe
from app.repositories.favorite_recipe_repository import FavoriteRecipeRepository
from app.schemas.favorite_recipe import (
    FavoriteRecipeCreate,
    FavoriteRecipeCreateResponse,
    FavoriteRecipeDeleteResponse,
    FavoriteRecipeDetailResponse,
    FavoriteRecipeListResponse,
)


class FavoriteRecipeService:
    def __init__(self, db: Session, repository: FavoriteRecipeRepository):
        self.db = db
        self.repository = repository

    @staticmethod
    def _json_list(items: list[str]) -> str:
        return json.dumps(items, ensure_ascii=False)

    @staticmethod
    def _load_json(value: str | None, fallback: Any) -> Any:
        if not value:
            return fallback
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return fallback

    @classmethod
    def _to_payload(cls, favorite: FavoriteRecipe) -> dict[str, Any]:
        payload = cls._load_json(favorite.payload_text, {})
        if not isinstance(payload, dict):
            payload = {}

        payload.update(
            {
                "favorite_id": str(favorite.id),
                "id": str(favorite.id),
                "liquor": favorite.liquor,
                "name": favorite.name,
                "reason": favorite.reason,
                "ingredient_yes": cls._load_json(favorite.ingredient_yes_text, []),
                "ingredient_no": cls._load_json(favorite.ingredient_no_text, []),
                "recipe": cls._load_json(favorite.recipe_text, []),
                "missing_ingredients": cls._load_json(
                    favorite.missing_ingredients_text,
                    [],
                ),
                "created_at": favorite.created_at,
            }
        )
        return payload

    def create_favorite(
        self, payload: FavoriteRecipeCreate
    ) -> FavoriteRecipeCreateResponse:
        payload_dict = payload.model_dump(mode="json")
        favorite = FavoriteRecipe(
            liquor=payload.liquor,
            name=payload.name,
            reason=payload.reason,
            ingredient_yes_text=self._json_list(payload.ingredient_yes),
            ingredient_no_text=self._json_list(payload.ingredient_no),
            recipe_text=self._json_list(payload.recipe),
            missing_ingredients_text=self._json_list(payload.missing_ingredients),
            payload_text=json.dumps(payload_dict, ensure_ascii=False),
        )
        self.repository.create(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return FavoriteRecipeCreateResponse(
            status="success",
            message="즐겨찾기 레시피에 저장되었습니다.",
            favorite_id=favorite.id,
        )

    def list_favorites(self) -> FavoriteRecipeListResponse:
        return FavoriteRecipeListResponse(
            status="success",
            data=[
                self._to_payload(favorite)
                for favorite in self.repository.list_all()
            ],
        )

    def get_favorite(self, favorite_id: int) -> FavoriteRecipeDetailResponse:
        favorite = self.repository.get(favorite_id)
        if favorite is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="즐겨찾기 레시피를 찾을 수 없습니다.",
            )
        return FavoriteRecipeDetailResponse(
            status="success",
            data=self._to_payload(favorite),
        )

    def delete_favorite(self, favorite_id: int) -> FavoriteRecipeDeleteResponse:
        favorite = self.repository.get(favorite_id)
        if favorite is not None:
            self.repository.delete(favorite)
            self.db.commit()

        return FavoriteRecipeDeleteResponse(
            status="success",
            message="즐겨찾기 레시피에서 삭제되었습니다.",
        )
