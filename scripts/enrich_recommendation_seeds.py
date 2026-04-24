import json
from pathlib import Path


SEED_FILE = Path(__file__).resolve().parents[1] / "seeds" / "recommendations.json"

INGREDIENT_META = {
    "bacon": {"display_name": "베이컨", "amount": 3, "unit": "줄"},
    "beef": {"display_name": "소고기", "amount": 180, "unit": "g"},
    "bread": {"display_name": "식빵", "amount": 2, "unit": "장"},
    "broccoli": {"display_name": "브로콜리", "amount": 120, "unit": "g"},
    "butter": {"display_name": "버터", "amount": 10, "unit": "g"},
    "cabbage": {"display_name": "양배추", "amount": 120, "unit": "g"},
    "carrot": {"display_name": "당근", "amount": 0.5, "unit": "개"},
    "cheese": {"display_name": "치즈", "amount": 2, "unit": "장"},
    "chicken": {"display_name": "닭고기", "amount": 180, "unit": "g"},
    "cucumber": {"display_name": "오이", "amount": 0.5, "unit": "개"},
    "egg": {"display_name": "달걀", "amount": 2, "unit": "개"},
    "eggplant": {"display_name": "가지", "amount": 0.5, "unit": "개"},
    "fish": {"display_name": "생선", "amount": 180, "unit": "g"},
    "garlic": {"display_name": "마늘", "amount": 2, "unit": "쪽"},
    "green_onion": {"display_name": "대파", "amount": 1, "unit": "대"},
    "lettuce": {"display_name": "양상추", "amount": 4, "unit": "장"},
    "milk": {"display_name": "우유", "amount": 150, "unit": "ml"},
    "mushroom": {"display_name": "버섯", "amount": 120, "unit": "g"},
    "onion": {"display_name": "양파", "amount": 0.5, "unit": "개"},
    "pepper": {"display_name": "파프리카", "amount": 0.5, "unit": "개"},
    "pork": {"display_name": "돼지고기", "amount": 180, "unit": "g"},
    "potato": {"display_name": "감자", "amount": 1, "unit": "개"},
    "sausage": {"display_name": "소시지", "amount": 2, "unit": "개"},
    "spinach": {"display_name": "시금치", "amount": 80, "unit": "g"},
    "tomato": {"display_name": "토마토", "amount": 1, "unit": "개"},
    "yogurt": {"display_name": "요거트", "amount": 3, "unit": "큰술"},
    "zucchini": {"display_name": "애호박", "amount": 0.5, "unit": "개"},
}

MAIN_PROTEINS = {"pork", "beef", "chicken", "fish", "sausage", "bacon", "egg"}

TIME_BY_TYPE = {
    "salad": 10,
    "muchim": 10,
    "dip": 8,
    "jeon": 15,
    "stew": 20,
    "steam": 18,
    "toast": 12,
    "grill": 15,
    "ball": 15,
    "roll": 15,
    "stir_fry": 15,
}

DIFFICULTY_BY_TYPE = {
    "salad": "easy",
    "muchim": "easy",
    "dip": "easy",
    "jeon": "medium",
    "stew": "medium",
    "steam": "medium",
    "toast": "easy",
    "grill": "easy",
    "ball": "medium",
    "roll": "medium",
    "stir_fry": "easy",
}

PANTRY_BY_TYPE = {
    "salad": ["소금 약간", "후추 약간", "올리브유 또는 식용유 1작은술"],
    "muchim": ["소금 약간", "식초 1작은술", "참기름 또는 식용유 1작은술"],
    "dip": ["소금 약간", "후추 약간"],
    "jeon": ["식용유 1큰술", "소금 약간"],
    "stew": ["식용유 1큰술", "소금 약간", "후추 약간", "물 100ml"],
    "steam": ["소금 약간", "후추 약간", "물 100ml"],
    "toast": ["버터 또는 식용유 약간", "후추 약간"],
    "grill": ["식용유 1큰술", "소금 약간", "후추 약간"],
    "ball": ["식용유 1큰술", "소금 약간", "후추 약간"],
    "roll": ["식용유 1큰술", "소금 약간", "후추 약간"],
    "stir_fry": ["식용유 1큰술", "소금 약간", "후추 약간"],
}

TIP_BY_TYPE = {
    "salad": "샐러드는 먹기 직전에 섞어야 채소 식감이 살아 있고 수분이 덜 생깁니다.",
    "muchim": "무침류는 너무 오래 두지 말고 바로 버무려야 아삭한 식감이 유지됩니다.",
    "dip": "요거트 딥은 차갑게 두었다가 내면 술과 더 산뜻하게 어울립니다.",
    "jeon": "전은 한쪽 면이 충분히 익은 뒤 뒤집어야 모양이 흐트러지지 않습니다.",
    "stew": "스튜류는 약불로 5분 이상 끓이면 재료 맛이 더 잘 어우러집니다.",
    "steam": "찜이나 은근한 조리는 센 불보다 약불로 마무리해야 재료가 부드럽습니다.",
    "toast": "토스트류는 빵을 먼저 살짝 구워야 재료를 올렸을 때 눅눅하지 않습니다.",
    "grill": "구이류는 재료를 너무 자주 뒤집지 말아야 겉면이 노릇하게 익습니다.",
    "ball": "동그랗게 뭉치는 재료는 너무 세게 누르지 않아야 식감이 살아 있습니다.",
    "roll": "달걀이나 말이류는 불을 약하게 줄이고 천천히 마무리하면 부드럽습니다.",
    "stir_fry": "볶음류는 센 불에서 짧게 끝내야 재료 식감이 살아 있고 물이 덜 생깁니다.",
}


def format_amount(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    if value == 0.5:
        return "1/2"
    return str(value)


def quantity_phrase(detail: dict) -> str:
    return f"{detail['display_name']} {format_amount(detail['amount'])}{detail['unit']}"


def quantity_topic_phrase(detail: dict) -> str:
    unit = detail["unit"]
    if unit in {"g", "ml", "큰술", "작은술", "쪽"}:
        particle = "은"
    else:
        particle = "은" if _has_batchim(unit) else "는"
    return f"{detail['display_name']} {format_amount(detail['amount'])}{unit}{particle}"


def quantity_object_phrase(detail: dict) -> str:
    unit = detail["unit"]
    if unit in {"g", "ml", "큰술", "작은술", "쪽"}:
        particle = "을"
    else:
        particle = "을" if _has_batchim(unit) else "를"
    return f"{detail['display_name']} {format_amount(detail['amount'])}{unit}{particle}"


def _has_batchim(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    target = stripped[-1]
    if "가" <= target <= "힣":
        return (ord(target) - ord("가")) % 28 != 0
    return False


def with_object_particle(text: str) -> str:
    return text + ("을" if _has_batchim(text) else "를")


def with_topic_particle(text: str) -> str:
    return text + ("은" if _has_batchim(text) else "는")


def classify(recipe_name: str) -> str:
    if "샐러드" in recipe_name:
        return "salad"
    if "무침" in recipe_name:
        return "muchim"
    if "딥" in recipe_name:
        return "dip"
    if "전" in recipe_name:
        return "jeon"
    if "스튜" in recipe_name:
        return "stew"
    if "찜" in recipe_name:
        return "steam"
    if "토스트" in recipe_name or "카나페" in recipe_name:
        return "toast"
    if "구이" in recipe_name:
        return "grill"
    if "볼" in recipe_name:
        return "ball"
    if "말이풍" in recipe_name:
        return "roll"
    return "stir_fry"


def prep_phrase(detail: dict) -> str:
    item_name = detail["item_name"]
    quantity = quantity_topic_phrase(detail)
    if item_name == "green_onion":
        return f"{quantity} 4~5cm 길이로 썬다"
    if item_name == "onion":
        return f"{quantity} 채 썬다"
    if item_name == "garlic":
        return f"{quantity} 편썬다"
    if item_name == "cucumber":
        return f"{quantity} 반달 모양으로 썬다"
    if item_name == "tomato":
        return f"{quantity} 한입 크기로 썬다"
    if item_name == "potato":
        return f"{quantity} 얇게 썰거나 채 썬다"
    if item_name == "broccoli":
        return f"{quantity} 한입 크기로 나눈다"
    if item_name == "mushroom":
        return f"{quantity} 밑동을 정리해 먹기 좋게 썬다"
    if item_name == "cabbage":
        return f"{quantity} 굵게 채 썬다"
    if item_name == "lettuce":
        return f"{quantity} 손으로 큼직하게 뜯는다"
    if item_name == "spinach":
        return f"{quantity} 씻어 물기를 턴다"
    if item_name == "zucchini":
        return f"{quantity} 반달 모양으로 썬다"
    if item_name == "eggplant":
        return f"{quantity} 길쭉하게 썬다"
    if item_name == "carrot":
        return f"{quantity} 가늘게 채 썬다"
    if item_name in {"pork", "beef", "chicken", "fish"}:
        return f"{quantity} 한입 크기로 손질한다"
    if item_name == "sausage":
        return f"{quantity} 어슷하게 썬다"
    if item_name == "bacon":
        return f"{quantity} 2~3등분한다"
    if item_name == "egg":
        return f"{quantity} 풀어둔다"
    if item_name == "bread":
        return f"{quantity} 먹기 좋게 준비한다"
    if item_name == "cheese":
        return f"{quantity} 올리기 좋게 뜯거나 자른다"
    if item_name == "butter":
        return f"{quantity} 실온에 잠시 두어 부드럽게 한다"
    if item_name == "milk":
        return f"{quantity} 미리 계량해 둔다"
    if item_name == "yogurt":
        return f"{quantity} 볼에 덜어둔다"
    return f"{quantity} 먹기 좋게 손질한다"


def build_prep_sentence(details: list[dict]) -> str:
    phrases = [prep_phrase(detail) for detail in details[:3]]
    if len(details) > 3:
        phrases.append("나머지 재료도 같은 크기로 정리한다")
    return "1: " + ", ".join(phrases) + "."


def first_main(details: list[dict]) -> dict:
    for detail in details:
        if detail["item_name"] in MAIN_PROTEINS or detail["item_name"] in {
            "potato",
            "mushroom",
            "broccoli",
        }:
            return detail
    return details[0]


def remaining_names(details: list[dict], exclude_name: str) -> str:
    names = [detail["display_name"] for detail in details if detail["item_name"] != exclude_name]
    return ", ".join(names[:2]) if names else "나머지 재료"


def build_steps(recipe_name: str, details: list[dict], recipe_type: str) -> list[str]:
    main = first_main(details)
    main_phrase = quantity_phrase(main)
    rest_phrase = remaining_names(details, main["item_name"])
    steps = [build_prep_sentence(details)]

    if recipe_type == "salad":
        steps.append(f"2: 볼에 {main_phrase}과 {rest_phrase}를 담고 가볍게 섞는다.")
        steps.append("3: 소금, 후추, 오일을 넣고 살짝 버무린다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 먹기 직전에 치즈나 요거트를 곁들여 마무리한다.")
    elif recipe_type == "muchim":
        if main["item_name"] in MAIN_PROTEINS:
            steps.append(f"2: 팬에 기름을 두르고 {main_phrase}을 2~3분 익힌다.")
            steps.append(f"3: {rest_phrase}를 넣고 식초와 기름을 더해 가볍게 버무린다.")
        else:
            steps.append(f"2: 볼에 {main_phrase}과 {rest_phrase}를 담는다.")
            steps.append("3: 소금, 식초, 기름을 넣고 빠르게 버무린다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 물이 생기기 전에 바로 낸다.")
    elif recipe_type == "dip":
        steps.append("2: 볼에 요거트와 소금, 후추를 넣고 부드럽게 섞는다.")
        steps.append(f"3: 손질한 {rest_phrase}를 넣어 농도를 맞춘다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 차갑게 두었다가 빵이나 채소와 함께 낸다.")
    elif recipe_type == "jeon":
        steps.append(f"2: 풀어둔 달걀에 {rest_phrase}를 넣어 반죽을 만든다.")
        steps.append("3: 팬에 기름을 두르고 앞뒤로 2~3분씩 노릇하게 익힌다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 한입 크기로 잘라 따뜻할 때 낸다.")
    elif recipe_type == "stew":
        steps.append(f"2: 냄비에 기름을 두르고 {main_phrase}과 양파류를 먼저 볶는다.")
        steps.append("3: 토마토나 우유, 물을 넣고 5~8분 정도 은근하게 끓인다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 마지막에 간을 맞춰 걸쭉하게 마무리한다.")
    elif recipe_type == "steam":
        steps.append(f"2: 냄비나 팬에 {main_phrase}을 올리고 대파나 버섯을 곁들인다.")
        steps.append("3: 물을 약간 두르고 뚜껑을 덮어 6~8분 정도 익힌다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 불을 끈 뒤 한 번 더 뜸을 들여 낸다.")
    elif recipe_type == "toast":
        steps.append("2: 빵을 먼저 가볍게 굽거나 팬에 노릇하게 익힌다.")
        steps.append(
            f"3: {with_object_particle(main_phrase)} 올리고 {rest_phrase}를 더해 치즈나 버터로 마무리한다."
        )
        steps.append(f"4: {with_topic_particle(recipe_name)} 한입 크기로 잘라 바로 낸다.")
    elif recipe_type == "grill":
        steps.append(f"2: 팬에 기름을 두르고 {quantity_object_phrase(main)} 먼저 굽는다.")
        steps.append(f"3: {rest_phrase}를 올리거나 곁들여 2분 정도 더 익힌다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 겉면이 노릇할 때 불을 끄고 바로 낸다.")
    elif recipe_type == "ball":
        steps.append(
            f"2: 삶거나 익힌 재료와 {quantity_object_phrase(main)} 한데 섞어 가볍게 뭉친다."
        )
        steps.append("3: 팬에 굴리듯 익히거나 팬에서 노릇하게 마무리한다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 한입 크기로 담아낸다.")
    elif recipe_type == "roll":
        steps.append(
            f"2: 팬에 기름을 두르고 {quantity_object_phrase(main)} 버섯·채소와 함께 먼저 볶는다."
        )
        steps.append("3: 달걀을 넣고 약불에서 익히며 모양을 잡는다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 촉촉함이 남을 때 불을 끄고 낸다.")
    else:
        steps.append(f"2: 팬에 기름을 두르고 {quantity_object_phrase(main)} 먼저 2~3분 볶는다.")
        steps.append(f"3: {with_object_particle(rest_phrase)} 넣고 1~2분 더 볶아 간을 맞춘다.")
        steps.append(f"4: {with_topic_particle(recipe_name)} 센 불에서 빠르게 마무리해 낸다.")

    return steps


def enrich() -> None:
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    for recipe in data["recipes"]:
        recipe_type = classify(recipe["name"])
        ingredient_details = []

        for item_name in recipe["ingredients"]:
            meta = INGREDIENT_META[item_name]
            ingredient_details.append(
                {
                    "item_name": item_name,
                    "display_name": meta["display_name"],
                    "amount": meta["amount"],
                    "unit": meta["unit"],
                }
            )

        recipe["servings"] = 1
        recipe["cook_time_minutes"] = TIME_BY_TYPE[recipe_type]
        recipe["difficulty"] = DIFFICULTY_BY_TYPE[recipe_type]
        recipe["ingredient_details"] = ingredient_details
        recipe["pantry_items"] = PANTRY_BY_TYPE[recipe_type]
        recipe["tip"] = TIP_BY_TYPE[recipe_type]
        recipe["recipe"] = build_steps(recipe["name"], ingredient_details, recipe_type)

    SEED_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    enrich()
