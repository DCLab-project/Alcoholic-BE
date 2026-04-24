import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Recipe, RecipeIngredient


SEED_FILE = Path(__file__).resolve().parents[2] / "seeds" / "recommendations.json"


def seed_recommendation_data(db: Session) -> None:
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
        if recipe is None:
            recipe = Recipe(
                liquor_name=key[0],
                refresh_group=key[1],
                name=key[2],
                reason=recipe_payload["reason"].strip(),
                instructions_text="\n".join(recipe_payload.get("recipe", [])),
                rank_hint=int(recipe_payload.get("rank_hint", 0)),
            )
            db.add(recipe)
            db.flush()
        else:
            recipe.reason = recipe_payload["reason"].strip()
            recipe.instructions_text = "\n".join(recipe_payload.get("recipe", []))
            recipe.rank_hint = int(recipe_payload.get("rank_hint", 0))
            recipe.ingredients.clear()
            db.flush()

        for ingredient_name in recipe_payload.get("ingredients", []):
            recipe.ingredients.append(
                RecipeIngredient(
                    ingredient_name=ingredient_name.strip().lower(),
                )
            )

    db.commit()
