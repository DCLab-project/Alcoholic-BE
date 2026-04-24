from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = REPO_ROOT / "seeds" / "recommendations.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "recipe_catalog.md"


LIQUOR_DISPLAY_NAMES = {
    "soju": "소주",
    "beer": "맥주",
    "white_wine": "화이트와인",
    "red_wine": "레드와인",
    "whisky": "위스키",
    "sparkling_wine": "스파클링와인",
    "sake": "사케",
}


DIFFICULTY_DISPLAY_NAMES = {
    "easy": "쉬움",
    "medium": "보통",
    "hard": "어려움",
}


def load_recipes() -> list[dict]:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    recipes = payload.get("recipes", [])
    if not isinstance(recipes, list):
        raise ValueError("recommendations.json의 recipes 필드가 리스트가 아닙니다.")
    return recipes


def sort_recipes(recipes: list[dict]) -> list[dict]:
    return sorted(
        recipes,
        key=lambda recipe: (
            recipe.get("liquor_name", ""),
            recipe.get("refresh_group", 0),
            -int(recipe.get("rank_hint", 0)),
            recipe.get("name", ""),
        ),
    )


def format_amount(amount: object) -> str:
    if isinstance(amount, float) and amount.is_integer():
        return str(int(amount))
    return str(amount)


def build_catalog(recipes: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for recipe in sort_recipes(recipes):
        grouped[recipe["liquor_name"]].append(recipe)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# 레시피 카탈로그",
        "",
        "> 이 문서는 `seeds/recommendations.json`을 기준으로 자동 생성됩니다.",
        f"> 생성 시각: `{generated_at}`",
        "",
        "## 요약",
        "",
        f"- 총 레시피 수: **{len(recipes)}개**",
        "- 검수 포인트: 술-안주 매칭, 재료 현실성, 레시피 단계 구체성, 상온 양념 가정, UI 표시 적합성",
        "",
    ]

    for liquor_name, liquor_recipes in grouped.items():
        display_name = LIQUOR_DISPLAY_NAMES.get(liquor_name, liquor_name)
        lines.append(f"- `{liquor_name}` ({display_name}): {len(liquor_recipes)}개")

    lines.extend(
        [
            "",
            "## 검수 기준",
            "",
            "- `유지`: 지금 그대로 서비스에 써도 무리가 없는 레시피",
            "- `수정`: 큰 방향은 맞지만 이유/재료/스텝 표현을 다듬어야 하는 레시피",
            "- `제외`: 현재 서비스 방향이나 주류 페어링 기준에 잘 맞지 않는 레시피",
            "",
        ]
    )

    for liquor_name, liquor_recipes in grouped.items():
        display_name = LIQUOR_DISPLAY_NAMES.get(liquor_name, liquor_name)
        lines.append(f"## {display_name} (`{liquor_name}`)")
        lines.append("")
        lines.append(f"- 레시피 수: **{len(liquor_recipes)}개**")
        lines.append("")

        for index, recipe in enumerate(liquor_recipes, start=1):
            difficulty = DIFFICULTY_DISPLAY_NAMES.get(
                recipe.get("difficulty", ""), recipe.get("difficulty", "-")
            )
            servings = recipe.get("servings", "-")
            cook_time_minutes = recipe.get("cook_time_minutes", "-")
            refresh_group = recipe.get("refresh_group", 0)
            rank_hint = recipe.get("rank_hint", 0)

            lines.append(f"### {index}. {recipe['name']}")
            lines.append("")
            lines.append(f"- refresh 그룹: `{refresh_group}`")
            lines.append(f"- rank hint: `{rank_hint}`")
            lines.append(f"- 인분/시간/난이도: `{servings}인분 / {cook_time_minutes}분 / {difficulty}`")
            lines.append(f"- 추천 이유: {recipe['reason']}")
            lines.append("")
            lines.append("#### 핵심 재료")
            lines.append("")
            lines.append("| 표시명 | 내부 키 | 수량 | 단위 |")
            lines.append("| --- | --- | ---: | --- |")

            for ingredient in recipe.get("ingredient_details", []):
                lines.append(
                    "| {display_name} | `{item_name}` | {amount} | {unit} |".format(
                        display_name=ingredient.get("display_name", "-"),
                        item_name=ingredient.get("item_name", "-"),
                        amount=format_amount(ingredient.get("amount", "-")),
                        unit=ingredient.get("unit", "-"),
                    )
                )

            lines.append("")
            lines.append("#### 상온 기본 양념")
            lines.append("")
            for pantry_item in recipe.get("pantry_items", []):
                lines.append(f"- {pantry_item}")

            lines.append("")
            lines.append("#### 조리 순서")
            lines.append("")
            for step in recipe.get("recipe", []):
                lines.append(f"- {step}")

            lines.append("")
            lines.append("#### 팁")
            lines.append("")
            lines.append(f"- {recipe.get('tip', '-')}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    recipes = load_recipes()
    OUTPUT_PATH.write_text(build_catalog(recipes), encoding="utf-8")
    print(f"recipe catalog generated: {OUTPUT_PATH}")
    print(f"recipe count: {len(recipes)}")


if __name__ == "__main__":
    main()
