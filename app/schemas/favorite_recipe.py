from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class FavoriteRecipeCreate(BaseModel):
    liquor: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    reason: str = ""
    ingredient_yes: list[str] = Field(default_factory=list)
    ingredient_no: list[str] = Field(default_factory=list)
    recipe: list[str] = Field(default_factory=list)
    missing_ingredients: list[str] = Field(default_factory=list)

    model_config = {"extra": "allow"}


class FavoriteRecipeCreateResponse(BaseModel):
    status: Literal["success"]
    message: str
    favorite_id: int


class FavoriteRecipeData(BaseModel):
    favorite_id: int
    liquor: str
    name: str
    reason: str
    ingredient_yes: list[str]
    ingredient_no: list[str]
    recipe: list[str]
    missing_ingredients: list[str]
    created_at: datetime

    model_config = {"extra": "allow"}


class FavoriteRecipeListResponse(BaseModel):
    status: Literal["success"]
    data: list[dict[str, Any]]


class FavoriteRecipeDetailResponse(BaseModel):
    status: Literal["success"]
    data: dict[str, Any]


class FavoriteRecipeDeleteResponse(BaseModel):
    status: Literal["success"]
    message: str
