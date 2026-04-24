import json
from pathlib import Path

from sqlalchemy import inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Recipe, RecipeIngredient


SEED_FILE = Path(__file__).resolve().parents[2] / "seeds" / "recommendations.json"

FALLBACK_DISPLAY_NAMES = {
    "bacon": "베이컨",
    "beef": "소고기",
    "bread": "식빵",
    "broccoli": "브로콜리",
    "butter": "버터",
    "cabbage": "양배추",
    "carrot": "당근",
    "cheese": "치즈",
    "chicken": "닭고기",
    "cucumber": "오이",
    "egg": "달걀",
    "eggplant": "가지",
    "fish": "생선",
    "garlic": "마늘",
    "green_onion": "대파",
    "lettuce": "양상추",
    "milk": "우유",
    "mushroom": "버섯",
    "onion": "양파",
    "pepper": "파프리카",
    "pork": "돼지고기",
    "potato": "감자",
    "sausage": "소시지",
    "spinach": "시금치",
    "tomato": "토마토",
    "yogurt": "요거트",
    "zucchini": "애호박",
}


def _ensure_recipe_schema(bind: Engine) -> None:
    inspector = inspect(bind)

    recipe_columns = {column["name"] for column in inspector.get_columns("recipes")}
    ingredient_columns = {
        column["name"] for column in inspector.get_columns("recipe_ingredients")
    }

    recipe_additions = {
        "servings": "INTEGER NOT NULL DEFAULT 1",
        "cook_time_minutes": "INTEGER NOT NULL DEFAULT 15",
        "difficulty": "VARCHAR(20) NOT NULL DEFAULT 'easy'",
        "pantry_items_text": "TEXT NOT NULL DEFAULT ''",
        "tip": "TEXT NOT NULL DEFAULT ''",
    }
    ingredient_additions = {
        "display_name": "VARCHAR(100) NOT NULL DEFAULT ''",
        "amount": "FLOAT NOT NULL DEFAULT 1",
        "unit": "VARCHAR(20) NOT NULL DEFAULT '개'",
    }

    with bind.begin() as connection:
        for column_name, definition in recipe_additions.items():
            if column_name not in recipe_columns:
                connection.execute(
                    text(f"ALTER TABLE recipes ADD COLUMN {column_name} {definition}")
                )
        for column_name, definition in ingredient_additions.items():
            if column_name not in ingredient_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE recipe_ingredients ADD COLUMN {column_name} {definition}"
                    )
                )


def _normalize_ingredient_details(recipe_payload: dict) -> list[dict]:
    ingredient_details = recipe_payload.get("ingredient_details")
    if ingredient_details:
        normalized: list[dict] = []
        for ingredient in ingredient_details:
            item_name = ingredient["item_name"].strip().lower()
            normalized.append(
                {
                    "item_name": item_name,
                    "display_name": ingredient.get(
                        "display_name",
                        FALLBACK_DISPLAY_NAMES.get(item_name, item_name),
                    ).strip(),
                    "amount": float(ingredient.get("amount", 1)),
                    "unit": ingredient.get("unit", "개").strip(),
                }
            )
        return normalized

    fallback_details = []
    for ingredient_name in recipe_payload.get("ingredients", []):
        item_name = ingredient_name.strip().lower()
        fallback_details.append(
            {
                "item_name": item_name,
                "display_name": FALLBACK_DISPLAY_NAMES.get(item_name, item_name),
                "amount": 1.0,
                "unit": "개",
            }
        )
    return fallback_details


def seed_recommendation_data(db: Session) -> None:
    _ensure_recipe_schema(db.bind)

    payload = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    recipes = payload.get("recipes", [])
    desired_keys = {
        (
            recipe_payload["liquor_name"].strip().lower(),
            int(recipe_payload.get("refresh_group", 0)),
            recipe_payload["name"].strip(),
        )
        for recipe_payload in recipes
    }

    existing_recipes = {
        (
            recipe.liquor_name,
            recipe.refresh_group,
            recipe.name,
        ): recipe
        for recipe in db.scalars(
            select(Recipe).options(selectinload(Recipe.ingredients))
        ).all()
    }

    for key, recipe in existing_recipes.items():
        if key not in desired_keys:
            db.delete(recipe)

    db.flush()

    for recipe_payload in recipes:
        key = (
            recipe_payload["liquor_name"].strip().lower(),
            int(recipe_payload.get("refresh_group", 0)),
            recipe_payload["name"].strip(),
        )

        recipe = existing_recipes.get(key)
        ingredient_details = _normalize_ingredient_details(recipe_payload)
        pantry_items = [item.strip() for item in recipe_payload.get("pantry_items", []) if item.strip()]

        if recipe is None:
            recipe = Recipe(
                liquor_name=key[0],
                refresh_group=key[1],
                name=key[2],
                reason=recipe_payload["reason"].strip(),
                instructions_text="\n".join(recipe_payload.get("recipe", [])),
                servings=int(recipe_payload.get("servings", 1)),
                cook_time_minutes=int(recipe_payload.get("cook_time_minutes", 15)),
                difficulty=recipe_payload.get("difficulty", "easy").strip(),
                pantry_items_text="\n".join(pantry_items),
                tip=recipe_payload.get("tip", "").strip(),
                rank_hint=int(recipe_payload.get("rank_hint", 0)),
            )
            db.add(recipe)
            db.flush()
        else:
            recipe.reason = recipe_payload["reason"].strip()
            recipe.instructions_text = "\n".join(recipe_payload.get("recipe", []))
            recipe.servings = int(recipe_payload.get("servings", 1))
            recipe.cook_time_minutes = int(recipe_payload.get("cook_time_minutes", 15))
            recipe.difficulty = recipe_payload.get("difficulty", "easy").strip()
            recipe.pantry_items_text = "\n".join(pantry_items)
            recipe.tip = recipe_payload.get("tip", "").strip()
            recipe.rank_hint = int(recipe_payload.get("rank_hint", 0))
            recipe.ingredients.clear()
            db.flush()

        for ingredient in ingredient_details:
            recipe.ingredients.append(
                RecipeIngredient(
                    ingredient_name=ingredient["item_name"],
                    display_name=ingredient["display_name"],
                    amount=ingredient["amount"],
                    unit=ingredient["unit"],
                )
            )

    db.commit()
