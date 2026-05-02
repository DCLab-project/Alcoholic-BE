import json
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Recipe, RecipeIngredient


SEED_FILE = Path(__file__).resolve().parents[2] / "seeds" / "recommendations.json"

FALLBACK_DISPLAY_NAMES = {
    "beef": "소고기",
    "bread": "빵",
    "broccoli": "브로콜리",
    "butter": "버터",
    "cabbage": "양배추",
    "carrot": "당근",
    "cheese": "치즈",
    "chicken": "닭고기",
    "cucumber": "오이",
    "egg": "달걀",
    "eggplant": "가지",
    "fish": "생선살",
    "garlic": "마늘",
    "leek": "대파",
    "lettuce": "상추",
    "milk": "우유",
    "mushroom": "버섯",
    "onion": "양파",
    "pepper": "파프리카",
    "pork": "돼지고기",
    "potato": "감자",
    "sausage": "소시지",
    "tomato": "토마토",
    "zucchini": "애호박",
    "lemon": "레몬",
    "avocado": "아보카도",
    "radish": "무",
    "tofu": "두부",
    "ginger": "생강",
    "salmon": "연어",
}


def _ensure_recipe_schema(bind: Engine) -> None:
    inspector = inspect(bind)
    is_mysql = bind.dialect.name in {"mysql", "mariadb"}

    recipe_columns = {column["name"] for column in inspector.get_columns("recipes")}
    ingredient_columns = {
        column["name"] for column in inspector.get_columns("recipe_ingredients")
    }

    # MySQL does not allow DEFAULT values on TEXT columns. SQLite keeps the
    # original defaults for local backward compatibility with existing DB files.
    text_definition = "TEXT NULL" if is_mysql else "TEXT NOT NULL DEFAULT ''"

    recipe_additions = {
        "servings": "INTEGER NOT NULL DEFAULT 1",
        "cook_time_minutes": "INTEGER NOT NULL DEFAULT 15",
        "difficulty": "VARCHAR(20) NOT NULL DEFAULT 'easy'",
        "pantry_items_text": text_definition,
        "pantry_item_details_text": text_definition,
        "recipe_steps_text": text_definition,
        "pairing_flavor_logic": text_definition,
        "pairing_ingredient_logic": text_definition,
        "pairing_why_this_liquor": text_definition,
        "tags_text": text_definition,
        "tip": text_definition,
    }
    ingredient_additions = {
        "display_name": "VARCHAR(100) NOT NULL DEFAULT ''",
        "variant_detail": "TEXT NOT NULL DEFAULT ''",
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


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


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
                    "variant_detail": ingredient.get("variant_detail", "").strip(),
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
                "variant_detail": "",
                "amount": 1.0,
                "unit": "개",
            }
        )
    return fallback_details


def _normalize_pantry_items(recipe_payload: dict) -> tuple[list[str], list[dict]]:
    pantry_payload = recipe_payload.get("pantry_items", [])
    pantry_text: list[str] = []
    pantry_details: list[dict] = []

    for item in pantry_payload:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            amount = float(item.get("amount", 0))
            unit = str(item.get("unit", "")).strip()
            pantry_details.append({"name": name, "amount": amount, "unit": unit})
            pantry_text.append(f"{name} {amount:g}{unit}".strip())
        else:
            pantry_line = str(item).strip()
            if pantry_line:
                pantry_text.append(pantry_line)

    return pantry_text, pantry_details


def _normalize_recipe_steps(recipe_payload: dict) -> tuple[list[str], list[dict]]:
    steps_payload = recipe_payload.get("recipe_steps")
    if steps_payload:
        step_lines: list[str] = []
        steps: list[dict] = []
        for index, step in enumerate(steps_payload, start=1):
            step_number = int(step.get("step_number", index))
            title = str(step.get("title", "")).strip()
            instruction = str(step.get("instruction", "")).strip()
            time_minutes = int(step.get("time_minutes", 0))
            heat_level = str(step.get("heat_level", "없음")).strip()
            success_cue = str(step.get("success_cue", "")).strip()
            steps.append(
                {
                    "step_number": step_number,
                    "title": title,
                    "instruction": instruction,
                    "time_minutes": time_minutes,
                    "heat_level": heat_level,
                    "success_cue": success_cue,
                }
            )
            title_part = f"{title}: " if title else ""
            step_lines.append(f"{step_number}. {title_part}{instruction}")
        return step_lines, steps

    legacy_steps = [str(step).strip() for step in recipe_payload.get("recipe", []) if str(step).strip()]
    generated_steps = [
        {
            "step_number": index,
            "title": "",
            "instruction": step,
            "time_minutes": 0,
            "heat_level": "없음",
            "success_cue": "",
        }
        for index, step in enumerate(legacy_steps, start=1)
    ]
    return legacy_steps, generated_steps


def _normalize_pairing(recipe_payload: dict) -> dict:
    pairing = recipe_payload.get("pairing_knowledge") or {}
    return {
        "flavor_logic": str(pairing.get("flavor_logic", "")).strip(),
        "ingredient_logic": str(pairing.get("ingredient_logic", "")).strip(),
        "why_this_liquor": str(pairing.get("why_this_liquor", "")).strip(),
    }


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
        pantry_items, pantry_item_details = _normalize_pantry_items(recipe_payload)
        recipe_lines, recipe_steps = _normalize_recipe_steps(recipe_payload)
        pairing = _normalize_pairing(recipe_payload)
        tags = [str(tag).strip() for tag in recipe_payload.get("tags", []) if str(tag).strip()]

        recipe_fields = {
            "liquor_name": key[0],
            "refresh_group": key[1],
            "name": key[2],
            "reason": recipe_payload["reason"].strip(),
            "instructions_text": "\n".join(recipe_lines),
            "servings": int(recipe_payload.get("servings", 1)),
            "cook_time_minutes": int(recipe_payload.get("cook_time_minutes", 15)),
            "difficulty": recipe_payload.get("difficulty", "easy").strip(),
            "pantry_items_text": "\n".join(pantry_items),
            "pantry_item_details_text": _json_dumps(pantry_item_details),
            "recipe_steps_text": _json_dumps(recipe_steps),
            "pairing_flavor_logic": pairing["flavor_logic"],
            "pairing_ingredient_logic": pairing["ingredient_logic"],
            "pairing_why_this_liquor": pairing["why_this_liquor"],
            "tags_text": _json_dumps(tags),
            "tip": recipe_payload.get("tip", "").strip(),
            "rank_hint": int(recipe_payload.get("rank_hint", 0)),
        }

        if recipe is None:
            recipe = Recipe(**recipe_fields)
            db.add(recipe)
            db.flush()
        else:
            for field_name, field_value in recipe_fields.items():
                setattr(recipe, field_name, field_value)
            recipe.ingredients.clear()
            db.flush()

        for ingredient in ingredient_details:
            recipe.ingredients.append(
                RecipeIngredient(
                    ingredient_name=ingredient["item_name"],
                    display_name=ingredient["display_name"],
                    variant_detail=ingredient["variant_detail"],
                    amount=ingredient["amount"],
                    unit=ingredient["unit"],
                )
            )

    db.commit()
