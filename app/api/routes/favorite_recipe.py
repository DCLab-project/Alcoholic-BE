from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.favorite_recipe_repository import FavoriteRecipeRepository
from app.schemas.favorite_recipe import (
    FavoriteRecipeCreate,
    FavoriteRecipeCreateResponse,
    FavoriteRecipeDeleteResponse,
    FavoriteRecipeDetailResponse,
    FavoriteRecipeListResponse,
)
from app.services.favorite_recipe_service import FavoriteRecipeService

router = APIRouter(prefix="/api/v1/favorite-recipes", tags=["즐겨찾기 레시피"])


def _service(db: Session) -> FavoriteRecipeService:
    return FavoriteRecipeService(db, FavoriteRecipeRepository(db))


@router.post(
    "",
    response_model=FavoriteRecipeCreateResponse,
    status_code=201,
    summary="즐겨찾기 레시피 저장",
)
def create_favorite_recipe(
    payload: FavoriteRecipeCreate,
    db: Session = Depends(get_db),
) -> FavoriteRecipeCreateResponse:
    return _service(db).create_favorite(payload)


@router.get(
    "",
    response_model=FavoriteRecipeListResponse,
    summary="즐겨찾기 레시피 목록 조회",
)
def list_favorite_recipes(
    db: Session = Depends(get_db),
) -> FavoriteRecipeListResponse:
    return _service(db).list_favorites()


@router.get(
    "/{favorite_id}",
    response_model=FavoriteRecipeDetailResponse,
    summary="즐겨찾기 레시피 상세 조회",
)
def get_favorite_recipe(
    favorite_id: int,
    db: Session = Depends(get_db),
) -> FavoriteRecipeDetailResponse:
    return _service(db).get_favorite(favorite_id)


@router.delete(
    "/{favorite_id}",
    response_model=FavoriteRecipeDeleteResponse,
    summary="즐겨찾기 레시피 삭제",
)
def delete_favorite_recipe(
    favorite_id: int,
    db: Session = Depends(get_db),
) -> FavoriteRecipeDeleteResponse:
    return _service(db).delete_favorite(favorite_id)
