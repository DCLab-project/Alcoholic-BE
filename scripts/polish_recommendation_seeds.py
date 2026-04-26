from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT_DIR / "seeds" / "recommendations.json"

JOSA_PAIRS = ("은/는", "이/가", "을/를", "과/와")

TERMS = [
    "스파클링와인",
    "카베르네 소비뇽",
    "카베르네",
    "화이트와인",
    "레드와인",
    "피노 누아",
    "프로세코",
    "샴페인",
    "준마이",
    "긴조",
    "다이긴조",
    "니고리",
    "버번",
    "싱글몰트",
    "블렌디드",
    "피트 위스키",
    "위스키",
    "사케",
    "소주",
    "맥주",
    "와인",
    "돼지고기",
    "돼지목살",
    "돼지안심",
    "대패 목살",
    "소고기",
    "닭다리살",
    "닭안심",
    "닭고기",
    "흰살생선",
    "대구살",
    "도미살",
    "연어",
    "양송이버섯",
    "표고버섯",
    "팽이버섯",
    "느타리버섯",
    "버섯",
    "방울토마토",
    "파프리카",
    "브로콜리",
    "양배추",
    "토마토",
    "애호박",
    "시금치",
    "당근",
    "감자",
    "가지",
    "오이",
    "상추",
    "양파",
    "대파",
    "마늘",
    "달걀",
    "계란",
    "베이컨",
    "소시지",
    "버터",
    "체다 치즈",
    "모짜렐라 치즈",
    "파마산 치즈",
    "리코타 치즈",
    "치즈",
    "요거트",
    "우유",
    "빵",
]

LIQUOR_DISPLAY_NAMES = {
    "soju": "소주",
    "beer": "맥주",
    "red_wine": "레드와인",
    "white_wine": "화이트와인",
    "sparkling_wine": "스파클링와인",
    "whisky": "위스키",
    "sake": "사케",
}

STYLE_TERMS_BY_LIQUOR = {
    "red_wine": (
        "카베르네 소비뇽",
        "카베르네",
        "피노 누아",
        "메를로",
        "쉬라즈",
        "산지오베제",
        "키안티",
        "치안티",
        "말벡",
    ),
    "white_wine": (
        "소비뇽 블랑",
        "샤르도네",
        "리슬링",
        "피노 그리지오",
    ),
    "sparkling_wine": (
        "샴페인",
        "프로세코",
        "카바",
        "스파클링 로제",
        "브뤼",
    ),
    "whisky": (
        "버번",
        "싱글몰트",
        "블렌디드",
        "피트 위스키",
        "피트",
        "셰리 캐스크",
        "하이볼",
    ),
    "sake": (
        "준마이",
        "긴조",
        "다이긴조",
        "니고리",
    ),
}

STYLE_NEUTRAL_PROFILES = {
    "red_wine": "레드와인의 탄닌, 산미와 과실감",
    "white_wine": "화이트와인의 산미와 산뜻한 과실감",
    "sparkling_wine": "스파클링와인의 기포와 산미",
    "whisky": "위스키의 오크 향과 구운 곡물 느낌",
    "sake": "사케의 쌀 향과 부드러운 우마미",
}


def _has_batchim(text: str) -> bool:
    for char in reversed(text):
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            return (code - 0xAC00) % 28 != 0
    return False


def _choose_josa(text: str, pair: str) -> str:
    with_batchim, without_batchim = pair.split("/")
    return with_batchim if _has_batchim(text) else without_batchim


def _with_josa(text: str, pair: str) -> str:
    return f"{text}{_choose_josa(text, pair)}"


def _fix_particles(text: str) -> str:
    for term in sorted(set(TERMS), key=len, reverse=True):
        for pair in JOSA_PAIRS:
            left, right = pair.split("/")
            correct = _choose_josa(term, pair)
            text = text.replace(f"{term}{left}", f"{term}{correct}")
            text = text.replace(f"{term}{right}", f"{term}{correct}")
    return text


def _liquor_display(recipe: dict[str, Any]) -> str:
    return LIQUOR_DISPLAY_NAMES.get(str(recipe.get("liquor_name", "")).strip(), "이 술")


def _liquor_style_terms(recipe: dict[str, Any]) -> tuple[str, ...]:
    return STYLE_TERMS_BY_LIQUOR.get(str(recipe.get("liquor_name", "")).strip(), ())


def _neutralize_style_references(text: str, recipe: dict[str, Any]) -> str:
    liquor_key = str(recipe.get("liquor_name", "")).strip()
    liquor_name = _liquor_display(recipe)
    neutral_profile = STYLE_NEUTRAL_PROFILES.get(liquor_key, f"{liquor_name}의 전반적인 향")
    style_terms = _liquor_style_terms(recipe)
    if not style_terms:
        return text

    joined_terms = "|".join(re.escape(term) for term in sorted(style_terms, key=len, reverse=True))
    text = re.sub(
        rf"(?:{joined_terms})(?:에서 느껴지는|의) [^.!?\n]+?에 자연스럽게 어울려요",
        f"{neutral_profile}에 자연스럽게 어울려요",
        text,
    )
    text = re.sub(
        rf"특히 (?:{joined_terms})(?: 스타일)?(?:과|와) 함께하면",
        f"{_with_josa(liquor_name, '과/와')} 함께하면",
        text,
    )

    for term in sorted(style_terms, key=len, reverse=True):
        text = text.replace(term, liquor_name)

    text = text.replace(f"{liquor_name} 스타일", liquor_name)
    text = text.replace(f"{liquor_name} 계열", liquor_name)
    text = text.replace(f"{liquor_name} 급", liquor_name)
    text = text.replace(f"{liquor_name}나 {liquor_name}", liquor_name)
    text = text.replace(f"{liquor_name}이나 {liquor_name}", liquor_name)
    text = text.replace(f"{liquor_name}와 {liquor_name}", liquor_name)
    text = text.replace(f"{liquor_name}과 {liquor_name}", liquor_name)
    text = text.replace(f"특히 {_with_josa(liquor_name, '과/와')} 함께하면", f"{_with_josa(liquor_name, '과/와')} 함께하면")
    text = text.replace(f"{liquor_name} {liquor_name}", liquor_name)
    return text


def _polish_template_phrases(text: str) -> str:
    def replace_point_object(match: re.Match[str]) -> str:
        phrase = match.group(1)
        return f"{phrase}{_choose_josa(phrase, '을/를')} 살린 "

    def replace_point_subject(match: re.Match[str]) -> str:
        phrase = match.group(1)
        return f"{phrase}{_choose_josa(phrase, '이/가')} 살아 있어서"

    text = re.sub(r"([^.!?\n]+?) 포인트를 살린 ", replace_point_object, text)
    text = re.sub(r"([^.!?\n]+?) 포인트가 살아 있어서", replace_point_subject, text)
    text = text.replace("짭짤한 포인트", "짭짤한 맛")
    text = text.replace(" 포인트를", " 매력을")
    text = text.replace(" 포인트가", " 매력이")
    text = text.replace("집안주예요.", "집 안주예요.")
    text = text.replace(
        "집에서 부담 없이 만들 수 있고 한입씩 곁들이기 좋아요.",
        "냉장고 재료로 만들기 쉽고, 술 한 잔에 천천히 곁들이기 좋아요.",
    )
    for liquor in ("소주", "맥주", "레드와인", "화이트와인", "스파클링와인", "위스키", "사케"):
        text = text.replace(
            f"{liquor}용 집 안주예요.",
            f"{_with_josa(liquor, '과/와')} 잘 어울리는 집 안주예요.",
        )
    return text


def _ingredient_names(recipe: dict[str, Any], limit: int = 3) -> str:
    names = [
        detail.get("display_name", "").strip()
        for detail in recipe.get("ingredient_details", [])
        if detail.get("display_name")
    ]
    return ", ".join(names[:limit])


def _ingredient_detail_names(recipe: dict[str, Any]) -> list[str]:
    return [
        detail.get("display_name", "").strip()
        for detail in recipe.get("ingredient_details", [])
        if detail.get("display_name")
    ]


def _primary_ingredient_name(recipe: dict[str, Any]) -> str:
    names = _ingredient_detail_names(recipe)
    return names[0] if names else "주재료"


def _remaining_ingredient_names(recipe: dict[str, Any]) -> str:
    names = _ingredient_detail_names(recipe)[1:]
    return ", ".join(names) if names else "나머지 재료"


def _pantry_names(recipe: dict[str, Any]) -> str:
    pantry_items = recipe.get("pantry_item_details") or recipe.get("pantry_items") or []
    names = [item.get("name", "").strip() for item in pantry_items if item.get("name")]
    return ", ".join(names[:3]) if names else "준비한 양념"


def _seasoning_names(recipe: dict[str, Any]) -> str:
    pantry_items = recipe.get("pantry_item_details") or recipe.get("pantry_items") or []
    excluded = {"식용유", "전분", "밀가루", "부침가루"}
    names = [
        item.get("name", "").strip()
        for item in pantry_items
        if item.get("name") and item.get("name") not in excluded
    ]
    return ", ".join(names[:3]) if names else _pantry_names(recipe)


def _fat_names(recipe: dict[str, Any]) -> str:
    names: list[str] = []
    if "식용유" in _pantry_names(recipe):
        names.append("식용유")
    if any(detail.get("item_name") == "butter" for detail in recipe.get("ingredient_details", [])):
        names.append("버터")
    return " 또는 ".join(names) if names else "식용유"


def _aromatic_names(recipe: dict[str, Any]) -> str:
    names = [
        detail.get("display_name", "").strip()
        for detail in recipe.get("ingredient_details", [])
        if detail.get("item_name") in {"garlic", "onion", "green_onion"}
        and detail.get("display_name")
    ]
    return ", ".join(names[:2])


def _polish_ingredient_list_phrase(text: str, names: str) -> str:
    if not names:
        return text
    return text.replace(f"{names} 재료를", f"{names}{_choose_josa(names, '을/를')}")


def _polish_generic_recipe_words(text: str, recipe: dict[str, Any]) -> str:
    primary = _primary_ingredient_name(recipe)
    remaining = _remaining_ingredient_names(recipe)
    all_names = _ingredient_names(recipe)
    pantry_names = _seasoning_names(recipe)
    fat_names = _fat_names(recipe)
    aromatics = _aromatic_names(recipe)
    liquid = "우유" if any(
        detail.get("item_name") == "milk" for detail in recipe.get("ingredient_details", [])
    ) else "물"

    for subject in ("주재료", primary):
        text = text.replace(
            f"{subject}에 준비한 양념을 가볍게 묻혀",
            f"{primary}에 {_with_josa(pantry_names, '을/를')} 가볍게 묻혀",
        )
    text = text.replace(f"{primary}에 식용유, ", f"{primary}에 ")
    text = text.replace(
        "주재료를 넣고 앞뒤로",
        f"{_with_josa(primary, '을/를')} 넣고 앞뒤로",
    )
    text = text.replace(
        "주재료를 넣고 중불에서",
        f"{_with_josa(primary, '을/를')} 넣고 중불에서",
    )
    text = text.replace("주재료 더하기", f"{primary} 넣기")
    text = text.replace("주재료 넣기", f"{primary} 넣기")
    text = text.replace("주재료와", f"{_with_josa(primary, '과/와')}")
    text = text.replace(
        "팬에 주재료를 먼저 넣어",
        f"팬에 {_with_josa(primary, '을/를')} 먼저 넣어",
    )
    text = text.replace(
        "팬에 주재료를 먼저 볶거나",
        f"팬에 {_with_josa(primary, '을/를')} 먼저 볶거나",
    )
    text = text.replace("주재료가 익어가면", f"{_with_josa(primary, '이/가')} 익어가면")
    text = text.replace("주재료의", f"{primary}의")
    text = text.replace("나머지 재료를", f"{_with_josa(remaining, '을/를')}")
    text = text.replace("준비한 재료를", f"{_with_josa(all_names, '을/를')}")
    text = text.replace("기름이나 버터를", f"{_with_josa(fat_names, '을/를')}")
    text = text.replace("팬을 예열하고 버터를 두른 뒤", f"팬을 예열하고 {_with_josa(fat_names, '을/를')} 두른 뒤")
    text = text.replace("물이나 우유를", f"{_with_josa(liquid, '을/를')}")
    if aromatics:
        text = text.replace("향이 나는 재료", aromatics)
        text = text.replace(
            "마늘이나 양파가 있으면 먼저 넣어",
            f"{_with_josa(aromatics, '을/를')} 먼저 넣어",
        )
    else:
        text = text.replace("향이 나는 재료", all_names)
    return text


def _polish_text(text: str, recipe: dict[str, Any] | None = None) -> str:
    if recipe is not None:
        text = _neutralize_style_references(text, recipe)
        text = _polish_ingredient_list_phrase(text, _ingredient_names(recipe))
        text = _polish_generic_recipe_words(text, recipe)
    text = _polish_template_phrases(text)
    text = _fix_particles(text)
    text = text.replace("  ", " ")
    return text


def _polish_tags(recipe: dict[str, Any]) -> None:
    tags = recipe.get("tags")
    if not isinstance(tags, list):
        return
    style_terms = set(_liquor_style_terms(recipe))
    liquor_name = _liquor_display(recipe)
    polished_tags: list[str] = []
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            continue
        if tag.strip() in style_terms:
            continue
        polished_tags.append(_polish_text(tag, recipe))
    if style_terms and liquor_name not in polished_tags:
        polished_tags.append(liquor_name)
    recipe["tags"] = list(dict.fromkeys(polished_tags))


def _polish_value(value: Any, recipe: dict[str, Any] | None = None) -> Any:
    if isinstance(value, str):
        return _polish_text(value, recipe)
    if isinstance(value, list):
        return [_polish_value(item, recipe) for item in value]
    if isinstance(value, dict):
        return {key: _polish_value(item, recipe) for key, item in value.items()}
    return value


def _rebuild_legacy_recipe_steps(recipe: dict[str, Any]) -> None:
    steps = recipe.get("recipe_steps", [])
    if not isinstance(steps, list):
        return
    legacy_steps = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_number = step.get("step_number")
        title = step.get("title")
        instruction = step.get("instruction")
        if step_number and title and instruction:
            legacy_steps.append(f"{step_number}. {title}: {instruction}")
    if legacy_steps:
        recipe["recipe"] = legacy_steps


def polish_payload(payload: dict[str, Any]) -> dict[str, Any]:
    recipes = payload.get("recipes", [])
    for recipe in recipes:
        if not isinstance(recipe, dict):
            continue
        for key in (
            "reason",
            "priority_reason",
            "selection_factors",
            "pairing_knowledge",
            "recipe",
            "recipe_steps",
            "tip",
        ):
            if key in recipe:
                recipe[key] = _polish_value(recipe[key], recipe)
        _polish_tags(recipe)
        _rebuild_legacy_recipe_steps(recipe)
    return payload


def main() -> None:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    polished = polish_payload(payload)
    SEED_PATH.write_text(
        json.dumps(polished, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Polished {len(polished.get('recipes', []))} recipes in {SEED_PATH}")


if __name__ == "__main__":
    main()
