from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.domain.models import Recipe, RecipeIngredient  # noqa: E402
from app.seeds.recommendation_seed import seed_recommendation_data  # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_recommendation_data(db)
        recipe_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
        ingredient_count = (
            db.scalar(select(func.count()).select_from(RecipeIngredient)) or 0
        )
    finally:
        db.close()

    database_url = engine.url.render_as_string(hide_password=True)
    print(f"database initialized: {database_url}")
    print(f"recipes: {recipe_count}")
    print(f"recipe ingredients: {ingredient_count}")


if __name__ == "__main__":
    main()
