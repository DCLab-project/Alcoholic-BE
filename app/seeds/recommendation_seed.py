import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import Recipe, RecipeIngredient


SEED_FILE = Path(__file__).resolve().parents[2] / "seeds" / "recommendations.json"


def seed_recommendation_data(db: Session) -> None:
    existing_recipe_id = db.scalar(select(Recipe.id).limit(1))
    if existing_recipe_id is not None:
        return

    payload = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    recipes = payload.get("recipes", [])

    for recipe_payload in recipes:
        recipe = Recipe(
            liquor_name=recipe_payload["liquor_name"].strip().lower(),
            refresh_group=int(recipe_payload.get("refresh_group", 0)),
            name=recipe_payload["name"].strip(),
            reason=recipe_payload["reason"].strip(),
            instructions_text="\n".join(recipe_payload.get("recipe", [])),
            rank_hint=int(recipe_payload.get("rank_hint", 0)),
        )
        db.add(recipe)
        db.flush()

        for ingredient_name in recipe_payload.get("ingredients", []):
            db.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_name=ingredient_name.strip().lower(),
                )
            )

    db.commit()

