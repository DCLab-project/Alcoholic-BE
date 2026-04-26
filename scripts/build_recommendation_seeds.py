from __future__ import annotations

import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from polish_recommendation_seeds import polish_payload


ROOT_DIR = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT_DIR / "seeds" / "recommendations.json"

ALLOWED_KEYS = {
    "bacon",
    "beef",
    "bread",
    "broccoli",
    "butter",
    "cabbage",
    "carrot",
    "cheese",
    "chicken",
    "cucumber",
    "egg",
    "eggplant",
    "fish",
    "garlic",
    "green_onion",
    "lettuce",
    "milk",
    "mushroom",
    "onion",
    "pepper",
    "pork",
    "potato",
    "sausage",
    "spinach",
    "tomato",
    "yogurt",
    "zucchini",
}

PANTRY_ALLOWED = {
    "소금",
    "후추",
    "식용유",
    "간장",
    "식초",
    "설탕",
    "올리고당",
    "마요네즈",
    "머스터드",
    "케첩",
    "굴소스",
    "레몬즙",
    "파슬리 가루",
    "허브 시즈닝",
    "전분",
    "부침가루",
    "밀가루",
}

HEAT_LEVELS = {"없음", "약불", "중불", "중강불", "센 불"}

INGREDIENT_DEFAULTS: dict[str, dict[str, Any]] = {
    "bacon": {"display_name": "베이컨", "variant_detail": "얇은 슬라이스 베이컨", "amount": 3, "unit": "줄"},
    "beef": {"display_name": "소고기", "variant_detail": "구이용 채끝 또는 등심", "amount": 200, "unit": "g"},
    "bread": {"display_name": "빵", "variant_detail": "얇게 자른 바게트 또는 식빵", "amount": 3, "unit": "조각"},
    "broccoli": {"display_name": "브로콜리", "variant_detail": "작은 송이로 자른 생브로콜리", "amount": 120, "unit": "g"},
    "butter": {"display_name": "버터", "variant_detail": "무염 버터", "amount": 12, "unit": "g"},
    "cabbage": {"display_name": "양배추", "variant_detail": "심지를 제거한 양배추 잎", "amount": 160, "unit": "g"},
    "carrot": {"display_name": "당근", "variant_detail": "단단한 세척 당근", "amount": 0.5, "unit": "개"},
    "cheese": {"display_name": "모짜렐라 치즈", "variant_detail": "슈레드 모짜렐라 치즈", "amount": 50, "unit": "g"},
    "chicken": {"display_name": "닭고기", "variant_detail": "뼈 없는 닭다리살 정육", "amount": 220, "unit": "g"},
    "cucumber": {"display_name": "오이", "variant_detail": "아삭한 백오이", "amount": 1, "unit": "개"},
    "egg": {"display_name": "달걀", "variant_detail": "신선한 대란", "amount": 2, "unit": "개"},
    "eggplant": {"display_name": "가지", "variant_detail": "탄력 있는 보라색 생가지", "amount": 1, "unit": "개"},
    "fish": {"display_name": "흰살생선", "variant_detail": "가시 없는 대구살 또는 동태살 순살", "amount": 160, "unit": "g"},
    "garlic": {"display_name": "마늘", "variant_detail": "생마늘을 편 썰어 사용", "amount": 3, "unit": "쪽"},
    "green_onion": {"display_name": "대파", "variant_detail": "흰 부분 중심의 굵은 대파", "amount": 0.5, "unit": "대"},
    "lettuce": {"display_name": "상추", "variant_detail": "컵처럼 말기 좋은 청상추", "amount": 5, "unit": "장"},
    "milk": {"display_name": "우유", "variant_detail": "일반 흰 우유", "amount": 80, "unit": "ml"},
    "mushroom": {"display_name": "양송이버섯", "variant_detail": "신선한 흰 양송이버섯", "amount": 5, "unit": "개"},
    "onion": {"display_name": "양파", "variant_detail": "단단한 흰 양파", "amount": 0.5, "unit": "개"},
    "pepper": {"display_name": "파프리카", "variant_detail": "빨간 파프리카와 노란 파프리카", "amount": 0.5, "unit": "개"},
    "pork": {"display_name": "돼지고기", "variant_detail": "구이용 돼지목살 또는 앞다리살", "amount": 220, "unit": "g"},
    "potato": {"display_name": "감자", "variant_detail": "포슬하게 익는 수미감자", "amount": 1, "unit": "개"},
    "sausage": {"display_name": "소시지", "variant_detail": "돈육 함량이 높은 비엔나 소시지", "amount": 6, "unit": "개"},
    "spinach": {"display_name": "시금치", "variant_detail": "잎이 연한 시금치", "amount": 80, "unit": "g"},
    "tomato": {"display_name": "토마토", "variant_detail": "붉게 익은 완숙 토마토", "amount": 1, "unit": "개"},
    "yogurt": {"display_name": "플레인 요거트", "variant_detail": "무가당 플레인 요거트", "amount": 3, "unit": "큰술"},
    "zucchini": {"display_name": "애호박", "variant_detail": "씨가 적고 단단한 애호박", "amount": 0.5, "unit": "개"},
}

PANTRY_SETS: dict[str, list[dict[str, Any]]] = {
    "salt": [
        {"name": "식용유", "amount": 1, "unit": "큰술"},
        {"name": "소금", "amount": 0.3, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "soy": [
        {"name": "간장", "amount": 1.5, "unit": "큰술"},
        {"name": "올리고당", "amount": 1, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "herb": [
        {"name": "식용유", "amount": 1, "unit": "큰술"},
        {"name": "소금", "amount": 0.3, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
        {"name": "허브 시즈닝", "amount": 0.4, "unit": "작은술"},
    ],
    "lemon": [
        {"name": "레몬즙", "amount": 1, "unit": "큰술"},
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
        {"name": "후추", "amount": 0.1, "unit": "작은술"},
    ],
    "vinegar": [
        {"name": "식초", "amount": 1.5, "unit": "큰술"},
        {"name": "설탕", "amount": 0.5, "unit": "작은술"},
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
    ],
    "mayo": [
        {"name": "마요네즈", "amount": 1.5, "unit": "큰술"},
        {"name": "레몬즙", "amount": 0.5, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "mustard": [
        {"name": "마요네즈", "amount": 1, "unit": "큰술"},
        {"name": "머스터드", "amount": 1, "unit": "작은술"},
        {"name": "레몬즙", "amount": 0.5, "unit": "작은술"},
    ],
    "ketchup": [
        {"name": "케첩", "amount": 1.5, "unit": "큰술"},
        {"name": "머스터드", "amount": 0.5, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "oyster": [
        {"name": "굴소스", "amount": 1, "unit": "큰술"},
        {"name": "간장", "amount": 0.5, "unit": "큰술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "starch": [
        {"name": "전분", "amount": 2, "unit": "큰술"},
        {"name": "식용유", "amount": 1.5, "unit": "큰술"},
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
    ],
    "flour": [
        {"name": "밀가루", "amount": 1, "unit": "큰술"},
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "pancake": [
        {"name": "부침가루", "amount": 2, "unit": "큰술"},
        {"name": "식용유", "amount": 2, "unit": "큰술"},
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
    ],
    "cream": [
        {"name": "밀가루", "amount": 1, "unit": "작은술"},
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
    ],
    "parsley": [
        {"name": "소금", "amount": 0.2, "unit": "작은술"},
        {"name": "후추", "amount": 0.2, "unit": "작은술"},
        {"name": "파슬리 가루", "amount": 0.3, "unit": "작은술"},
    ],
}

LIQUOR_PROFILES = {
    "soju": {
        "display": "소주",
        "styles": {
            "클린 소주": "깔끔한 끝맛",
            "차가운 소주": "시원한 목넘김",
            "부드러운 소주": "둥근 단맛",
        },
        "why": "짭조름한 감칠맛과 따뜻한 집밥형 안주를 산뜻하게 정리해줘요.",
    },
    "beer": {
        "display": "맥주",
        "styles": {
            "라거": "청량한 탄산과 가벼운 몰트감",
            "페일에일": "은은한 홉 향과 고소한 여운",
            "밀맥주": "부드러운 곡물 향과 산뜻한 기포",
        },
        "why": "바삭함과 짭짤함을 기포로 씻어줘서 한입씩 계속 먹기 좋아요.",
    },
    "white_wine": {
        "display": "화이트와인",
        "styles": {
            "소비뇽 블랑": "상큼한 산미와 허브 향",
            "샤르도네": "둥근 바디감과 부드러운 과실향",
            "리슬링": "은은한 단맛과 깨끗한 산미",
        },
        "why": "담백한 단백질과 신선한 채소의 향을 살리면서 끝맛을 가볍게 만들어줘요.",
    },
    "red_wine": {
        "display": "레드와인",
        "styles": {
            "카베르네 소비뇽": "탄닌과 묵직한 바디감",
            "메를로": "부드러운 질감과 검붉은 과실향",
            "피노 누아": "섬세한 산미와 붉은 과실향",
            "쉬라즈": "후추 뉘앙스와 진한 구운 향",
        },
        "why": "구운 고기, 토마토 산미, 버섯 우마미를 탄닌과 과실감으로 안정감 있게 받아줘요.",
    },
    "whisky": {
        "display": "위스키",
        "styles": {
            "버번": "바닐라와 오크의 달콤한 향",
            "싱글몰트": "곡물감과 긴 여운",
            "블렌디드": "부드러운 단맛과 균형감",
            "피트 위스키": "훈연감과 스모키한 향",
        },
        "why": "농축된 구운 향과 단짠 풍미를 긴 여운으로 받아줘서 천천히 즐기기 좋아요.",
    },
    "sparkling_wine": {
        "display": "스파클링와인",
        "styles": {
            "프로세코": "가벼운 과실향과 산뜻한 기포",
            "카바": "드라이한 산미와 고소한 효모향",
            "샴페인": "섬세한 기포와 미네랄감",
            "스파클링 로제": "화사한 베리 향과 산미",
        },
        "why": "기포와 산미가 치즈, 달걀, 생선, 채소의 끝맛을 산뜻하게 정리해줘요.",
    },
    "sake": {
        "display": "사케",
        "styles": {
            "준마이": "쌀 향과 우마미",
            "긴조": "화사한 향과 깔끔한 산미",
            "다이긴조": "섬세한 향과 맑은 여운",
            "니고리": "부드러운 질감과 은은한 단맛",
        },
        "why": "간장 향, 버섯 감칠맛, 담백한 단백질을 부드럽게 이어줘요.",
    },
}

STYLE_CYCLES = {liquor: list(profile["styles"]) for liquor, profile in LIQUOR_PROFILES.items()}

METHOD_TIME = {
    "팬구이": 16,
    "구이": 16,
    "에어프라이어": 18,
    "볶음": 13,
    "조림": 20,
    "찜": 21,
    "탕": 22,
    "전골": 28,
    "스튜": 28,
    "수프": 20,
    "샐러드": 12,
    "무침": 12,
    "전": 15,
    "딥": 18,
    "오픈샌드": 13,
    "꼬치구이": 19,
    "그라탕": 20,
    "말이구이": 17,
    "달걀말이": 15,
    "달걀찜": 14,
}


def ing(
    key: str,
    amount: float | int | None = None,
    unit: str | None = None,
    *,
    display_name: str | None = None,
    variant_detail: str | None = None,
) -> dict[str, Any]:
    item = deepcopy(INGREDIENT_DEFAULTS[key])
    item["item_name"] = key
    if amount is not None:
        item["amount"] = amount
    if unit is not None:
        item["unit"] = unit
    if display_name is not None:
        item["display_name"] = display_name
    if variant_detail is not None:
        item["variant_detail"] = variant_detail
    return item


def pantry(name: str, amount: float | int, unit: str) -> dict[str, Any]:
    return {"name": name, "amount": amount, "unit": unit}


def pantry_set(*names: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for name in names:
        items.extend(deepcopy(PANTRY_SETS[name]))
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        if item["name"] in seen:
            continue
        seen.add(item["name"])
        deduped.append(item)
    return deduped


def recipe_spec(
    name: str,
    method: str,
    rank_hint: int,
    refresh_group: int,
    ingredients: list[dict[str, Any]],
    pantry_key: str | tuple[str, ...],
    vibe: str,
    tags: list[str],
    *,
    servings: int = 1,
    difficulty: str | None = None,
    style: str | None = None,
    tip: str | None = None,
) -> dict[str, Any]:
    pantry_items = pantry_set(*(pantry_key if isinstance(pantry_key, tuple) else (pantry_key,)))
    if difficulty is None:
        difficulty = "medium" if method in {"조림", "찜", "스튜", "전골", "그라탕", "말이구이", "꼬치구이", "달걀말이", "달걀찜"} else "easy"
    return {
        "name": name,
        "method": method,
        "rank_hint": rank_hint,
        "refresh_group": refresh_group,
        "ingredient_details": ingredients,
        "pantry_items": pantry_items,
        "vibe": vibe,
        "tags": tags,
        "servings": servings,
        "cook_time_minutes": METHOD_TIME[method],
        "difficulty": difficulty,
        "style": style,
        "tip": tip,
    }


def ingredient_names(spec: dict[str, Any], limit: int = 3) -> str:
    return ", ".join(item["display_name"] for item in spec["ingredient_details"][:limit])


def first_name(spec: dict[str, Any]) -> str:
    return spec["ingredient_details"][0]["display_name"]


def tip_for(spec: dict[str, Any]) -> str:
    if spec.get("tip"):
        return spec["tip"]
    method = spec["method"]
    main = first_name(spec)
    tips = {
        "팬구이": f"{main}은 팬을 충분히 예열한 뒤 올려야 물이 덜 나오고 구운 향이 선명해져요.",
        "구이": f"{main}은 겉면에 먼저 색을 내면 술과 잘 맞는 고소한 향이 더 또렷해져요.",
        "에어프라이어": "재료를 겹치지 않게 펼치면 수분이 덜 차고 가장자리가 더 맛있게 구워져요.",
        "볶음": "양념은 마지막에 넣고 짧게 섞어야 재료의 식감과 향이 살아나요.",
        "조림": "소스가 거의 남지 않을 때까지 졸이면 한입씩 먹기 좋은 농축된 안주가 돼요.",
        "찜": "뚜껑을 자주 열지 않아야 재료의 수분과 향이 빠지지 않고 촉촉하게 익어요.",
        "탕": "생선이나 고기를 넣은 뒤 세게 젓지 않으면 국물이 맑고 깔끔하게 유지돼요.",
        "전골": "버섯과 채소를 먼저 끓여 단맛을 낸 뒤 단백질을 넣으면 국물이 탁해지지 않아요.",
        "스튜": "토마토나 양파는 먼저 볶아 수분을 날리면 짧게 끓여도 맛이 진해져요.",
        "수프": "우유를 넣은 뒤에는 약불로 유지해야 분리되지 않고 부드럽게 완성돼요.",
        "샐러드": "채소 물기를 충분히 빼야 드레싱이 묽어지지 않고 마지막까지 산뜻해요.",
        "무침": "먹기 직전에 버무리면 재료의 아삭함과 산미가 가장 깔끔하게 살아나요.",
        "전": "가루옷은 얇게 묻혀야 주재료의 단맛과 식감이 묻히지 않아요.",
        "딥": "딥은 조금 되직하게 만들어야 빵이나 채소에 올렸을 때 흐르지 않아요.",
        "오픈샌드": "빵은 먼저 바삭하게 구워야 토핑을 올려도 쉽게 눅눅해지지 않아요.",
        "꼬치구이": "재료 크기를 비슷하게 맞추면 겉만 타지 않고 속까지 고르게 익어요.",
        "그라탕": "치즈를 올리기 전 재료의 수분을 줄이면 완성 후 물이 덜 생겨요.",
        "말이구이": "말이의 이음새를 먼저 구우면 뒤집을 때 풀리지 않아 모양이 깔끔해요.",
        "달걀말이": "달걀물이 완전히 마르기 전에 말아야 층이 잘 붙고 촉촉하게 완성돼요.",
        "달걀찜": "물이 끓은 뒤에는 약불로 낮춰야 큰 구멍 없이 부드럽게 익어요.",
    }
    return tips[method]


def build_steps(spec: dict[str, Any]) -> list[dict[str, Any]]:
    method = spec["method"]
    names = ingredient_names(spec)
    main = first_name(spec)
    pantry_names = ", ".join(item["name"] for item in spec["pantry_items"][:3])

    def step(number: int, title: str, instruction: str, minutes: int, heat: str, cue: str) -> dict[str, Any]:
        return {
            "step_number": number,
            "title": title,
            "instruction": instruction,
            "time_minutes": minutes,
            "heat_level": heat,
            "success_cue": cue,
        }

    common_prep = step(
        1,
        "재료 손질",
        f"{names} 재료를 먹기 좋은 크기로 준비하고, 물기가 있는 재료는 키친타월로 가볍게 눌러주세요.",
        3,
        "없음",
        "재료 크기가 비슷하고 표면 물기가 많지 않으면 좋아요.",
    )

    if method in {"팬구이", "구이"}:
        return [
            common_prep,
            step(2, "밑간하기", "주재료에 준비한 양념을 가볍게 묻혀 2분 정도 두세요.", 2, "없음", "표면에 간이 얇게 고르게 붙어 있으면 좋아요."),
            step(3, "향내기", "팬을 예열하고 기름이나 버터를 두른 뒤 마늘이나 양파가 있으면 먼저 넣어 향을 내주세요.", 3, "중불", "마늘 가장자리가 연한 갈색이고 향이 올라오면 좋아요."),
            step(4, "굽기", "주재료를 넣고 앞뒤로 색이 나도록 구워주세요.", 6, "중강불", "겉면에 노릇한 구운 자국이 생기면 좋아요."),
            step(5, "마무리", "불을 줄이거나 끄고 남은 양념을 넣어 재료에 가볍게 입힌 뒤 바로 담아주세요.", 2, "약불", "재료 표면에 윤기가 돌고 팬 바닥에 물이 많이 남지 않으면 좋아요."),
        ]

    if method == "에어프라이어":
        return [
            common_prep,
            step(2, "시즈닝", "준비한 양념을 재료 표면에 고르게 묻혀주세요.", 2, "없음", "재료 겉면에 양념이 얇게 붙어 있으면 좋아요."),
            step(3, "바스켓에 담기", "에어프라이어 바스켓에 재료를 겹치지 않게 펼쳐 담아주세요.", 2, "없음", "재료 사이에 작은 틈이 있어야 열이 잘 돌아요."),
            step(4, "굽기", "180도에서 8~12분 구워주세요. 중간에 한 번 뒤집으면 더 고르게 익어요.", 10, "없음", "가장자리가 노릇하고 속까지 따뜻하게 익으면 좋아요."),
            step(5, "한김 식히기", "꺼낸 뒤 1분 정도 두었다가 접시에 담아주세요.", 1, "없음", "표면의 수분이 날아가고 집어 먹기 좋은 온도면 좋아요."),
        ]

    if method == "볶음":
        return [
            common_prep,
            step(2, "양념 준비", "작은 그릇에 양념 재료를 미리 섞어주세요.", 2, "없음", "양념이 뭉치지 않고 균일하게 섞이면 좋아요."),
            step(3, "먼저 볶기", "팬을 달군 뒤 단단한 재료나 고기부터 넣어 겉면을 익혀주세요.", 4, "중강불", "재료에서 고소한 향이 나고 겉면 색이 변하면 좋아요."),
            step(4, "함께 볶기", "나머지 재료를 넣고 수분이 많이 생기지 않게 짧게 볶아주세요.", 3, "중불", "채소는 숨이 살짝 죽고 중심 식감은 남아 있으면 좋아요."),
            step(5, "양념 코팅", "준비한 양념을 넣고 센 불에서 빠르게 섞어 마무리해주세요.", 2, "센 불", "팬 바닥에 물이 흥건하지 않고 재료에 윤기가 돌면 좋아요."),
        ]

    if method == "조림":
        return [
            common_prep,
            step(2, "겉면 굽기", "팬에 주재료를 먼저 넣어 겉면에 색을 내주세요.", 4, "중강불", "겉면이 살짝 단단해지고 구운 향이 나면 좋아요."),
            step(3, "양념 넣기", "준비한 양념과 물 4~5큰술을 넣고 재료를 고르게 섞어주세요.", 2, "중불", "양념이 재료 사이에 고르게 퍼지면 좋아요."),
            step(4, "자작하게 조리기", "뚜껑을 덮거나 약불로 낮춰 속까지 익히며 소스를 줄여주세요.", 8, "약불", "소스가 반 이상 줄고 재료에 간이 배면 좋아요."),
            step(5, "윤기 내기", "마지막에는 뚜껑을 열고 1~2분 더 굴려가며 윤기를 내주세요.", 2, "중불", "소스가 재료에 얇게 붙고 팬 바닥에 조금만 남으면 좋아요."),
        ]

    if method == "찜":
        return [
            common_prep,
            step(2, "층 만들기", "냄비나 내열 용기에 단단한 재료를 아래에 깔고 부드러운 재료를 위에 올려주세요.", 3, "없음", "재료가 한쪽으로 몰리지 않고 고르게 담기면 좋아요."),
            step(3, "수분 더하기", "준비한 양념과 물 4~6큰술을 넣어 촉촉하게 익을 준비를 해주세요.", 2, "없음", "바닥에 얇게 수분이 깔려 있으면 좋아요."),
            step(4, "뚜껑 덮어 익히기", "뚜껑을 덮고 재료가 속까지 익도록 천천히 쪄주세요.", 10, "중불", "단백질은 붉은빛이 사라지고 채소는 부드러워지면 좋아요."),
            step(5, "가볍게 정리", "뚜껑을 열어 남은 수분을 1분 정도 날린 뒤 접시에 담아주세요.", 2, "약불", "국물이 과하게 흥건하지 않고 촉촉함만 남으면 좋아요."),
        ]

    if method in {"탕", "전골"}:
        return [
            common_prep,
            step(2, "맑은 국물 시작", "냄비에 물을 넣고 향을 낼 채소나 마늘을 먼저 끓여주세요.", 6, "센 불", "물이 끓고 채소 향이 은은하게 올라오면 좋아요."),
            step(3, "주재료 넣기", "주재료를 넣고 중불에서 익히며 떠오르는 거품은 걷어주세요.", 7, "중불", "국물이 탁하지 않고 주재료가 익어가면 좋아요."),
            step(4, "간 맞추기", f"{pantry_names}로 간을 맞추고 나머지 재료를 넣어 한 번 더 끓여주세요.", 5, "약불", "짠맛이 튀지 않고 국물 맛이 맑으면 좋아요."),
            step(5, "담아내기", "불을 끄고 1분 정도 안정시킨 뒤 그릇에 담아주세요.", 1, "없음", "국물이 맑고 재료 모양이 무너지지 않으면 좋아요."),
        ]

    if method in {"스튜", "수프"}:
        return [
            common_prep,
            step(2, "기본 재료 볶기", "냄비에 기름이나 버터를 두르고 향이 나는 재료를 먼저 볶아주세요.", 4, "중불", "양파나 마늘 향이 부드럽게 올라오면 좋아요."),
            step(3, "주재료 더하기", "주재료와 나머지 재료를 넣고 겉면이 살짝 익도록 섞어주세요.", 4, "중강불", "재료 표면에 윤기가 돌고 구운 향이 나면 좋아요."),
            step(4, "끓이기", "물이나 우유를 넣고 재료가 부드러워질 때까지 끓여주세요.", 12, "중불", "감자나 고기가 젓가락으로 쉽게 들어갈 정도면 좋아요."),
            step(5, "농도 맞추기", f"{pantry_names}로 간을 맞추고 원하는 농도까지 2~3분 더 끓여주세요.", 3, "약불", "숟가락에 국물이 가볍게 묻는 농도면 좋아요."),
        ]

    if method in {"샐러드", "무침"}:
        return [
            common_prep,
            step(2, "물기 정리", "오이나 잎채소가 있으면 찬물에 헹군 뒤 물기를 충분히 털어주세요.", 3, "없음", "재료 표면에 물방울이 거의 없으면 좋아요."),
            step(3, "소스 만들기", "볼에 소스 재료를 넣고 고르게 섞어주세요.", 2, "없음", "단맛과 산미가 한쪽으로 몰리지 않고 균일하면 좋아요."),
            step(4, "가볍게 섞기", "준비한 재료를 소스에 넣고 젓가락으로 살살 섞어주세요.", 2, "없음", "재료가 으깨지지 않고 표면에 소스가 얇게 묻으면 좋아요."),
            step(5, "차게 내기", "접시에 담아 바로 내거나 2분 정도 차게 두었다가 내주세요.", 1, "없음", "채소의 아삭함과 소스의 산뜻함이 살아 있으면 좋아요."),
        ]

    if method == "전":
        return [
            common_prep,
            step(2, "가루옷 준비", "부침가루나 준비한 양념을 사용해 재료 표면에 얇게 가루옷을 입혀주세요.", 3, "없음", "가루가 뭉치지 않고 얇게 묻어 있으면 좋아요."),
            step(3, "달걀물 묻히기", "달걀이 있으면 잘 풀어 재료를 한 번 가볍게 적셔주세요.", 2, "없음", "표면에 달걀물이 고르게 묻으면 좋아요."),
            step(4, "부치기", "기름 두른 팬에 올려 앞뒤로 노릇하게 부쳐주세요.", 5, "중불", "가장자리가 단단해지고 노릇한 색이 나면 좋아요."),
            step(5, "기름 빼기", "키친타월에 잠깐 올려 여분의 기름을 빼고 담아주세요.", 1, "없음", "표면에 기름이 흐르지 않고 따뜻하면 좋아요."),
        ]

    if method == "딥":
        return [
            common_prep,
            step(2, "재료 볶기", "팬에 기름이나 버터를 두르고 향이 나는 재료부터 천천히 볶아주세요.", 6, "약불", "수분이 줄고 단향이나 고소한 향이 올라오면 좋아요."),
            step(3, "농도 만들기", "준비한 양념과 우유나 요거트를 넣어 되직하게 섞어주세요.", 5, "약불", "주걱으로 밀었을 때 바닥이 잠깐 보이면 좋아요."),
            step(4, "곁들임 준비", "빵이나 채소를 먹기 좋은 크기로 준비해 바삭하거나 차갑게 정리해주세요.", 3, "중불", "찍어 먹기 좋은 크기와 식감이면 좋아요."),
            step(5, "담아내기", "딥을 작은 그릇에 담고 곁들임 재료와 함께 내주세요.", 1, "없음", "딥이 흐르지 않고 숟가락으로 떠지는 농도면 좋아요."),
        ]

    if method == "오픈샌드":
        return [
            common_prep,
            step(2, "빵 굽기", "빵을 마른 팬이나 에어프라이어에 넣어 앞뒤로 바삭하게 구워주세요.", 3, "중불", "빵 가장자리가 노릇하고 표면이 단단하면 좋아요."),
            step(3, "토핑 익히기", "팬에 토핑 재료를 넣고 수분이 과하게 남지 않게 짧게 익혀주세요.", 4, "중불", "토핑에 윤기가 돌고 물이 흥건하지 않으면 좋아요."),
            step(4, "올리기", "구운 빵 위에 토핑을 올리고 치즈나 소스를 얹어주세요.", 2, "없음", "토핑이 빵 위에 안정적으로 올라가 있으면 좋아요."),
            step(5, "마무리", "먹기 좋은 크기로 잘라 바로 내주세요.", 1, "없음", "빵은 바삭하고 토핑은 따뜻하거나 촉촉하면 좋아요."),
        ]

    if method == "꼬치구이":
        return [
            common_prep,
            step(2, "꼬치 끼우기", "재료를 비슷한 높이로 맞춰 꼬치에 번갈아 끼워주세요.", 5, "없음", "꼬치가 팬에 평평하게 닿을 수 있으면 좋아요."),
            step(3, "초벌 굽기", "팬에 기름을 얇게 두르고 꼬치를 올려 속까지 익혀주세요.", 6, "중불", "재료 겉면이 익고 꼬치가 흐트러지지 않으면 좋아요."),
            step(4, "양념 입히기", "준비한 양념을 바르듯 넣고 앞뒤로 굴려가며 구워주세요.", 4, "중강불", "양념이 재료 표면에 얇게 붙으면 좋아요."),
            step(5, "담아내기", "불을 끄고 1분 식힌 뒤 한입씩 먹기 좋게 담아주세요.", 1, "없음", "꼬치에서 재료가 쉽게 빠지지 않으면 좋아요."),
        ]

    if method == "그라탕":
        return [
            common_prep,
            step(2, "속재료 익히기", "팬에 주재료를 먼저 볶거나 데워 수분을 줄여주세요.", 5, "중불", "팬 바닥에 물이 많이 남지 않으면 좋아요."),
            step(3, "소스 섞기", "준비한 양념과 우유나 치즈를 넣어 재료를 가볍게 묶어주세요.", 4, "약불", "소스가 재료에 얇게 붙는 농도면 좋아요."),
            step(4, "치즈 올리기", "내열 용기에 담고 치즈를 고르게 올려주세요.", 2, "없음", "치즈가 표면을 고르게 덮으면 좋아요."),
            step(5, "굽기", "에어프라이어 180도에서 6~8분 구워주세요.", 7, "없음", "치즈가 녹고 윗면에 옅은 갈색이 돌면 좋아요."),
        ]

    if method == "말이구이":
        return [
            common_prep,
            step(2, "속재료 놓기", "넓게 펼친 재료 위에 속재료를 올리고 너무 많이 넣지 않게 정리해주세요.", 3, "없음", "말았을 때 끝이 닫힐 정도의 양이면 좋아요."),
            step(3, "단단히 말기", "재료가 빠지지 않도록 끝부분을 눌러가며 단단히 말아주세요.", 4, "없음", "이음새가 아래로 향하면 풀리지 않아요."),
            step(4, "이음새 굽기", "팬에 올릴 때 이음새가 먼저 닿게 두고 중불에서 고정해주세요.", 5, "중불", "말이가 풀리지 않고 겉면이 붙으면 좋아요."),
            step(5, "마무리 굽기", "굴려가며 전체를 노릇하게 익히고 바로 담아주세요.", 3, "중강불", "겉면이 고르게 노릇하고 속재료가 따뜻하면 좋아요."),
        ]

    if method == "달걀말이":
        return [
            common_prep,
            step(2, "달걀물 만들기", "달걀과 우유, 소금 등을 넣고 흰자 덩어리가 보이지 않게 풀어주세요.", 3, "없음", "달걀물이 균일한 노란색이면 좋아요."),
            step(3, "얇게 붓기", "기름을 얇게 두른 팬에 달걀물을 조금 붓고 약불에서 익혀주세요.", 3, "약불", "윗면이 촉촉할 때 말기 시작하면 좋아요."),
            step(4, "반복해서 말기", "달걀물을 조금씩 더 부어 이어가며 말아주세요.", 6, "약불", "층이 떨어지지 않고 부드럽게 붙으면 좋아요."),
            step(5, "식혀 썰기", "불을 끄고 1분 둔 뒤 한입 크기로 썰어주세요.", 1, "없음", "단면이 부서지지 않고 촉촉하면 좋아요."),
        ]

    if method == "달걀찜":
        return [
            common_prep,
            step(2, "달걀물 풀기", "달걀, 우유나 물, 간을 넣고 거품이 과하지 않게 풀어주세요.", 3, "없음", "알끈이 풀리고 색이 균일하면 좋아요."),
            step(3, "그릇에 담기", "내열 그릇에 달걀물을 붓고 버섯이나 대파 같은 재료를 고르게 올려주세요.", 2, "없음", "재료가 한쪽에 몰리지 않으면 좋아요."),
            step(4, "중탕하기", "냄비에 물을 조금 붓고 그릇을 넣은 뒤 뚜껑을 덮어 약불로 익혀주세요.", 7, "약불", "가장자리가 굳고 가운데가 살짝 흔들리면 좋아요."),
            step(5, "잔열 마무리", "불을 끄고 1분 둔 뒤 숟가락으로 떠서 확인해주세요.", 1, "없음", "흐르는 달걀물이 없고 촉촉하면 좋아요."),
        ]

    raise ValueError(f"Unsupported method: {method}")


def make_recipe(liquor_name: str, spec: dict[str, Any], index: int) -> dict[str, Any]:
    profile = LIQUOR_PROFILES[liquor_name]
    style = spec.get("style") or next(
        (tag for tag in spec["tags"] if tag in profile["styles"]),
        STYLE_CYCLES[liquor_name][index % len(STYLE_CYCLES[liquor_name])],
    )
    style_note = profile["styles"][style]
    names = ingredient_names(spec)
    vibe = spec["vibe"]
    method = spec["method"]
    tags = []
    for tag in [method, *spec["tags"], style]:
        if tag not in tags:
            tags.append(tag)

    return {
        "liquor_name": liquor_name,
        "name": spec["name"],
        "refresh_group": spec["refresh_group"],
        "rank_hint": spec["rank_hint"],
        "reason": f"{vibe} 포인트를 살린 {profile['display']}용 집안주예요. 집에서 부담 없이 만들 수 있고 한입씩 곁들이기 좋아요.",
        "pairing_knowledge": {
            "flavor_logic": f"이 조합은 {vibe} 포인트가 살아 있어서 {style}에서 느껴지는 {style_note}에 자연스럽게 어울려요.",
            "ingredient_logic": f"{names} 재료를 {method} 방식으로 조리해 향과 식감을 또렷하게 살렸어요.",
            "why_this_liquor": f"{profile['display']}는 {profile['why']} 특히 {style} 스타일과 함께하면 안주의 여운이 부담 없이 이어져요.",
        },
        "servings": spec["servings"],
        "cook_time_minutes": spec["cook_time_minutes"],
        "difficulty": spec["difficulty"],
        "ingredient_details": spec["ingredient_details"],
        "pantry_items": spec["pantry_items"],
        "recipe_steps": build_steps(spec),
        "tip": tip_for(spec),
        "tags": tags,
    }


def build_specs() -> dict[str, list[dict[str, Any]]]:
    return {
        "soju": [
            recipe_spec("돼지목살 대파 소금구이", "팬구이", 93, 0, [ing("pork"), ing("green_onion", 1, "대"), ing("lettuce"), ing("garlic")], "salt", "돼지목살의 고소한 육향과 구운 대파의 단맛", ["돼지고기", "대파", "소금구이"], servings=2),
            recipe_spec("양배추 대패 돼지고기찜", "찜", 90, 1, [ing("pork", 180, "g", variant_detail="얇게 썬 대패 목살"), ing("cabbage", 220, "g"), ing("mushroom", 80, "g", display_name="팽이버섯", variant_detail="밑동을 제거한 팽이버섯")], "soy", "양배추 채수와 얇은 돼지고기의 담백한 감칠맛", ["돼지고기", "양배추", "담백"], servings=2),
            recipe_spec("맑은 대구 대파탕", "탕", 91, 0, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("green_onion", 1, "대"), ing("mushroom", 60, "g", display_name="느타리버섯", variant_detail="결대로 찢은 느타리버섯"), ing("garlic", 1, "쪽", variant_detail="생마늘을 곱게 다져 사용")], "salt", "대구살의 시원한 국물맛과 대파의 깔끔한 향", ["맑은탕", "대구살", "대파"]),
            recipe_spec("오이 소고기 냉채", "무침", 82, 1, [ing("beef", 140, "g", variant_detail="얇게 썬 샤부샤부용 소고기"), ing("cucumber"), ing("onion", 0.25, "개"), ing("lettuce", 4, "장")], "vinegar", "오이의 아삭함과 데친 소고기의 담백한 육향", ["냉채", "소고기", "오이"]),
            recipe_spec("양송이 대파 달걀찜", "달걀찜", 78, 0, [ing("egg", 3, "개"), ing("mushroom", 3, "개"), ing("green_onion", 0.4, "대"), ing("milk", 50, "ml")], "soy", "달걀의 부드러움과 양송이버섯의 은은한 우마미", ["달걀찜", "양송이버섯", "부드러움"]),
            recipe_spec("돼지고기 양파 간장볶음", "볶음", 86, 1, [ing("pork", 200, "g", variant_detail="얇게 썬 돼지 앞다리살"), ing("onion"), ing("cabbage", 120, "g"), ing("garlic")], "soy", "얇은 돼지고기와 양파의 단짠 감칠맛", ["볶음", "돼지고기", "양파"], servings=2),
            recipe_spec("닭고기 감자 간장조림", "조림", 88, 0, [ing("chicken", 240, "g"), ing("potato", 1.5, "개"), ing("carrot"), ing("garlic")], "soy", "닭고기 육즙과 감자의 포근한 단맛", ["조림", "닭고기", "감자"], servings=2),
            recipe_spec("가지 돼지고기 말이구이", "말이구이", 84, 1, [ing("eggplant"), ing("pork", 160, "g", variant_detail="얇게 썬 돼지 앞다리살"), ing("green_onion"), ing("garlic")], "soy", "구운 가지의 부드러움과 돼지고기의 짭조름한 육향", ["말이구이", "가지", "돼지고기"]),
            recipe_spec("양배추 소고기 달걀전", "전", 77, 0, [ing("beef", 120, "g", variant_detail="잘게 다진 소고기"), ing("cabbage", 120, "g"), ing("egg", 2, "개"), ing("green_onion")], "pancake", "양배추의 단맛과 소고기의 고소함을 얇게 부친 맛", ["전", "소고기", "양배추"], servings=2),
            recipe_spec("토마토 대구살 맑은조림", "조림", 83, 1, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("tomato", 1.5, "개"), ing("onion"), ing("garlic")], "soy", "토마토 산미와 대구살의 담백한 감칠맛", ["조림", "대구살", "토마토"]),
            recipe_spec("오이 베이컨 겨자무침", "무침", 75, 0, [ing("bacon", 2, "줄"), ing("cucumber"), ing("onion", 0.2, "개"), ing("lettuce", 4, "장")], "mustard", "오이의 수분감과 베이컨의 짭짤한 향", ["무침", "오이", "베이컨"]),
            recipe_spec("닭고기 브로콜리 소금구이", "팬구이", 85, 1, [ing("chicken", 220, "g", variant_detail="닭안심 또는 닭다리살 정육"), ing("broccoli"), ing("garlic"), ing("onion", 0.3, "개")], "salt", "닭고기의 담백함과 브로콜리의 아삭한 구운 향", ["팬구이", "닭고기", "브로콜리"], servings=2),
            recipe_spec("돼지고기 가지 간장찜", "찜", 83, 0, [ing("pork", 200, "g", variant_detail="얇게 썬 돼지목살"), ing("eggplant", 1.5, "개"), ing("onion"), ing("garlic")], "soy", "가지가 머금은 간장 향과 돼지고기의 부드러운 지방감", ["찜", "가지", "돼지고기"], servings=2),
            recipe_spec("소고기 표고 대파볶음", "볶음", 87, 1, [ing("beef", 180, "g", variant_detail="얇게 썬 불고기용 소고기"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="도톰하게 썬 생표고버섯"), ing("green_onion", 1, "대"), ing("garlic")], "soy", "표고버섯 우마미와 소고기 육향", ["볶음", "소고기", "표고버섯"]),
            recipe_spec("감자 베이컨 간장조림", "조림", 80, 0, [ing("potato", 1.5, "개"), ing("bacon", 2, "줄"), ing("onion"), ing("garlic")], "soy", "감자의 포근함과 베이컨의 짭짤한 감칠맛", ["조림", "감자", "베이컨"]),
            recipe_spec("양배추 닭고기 맑은탕", "탕", 84, 1, [ing("chicken", 220, "g"), ing("cabbage", 180, "g"), ing("green_onion", 1, "대"), ing("garlic", 1, "쪽", variant_detail="생마늘을 곱게 다져 사용")], "salt", "양배추 단맛과 닭고기 육수가 만든 맑은 감칠맛", ["탕", "닭고기", "양배추"], servings=2),
            recipe_spec("토마토 달걀 부드러운볶음", "볶음", 72, 0, [ing("egg", 3, "개"), ing("tomato", 1.5, "개"), ing("green_onion"), ing("onion", 0.2, "개")], "salt", "토마토 산미와 달걀의 몽글한 고소함", ["볶음", "달걀", "토마토"]),
            recipe_spec("오이 파프리카 상추무침", "무침", 70, 1, [ing("cucumber"), ing("pepper"), ing("lettuce", 5, "장"), ing("onion", 0.2, "개")], "vinegar", "오이와 파프리카의 시원한 아삭함", ["무침", "파프리카", "상추"]),
            recipe_spec("대구살 양파찜", "찜", 86, 0, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("onion"), ing("mushroom", 60, "g", display_name="느타리버섯", variant_detail="결대로 찢은 느타리버섯"), ing("green_onion")], "soy", "대구살의 담백함과 양파 채수의 단맛", ["찜", "대구살", "양파"]),
            recipe_spec("돼지고기 파프리카 꼬치구이", "꼬치구이", 81, 1, [ing("pork", 200, "g"), ing("pepper"), ing("onion"), ing("garlic")], "herb", "돼지고기 구운 향과 파프리카의 달큰한 채즙", ["꼬치구이", "돼지고기", "파프리카"], servings=2),
            recipe_spec("소고기 감자 간장조림", "조림", 88, 0, [ing("beef", 180, "g"), ing("potato", 1.5, "개"), ing("carrot"), ing("garlic")], "soy", "소고기 육향과 감자의 포근한 단짠 맛", ["조림", "소고기", "감자"], servings=2),
            recipe_spec("닭고기 상추 오이샐러드", "샐러드", 74, 1, [ing("chicken", 180, "g", variant_detail="익혀 찢은 닭안심"), ing("lettuce", 5, "장"), ing("cucumber"), ing("tomato")], "mayo", "닭고기의 담백함과 상추, 오이의 신선함", ["샐러드", "닭고기", "상추"]),
            recipe_spec("버터 양송이 감자구이", "팬구이", 79, 0, [ing("mushroom", 6, "개"), ing("potato", 1.5, "개"), ing("butter", 14, "g"), ing("garlic")], "parsley", "양송이버섯 우마미와 버터 감자의 고소함", ["팬구이", "양송이버섯", "감자"]),
            recipe_spec("소시지 대파 팬구이", "팬구이", 71, 1, [ing("sausage", 6, "개"), ing("green_onion", 1, "대"), ing("onion"), ing("garlic")], "salt", "소시지의 짭짤함과 구운 대파 단맛", ["팬구이", "소시지", "대파"]),
            recipe_spec("돼지고기 브로콜리 굴소스볶음", "볶음", 82, 0, [ing("pork", 190, "g", variant_detail="얇게 썬 돼지 앞다리살"), ing("broccoli", 130, "g"), ing("onion"), ing("garlic")], "oyster", "브로콜리의 아삭함과 돼지고기 굴소스 감칠맛", ["볶음", "돼지고기", "브로콜리"], servings=2),
            recipe_spec("닭고기 양송이 맑은탕", "탕", 83, 1, [ing("chicken", 220, "g"), ing("mushroom", 5, "개"), ing("green_onion", 1, "대"), ing("garlic", 1, "쪽", variant_detail="생마늘을 곱게 다져 사용")], "salt", "닭고기 국물과 양송이버섯의 은은한 감칠맛", ["탕", "닭고기", "양송이버섯"], servings=2),
            recipe_spec("가지 대파 달걀찜", "달걀찜", 73, 0, [ing("egg", 3, "개"), ing("eggplant"), ing("green_onion"), ing("milk", 50, "ml")], "soy", "부드러운 달걀과 가지의 촉촉한 단맛", ["달걀찜", "가지", "대파"]),
            recipe_spec("소고기 오이 상추쌈구이", "팬구이", 86, 1, [ing("beef", 180, "g", variant_detail="얇게 썬 구이용 소고기"), ing("cucumber"), ing("lettuce", 6, "장"), ing("garlic")], "salt", "소고기 구운 향과 오이, 상추의 산뜻한 식감", ["팬구이", "소고기", "상추쌈"]),
            recipe_spec("대구살 감자 맑은스튜", "스튜", 81, 0, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("potato", 1.5, "개"), ing("onion"), ing("carrot")], "salt", "대구살의 담백함과 감자가 만든 부드러운 국물감", ["스튜", "대구살", "감자"]),
            recipe_spec("파프리카 대파 달걀말이", "달걀말이", 76, 1, [ing("egg", 3, "개"), ing("pepper"), ing("green_onion"), ing("milk", 2, "큰술")], "salt", "파프리카의 은은한 단맛과 부드러운 달걀층", ["달걀말이", "파프리카", "대파"]),
        ],
        "beer": [
            recipe_spec("감자 베이컨 해시구이", "팬구이", 88, 0, [ing("potato", 2, "개"), ing("bacon", 3, "줄"), ing("onion"), ing("garlic")], "salt", "감자의 바삭한 가장자리와 베이컨의 짭짤한 향", ["감자", "베이컨", "라거"]),
            recipe_spec("체다 브로콜리 감자볼", "에어프라이어", 84, 1, [ing("potato", 1.5, "개"), ing("broccoli", 100, "g"), ing("cheese", 2, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("egg", 1, "개")], "starch", "감자의 포슬함과 체다 치즈의 짭짤한 고소함", ["감자볼", "체다", "브로콜리"], servings=2),
            recipe_spec("소시지 파프리카 치즈꼬치", "꼬치구이", 86, 0, [ing("sausage", 6, "개"), ing("pepper"), ing("onion"), ing("cheese", 40, "g", display_name="모짜렐라 치즈", variant_detail="한입 크기 모짜렐라 치즈")], "herb", "소시지 육즙과 파프리카, 치즈의 단짠 조합", ["꼬치", "소시지", "파프리카"], servings=2),
            recipe_spec("갈릭버터 양송이 팝", "에어프라이어", 82, 1, [ing("mushroom", 8, "개"), ing("butter", 16, "g"), ing("garlic"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "parsley", "양송이버섯 채수와 마늘버터의 고소한 향", ["양송이버섯", "마늘버터", "에어프라이어"]),
            recipe_spec("닭안심 전분구이", "팬구이", 85, 0, [ing("chicken", 180, "g", display_name="닭안심", variant_detail="힘줄을 제거한 냉장 닭안심"), ing("garlic"), ing("lettuce", 4, "장")], "starch", "닭안심의 담백한 속살과 바삭한 전분 코팅", ["닭안심", "바삭함", "라거"]),
            recipe_spec("양배추 베이컨 크런치구이", "에어프라이어", 80, 1, [ing("cabbage", 180, "g"), ing("bacon", 3, "줄"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "salt", "양배추 가장자리의 바삭함과 베이컨의 훈연 짠맛", ["양배추", "베이컨", "크런치"]),
            recipe_spec("토마토 체다 에그컵", "에어프라이어", 79, 0, [ing("tomato", 6, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("egg", 2, "개"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("onion", 0.2, "개")], "parsley", "토마토 산미와 체다 달걀의 부드러운 짠맛", ["에그컵", "체다", "토마토"]),
            recipe_spec("돼지앞다리 후추구이", "팬구이", 83, 1, [ing("pork", 220, "g", variant_detail="구이용 돼지 앞다리살"), ing("onion"), ing("garlic"), ing("pepper")], "salt", "돼지고기 구운 향과 후추의 선명한 여운", ["돼지고기", "후추", "팬구이"], servings=2),
            recipe_spec("오이 요거트 딥과 감자구이", "딥", 76, 0, [ing("cucumber"), ing("yogurt", 4, "큰술"), ing("potato", 2, "개"), ing("garlic", 0.3, "쪽", variant_detail="생마늘을 아주 곱게 다져 사용")], "lemon", "감자구이의 고소함과 오이 요거트 딥의 산뜻함", ["딥", "감자", "요거트"]),
            recipe_spec("브로콜리 체다 미니그라탕", "그라탕", 81, 1, [ing("broccoli", 140, "g"), ing("cheese", 2, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("milk", 70, "ml"), ing("butter", 10, "g")], "cream", "브로콜리의 아삭함과 체다 소스의 고소함", ["그라탕", "브로콜리", "체다"]),
            recipe_spec("가지 베이컨 롤구이", "말이구이", 82, 0, [ing("eggplant"), ing("bacon", 4, "줄"), ing("cheese", 40, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("garlic")], "herb", "부드러운 가지와 베이컨, 치즈의 짭짤한 한입감", ["말이구이", "가지", "베이컨"]),
            recipe_spec("소시지 감자 간장볶음", "볶음", 78, 1, [ing("sausage", 6, "개"), ing("potato", 1.5, "개"), ing("onion"), ing("garlic")], "soy", "소시지 짠맛과 감자의 단짠 볶음 향", ["볶음", "소시지", "감자"], servings=2),
            recipe_spec("소고기 양파 미니볼", "팬구이", 82, 0, [ing("beef", 220, "g", variant_detail="소고기 다짐육"), ing("onion", 0.3, "개"), ing("egg", 1, "개"), ing("garlic")], "starch", "소고기 다짐육의 진한 육향과 양파 단맛", ["미니볼", "소고기", "양파"], servings=2),
            recipe_spec("파프리카 모짜렐라 에어프라이어구이", "에어프라이어", 77, 1, [ing("pepper", 1, "개"), ing("cheese", 60, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("mushroom", 4, "개"), ing("onion", 0.3, "개")], "herb", "파프리카의 단맛과 녹은 모짜렐라의 고소함", ["파프리카", "모짜렐라", "에어프라이어"]),
            recipe_spec("닭고기 양배추 머스터드샐러드", "샐러드", 74, 0, [ing("chicken", 170, "g", display_name="닭안심", variant_detail="익혀 찢은 닭안심"), ing("cabbage", 140, "g"), ing("lettuce", 4, "장"), ing("cucumber", 0.5, "개")], "mustard", "닭안심과 양배추를 가볍게 묶는 머스터드 산미", ["샐러드", "닭고기", "머스터드"]),
            recipe_spec("베이컨 대파 달걀말이", "달걀말이", 75, 1, [ing("bacon", 2, "줄"), ing("green_onion", 0.6, "대"), ing("egg", 3, "개"), ing("milk", 2, "큰술")], "salt", "베이컨의 짭짤함과 대파 달걀의 부드러운 식감", ["달걀말이", "베이컨", "대파"]),
            recipe_spec("양송이 감자 크림딥", "딥", 79, 0, [ing("mushroom", 5, "개"), ing("potato", 1, "개"), ing("milk", 90, "ml"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "cream", "양송이버섯 우마미와 감자 크림의 되직한 고소함", ["딥", "양송이버섯", "감자"]),
            recipe_spec("돼지고기 파프리카 양배추 에어프라이어구이", "에어프라이어", 83, 1, [ing("pork", 220, "g"), ing("pepper", 1, "개"), ing("cabbage", 120, "g"), ing("garlic")], "herb", "돼지고기의 구운 향과 파프리카, 양배추의 달큰한 수분감", ["돼지고기", "파프리카", "에어프라이어"], servings=2),
            recipe_spec("브로콜리 베이컨 팬볶음", "볶음", 76, 0, [ing("broccoli", 130, "g"), ing("bacon", 3, "줄"), ing("garlic"), ing("onion", 0.3, "개")], "salt", "브로콜리의 아삭함과 베이컨 기름의 짭짤한 향", ["볶음", "브로콜리", "베이컨"]),
            recipe_spec("감자 달걀 마요샐러드", "샐러드", 72, 1, [ing("potato", 1.5, "개"), ing("egg", 2, "개"), ing("cucumber", 0.5, "개"), ing("yogurt", 1, "큰술")], "mayo", "감자와 달걀의 포근함을 가볍게 잡는 마요 소스", ["샐러드", "감자", "달걀"]),
            recipe_spec("체다 소시지 양파그라탕", "그라탕", 80, 0, [ing("sausage", 6, "개"), ing("onion", 0.7, "개"), ing("cheese", 2, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("milk", 70, "ml")], "cream", "소시지와 양파 단맛을 체다 치즈로 묶은 진한 맛", ["그라탕", "소시지", "체다"], servings=2),
            recipe_spec("닭다리살 허브 꼬치구이", "꼬치구이", 84, 1, [ing("chicken", 240, "g"), ing("pepper"), ing("onion"), ing("garlic")], "herb", "닭다리살의 육즙과 허브, 파프리카의 구운 향", ["꼬치구이", "닭다리살", "허브"], servings=2),
            recipe_spec("토마토 베이컨 오픈샌드", "오픈샌드", 73, 0, [ing("bread", 2, "조각"), ing("tomato", 1, "개"), ing("bacon", 2, "줄"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈")], "parsley", "바삭한 빵과 토마토, 베이컨의 짭짤한 대비", ["오픈샌드", "토마토", "베이컨"]),
            recipe_spec("소시지 브로콜리 굴소스볶음", "볶음", 77, 1, [ing("sausage", 6, "개"), ing("broccoli", 130, "g"), ing("garlic"), ing("onion", 0.3, "개")], "oyster", "소시지의 짭짤함과 브로콜리 굴소스 감칠맛", ["볶음", "소시지", "브로콜리"]),
            recipe_spec("가지 파마산 에어프라이어칩", "에어프라이어", 71, 0, [ing("eggplant", 1.5, "개"), ing("cheese", 2, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루"), ing("garlic", 1, "쪽")], "herb", "가지 가장자리의 바삭함과 파마산 치즈의 짭짤함", ["가지", "파마산", "칩"]),
            recipe_spec("소고기 감자 미니그라탕", "그라탕", 81, 1, [ing("beef", 160, "g", variant_detail="잘게 썬 구이용 소고기"), ing("potato", 1.5, "개"), ing("cheese", 60, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("milk", 80, "ml")], "cream", "소고기 육향과 감자, 치즈의 묵직한 고소함", ["그라탕", "소고기", "감자"], servings=2),
            recipe_spec("파프리카 베이컨 꼬치구이", "꼬치구이", 74, 0, [ing("pepper", 1, "개"), ing("bacon", 4, "줄"), ing("onion"), ing("mushroom", 5, "개")], "herb", "파프리카 단맛과 베이컨 훈연향을 한입에 먹는 맛", ["꼬치구이", "파프리카", "베이컨"]),
            recipe_spec("닭안심 요거트 머스터드딥", "딥", 75, 1, [ing("chicken", 170, "g", display_name="닭안심", variant_detail="삶거나 구운 닭안심"), ing("yogurt", 4, "큰술"), ing("cucumber", 0.5, "개"), ing("garlic", 0.3, "쪽", variant_detail="생마늘을 아주 곱게 다져 사용")], "mustard", "담백한 닭안심과 요거트 머스터드의 산뜻함", ["딥", "닭안심", "요거트"]),
            recipe_spec("버터갈릭 감자 큐브구이", "팬구이", 78, 0, [ing("potato", 2, "개"), ing("butter", 16, "g"), ing("garlic"), ing("green_onion", 0.4, "대")], "parsley", "감자 큐브의 바삭한 겉면과 마늘버터 향", ["팬구이", "감자", "마늘버터"]),
            recipe_spec("체다 달걀 감자전", "전", 70, 1, [ing("potato", 1.5, "개"), ing("egg", 2, "개"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("onion", 0.2, "개")], "pancake", "감자전의 바삭함과 체다 달걀의 짭짤한 고소함", ["전", "감자", "체다"]),
        ],
        "white_wine": [
            recipe_spec("도미 오이 레몬무침", "무침", 94, 0, [ing("fish", 120, "g", display_name="도미살", variant_detail="생식 가능한 횟감용 도미 필렛"), ing("cucumber"), ing("onion", 0.2, "개"), ing("lettuce", 3, "장")], "lemon", "도미살의 담백함과 오이, 레몬의 산뜻함", ["도미", "오이", "소비뇽 블랑"]),
            recipe_spec("대구살 토마토 찜", "찜", 90, 1, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("tomato", 1.5, "개"), ing("onion"), ing("garlic", 1, "쪽")], "lemon", "대구살의 담백함과 토마토 산미가 만든 부드러운 찜", ["대구살", "토마토", "찜"]),
            recipe_spec("닭안심 요거트 오이샐러드", "샐러드", 88, 0, [ing("chicken", 170, "g", display_name="닭안심", variant_detail="익혀 찢은 닭안심"), ing("yogurt", 4, "큰술"), ing("cucumber"), ing("lettuce", 4, "장")], "lemon", "닭안심의 담백함과 요거트 오이의 시원한 산미", ["샐러드", "닭안심", "요거트"]),
            recipe_spec("브로콜리 달걀 밀크프리타타", "팬구이", 79, 1, [ing("broccoli", 120, "g"), ing("egg", 3, "개"), ing("milk", 50, "ml"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "salt", "브로콜리의 풋풋함과 달걀, 우유의 부드러운 고소함", ["프리타타", "브로콜리", "달걀"]),
            recipe_spec("흰살생선 파프리카 호일구이", "에어프라이어", 89, 0, [ing("fish", display_name="흰살생선", variant_detail="대구살 또는 광어 구이용 필렛"), ing("pepper", 1, "개"), ing("butter", 10, "g"), ing("onion", 0.3, "개")], "herb", "흰살생선의 촉촉함과 파프리카의 달큰한 향", ["흰살생선", "파프리카", "호일구이"]),
            recipe_spec("양송이 우유 크림찜", "찜", 80, 1, [ing("mushroom", 7, "개"), ing("milk", 100, "ml"), ing("onion"), ing("butter", 10, "g")], "cream", "양송이버섯 우마미와 우유 크림의 부드러운 질감", ["양송이버섯", "우유", "크림"]),
            recipe_spec("토마토 오이 요거트컵", "샐러드", 76, 0, [ing("tomato", 6, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("cucumber"), ing("yogurt", 3, "큰술"), ing("onion", 0.1, "개")], "lemon", "토마토와 오이를 요거트로 가볍게 묶은 상큼함", ["토마토", "오이", "요거트"]),
            recipe_spec("닭고기 양배추 레몬샐러드", "샐러드", 82, 1, [ing("chicken", 180, "g", variant_detail="익혀 찢은 닭다리살 또는 닭안심"), ing("cabbage", 150, "g"), ing("lettuce", 4, "장"), ing("cucumber", 0.5, "개")], "lemon", "닭고기의 담백함과 양배추 레몬 드레싱의 산뜻함", ["샐러드", "닭고기", "양배추"]),
            recipe_spec("대구살 브로콜리 팬구이", "팬구이", 88, 0, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("broccoli", 130, "g"), ing("garlic"), ing("butter", 8, "g")], "lemon", "대구살의 담백한 결감과 브로콜리의 구운 향", ["팬구이", "대구살", "브로콜리"]),
            recipe_spec("가지 토마토 허브찜", "찜", 77, 1, [ing("eggplant", 1.5, "개"), ing("tomato", 1.5, "개"), ing("onion"), ing("garlic", 1, "쪽")], "herb", "가지의 부드러운 단맛과 토마토의 가벼운 산미", ["가지", "토마토", "허브"]),
            recipe_spec("시금치 달걀 밀크수프", "수프", 74, 0, [ing("spinach", 90, "g"), ing("egg", 2, "개"), ing("milk", 160, "ml"), ing("onion", 0.3, "개")], "cream", "시금치의 은은한 단맛과 달걀 우유의 포근한 질감", ["수프", "시금치", "달걀"]),
            recipe_spec("연어 파프리카 팬구이", "팬구이", 90, 1, [ing("fish", 150, "g", display_name="연어", variant_detail="구이용 연어 필렛"), ing("pepper", 1, "개"), ing("butter", 10, "g"), ing("garlic", 1, "쪽")], "lemon", "연어의 고소한 지방감과 파프리카의 산뜻한 단맛", ["연어", "파프리카", "팬구이"]),
            recipe_spec("리코타 오이 상추샐러드", "샐러드", 75, 0, [ing("cucumber"), ing("cheese", 80, "g", display_name="리코타 치즈", variant_detail="수분감이 적당한 리코타 치즈"), ing("lettuce", 5, "장"), ing("onion", 0.15, "개")], "lemon", "오이와 상추의 신선함, 리코타 치즈의 밀키한 질감", ["샐러드", "리코타", "오이"]),
            recipe_spec("닭다리살 양송이 우유조림", "조림", 84, 1, [ing("chicken", 230, "g"), ing("mushroom", 5, "개"), ing("milk", 120, "ml"), ing("garlic")], "cream", "닭다리살의 고소함과 양송이 우유 소스의 부드러움", ["조림", "닭다리살", "양송이버섯"], servings=2),
            recipe_spec("흰살생선 양배추 레몬찜", "찜", 86, 0, [ing("fish", display_name="흰살생선", variant_detail="가시 없는 대구살 또는 광어 필렛"), ing("cabbage", 160, "g"), ing("green_onion"), ing("garlic", 1, "쪽")], "lemon", "흰살생선과 양배추 채수의 맑고 산뜻한 맛", ["찜", "흰살생선", "양배추"]),
            recipe_spec("토마토 달걀 오픈샌드", "오픈샌드", 70, 1, [ing("bread", 2, "조각"), ing("tomato", 1, "개"), ing("egg", 2, "개"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "parsley", "바삭한 빵 위에 올린 토마토 달걀의 산뜻한 고소함", ["오픈샌드", "토마토", "달걀"]),
            recipe_spec("브로콜리 요거트 딥", "딥", 72, 0, [ing("broccoli", 140, "g"), ing("yogurt", 4, "큰술"), ing("garlic", 0.3, "쪽", variant_detail="생마늘을 아주 곱게 다져 사용"), ing("cucumber", 0.5, "개")], "lemon", "브로콜리의 풋풋함과 요거트 딥의 가벼운 산미", ["딥", "브로콜리", "요거트"]),
            recipe_spec("소고기 오이 레몬샐러드", "샐러드", 76, 1, [ing("beef", 140, "g", variant_detail="얇게 구운 소고기 채끝"), ing("cucumber"), ing("lettuce", 5, "장"), ing("onion", 0.15, "개")], "lemon", "얇게 구운 소고기와 오이 레몬 드레싱의 깔끔한 조합", ["샐러드", "소고기", "오이"]),
            recipe_spec("대구살 감자 요거트샐러드", "샐러드", 80, 0, [ing("fish", 130, "g", display_name="대구살", variant_detail="익혀 결대로 찢은 대구살"), ing("potato", 1, "개"), ing("yogurt", 3, "큰술"), ing("cucumber", 0.5, "개")], "lemon", "대구살과 감자를 요거트로 가볍게 묶은 담백함", ["샐러드", "대구살", "요거트"]),
            recipe_spec("파프리카 닭안심 꼬치구이", "꼬치구이", 81, 1, [ing("chicken", 180, "g", display_name="닭안심", variant_detail="힘줄을 제거한 닭안심"), ing("pepper", 1, "개"), ing("onion"), ing("garlic")], "herb", "닭안심의 담백함과 파프리카의 구운 단맛", ["꼬치구이", "닭안심", "파프리카"]),
            recipe_spec("양송이 시금치 버터팬구이", "팬구이", 78, 0, [ing("mushroom", 6, "개"), ing("spinach", 80, "g"), ing("butter", 10, "g"), ing("garlic")], "salt", "양송이버섯 우마미와 시금치의 은은한 단맛", ["팬구이", "양송이버섯", "시금치"]),
            recipe_spec("오이 당근 초무침", "무침", 68, 1, [ing("cucumber"), ing("carrot", 0.7, "개"), ing("onion", 0.15, "개"), ing("lettuce", 3, "장")], "vinegar", "오이와 당근의 아삭한 식감과 가벼운 산미", ["무침", "오이", "당근"]),
            recipe_spec("연어 양배추 레몬마요샐러드", "샐러드", 84, 0, [ing("fish", 140, "g", display_name="연어", variant_detail="구워 식힌 연어 필렛"), ing("cabbage", 150, "g"), ing("carrot", 0.3, "개"), ing("cucumber", 0.5, "개")], "mayo", "연어의 고소함과 양배추 레몬마요의 산뜻한 균형", ["샐러드", "연어", "양배추"]),
            recipe_spec("토마토 브로콜리 치즈그라탕", "그라탕", 79, 1, [ing("tomato", 1.5, "개"), ing("broccoli", 120, "g"), ing("cheese", 50, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("milk", 50, "ml")], "cream", "토마토 산미와 브로콜리, 모짜렐라의 부드러운 고소함", ["그라탕", "토마토", "브로콜리"]),
            recipe_spec("닭고기 감자 요거트샐러드", "샐러드", 77, 0, [ing("chicken", 160, "g", variant_detail="익혀 찢은 닭안심"), ing("potato", 1, "개"), ing("yogurt", 3, "큰술"), ing("onion", 0.15, "개")], "lemon", "닭고기와 감자를 요거트로 가볍게 묶은 포근한 맛", ["샐러드", "닭고기", "감자"]),
            recipe_spec("대구살 양파 맑은스튜", "스튜", 82, 1, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("onion"), ing("carrot"), ing("green_onion")], "salt", "대구살과 양파가 만든 맑고 부드러운 감칠맛", ["스튜", "대구살", "양파"]),
            recipe_spec("가지 리코타 토마토롤", "말이구이", 78, 0, [ing("eggplant"), ing("cheese", 70, "g", display_name="리코타 치즈", variant_detail="수분감이 적당한 리코타 치즈"), ing("tomato", 1, "개"), ing("garlic", 1, "쪽")], "herb", "구운 가지와 리코타, 토마토 산미가 만든 부드러운 한입감", ["말이구이", "가지", "리코타"]),
            recipe_spec("브로콜리 닭안심 찜", "찜", 80, 1, [ing("broccoli", 130, "g"), ing("chicken", 180, "g", display_name="닭안심", variant_detail="힘줄을 제거한 닭안심"), ing("onion"), ing("garlic", 1, "쪽")], "lemon", "닭안심의 담백함과 브로콜리의 산뜻한 채소감", ["찜", "닭안심", "브로콜리"]),
            recipe_spec("토마토 양송이 허브찜", "찜", 76, 0, [ing("tomato", 1.5, "개"), ing("mushroom", 6, "개"), ing("garlic", 1, "쪽"), ing("onion", 0.3, "개")], "herb", "토마토와 양송이버섯이 만든 가벼운 채수 감칠맛", ["찜", "토마토", "양송이버섯"]),
            recipe_spec("시금치 요거트 달걀샐러드", "샐러드", 73, 1, [ing("spinach", 80, "g"), ing("egg", 2, "개"), ing("yogurt", 3, "큰술"), ing("cucumber", 0.5, "개")], "lemon", "시금치와 달걀의 부드러움을 요거트 산미로 잡은 맛", ["샐러드", "시금치", "요거트"]),
        ],
        "red_wine": [
            recipe_spec("후추 소고기 양파 큐브구이", "팬구이", 94, 0, [ing("beef", 220, "g", variant_detail="스테이크용 등심 또는 채끝"), ing("onion"), ing("garlic", 5, "쪽"), ing("butter", 12, "g")], "salt", "소고기 육향과 양파 단맛, 후추 향", ["소고기", "후추", "카베르네"]),
            recipe_spec("새콤 가지 양송이 구이", "구이", 86, 1, [ing("eggplant"), ing("mushroom", 5, "개"), ing("onion", 0.4, "개"), ing("garlic", 1, "쪽")], "vinegar", "구운 가지의 부드러움과 양송이버섯 우마미", ["가지", "양송이버섯", "메를로"]),
            recipe_spec("소고기 토마토 감자 스튜", "스튜", 91, 0, [ing("beef", 180, "g", variant_detail="국거리용 양지 또는 사태"), ing("tomato", 2, "개"), ing("potato"), ing("carrot")], "soy", "토마토 산미와 소고기 육향이 녹아든 진한 국물감", ["스튜", "소고기", "토마토"], servings=2),
            recipe_spec("표고 소고기 간장조림", "조림", 89, 1, [ing("beef", 220, "g", variant_detail="구이용 채끝 또는 안심"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="도톰하게 썬 생표고버섯"), ing("garlic", 6, "쪽"), ing("onion", 0.2, "개")], "soy", "표고버섯의 진한 우마미와 소고기 간장 윤기", ["조림", "소고기", "표고버섯"], servings=2),
            recipe_spec("돼지목살 토마토 양파조림", "조림", 87, 0, [ing("pork", 260, "g", variant_detail="구이용 돼지목살"), ing("tomato", 2, "개"), ing("onion", 0.7, "개"), ing("garlic")], "herb", "돼지목살 지방감과 토마토 산미, 양파 단맛", ["조림", "돼지목살", "토마토"], servings=2),
            recipe_spec("닭다리살 양파 당근 허브찜", "찜", 82, 1, [ing("chicken", 280, "g"), ing("onion", 1, "개"), ing("carrot"), ing("garlic", 5, "쪽")], "soy", "닭다리살의 촉촉함과 양파, 당근의 은은한 단맛", ["찜", "닭다리살", "피노누아"], servings=2),
            recipe_spec("구운 파프리카 베이컨 샐러드", "샐러드", 78, 1, [ing("pepper", 1, "개"), ing("bacon", 3, "줄"), ing("lettuce", 5, "장"), ing("onion", 0.2, "개")], "vinegar", "구운 파프리카 단맛과 베이컨의 짭짤한 향", ["샐러드", "파프리카", "베이컨"]),
            recipe_spec("양송이 토마토 모짜렐라 에어프라이어구이", "에어프라이어", 84, 0, [ing("mushroom", 7, "개"), ing("tomato", 6, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("cheese", 55, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("garlic", 1, "쪽")], "parsley", "양송이버섯 채수와 토마토 산미, 모짜렐라의 고소함", ["에어프라이어", "양송이버섯", "피노누아"]),
            recipe_spec("돼지안심 통마늘 허브구이", "에어프라이어", 88, 1, [ing("pork", 320, "g", display_name="돼지안심", variant_detail="기름기가 적은 돼지안심"), ing("garlic", 8, "쪽"), ing("onion"), ing("butter", 8, "g")], "herb", "돼지안심의 담백함과 통마늘의 달큰한 구운 향", ["에어프라이어", "돼지안심", "허브"], servings=2),
            recipe_spec("소고기 양배추 식초간장볶음", "볶음", 82, 0, [ing("beef", 220, "g", variant_detail="얇게 썬 불고기감 소고기"), ing("cabbage", 180, "g"), ing("onion"), ing("garlic")], "vinegar", "소고기 육향과 양배추 단맛, 식초간장 산미", ["볶음", "소고기", "양배추"], servings=2),
            recipe_spec("가지 토마토 모짜렐라 겹구이", "구이", 84, 1, [ing("eggplant"), ing("tomato"), ing("cheese", 50, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("garlic", 1, "쪽")], "herb", "가지의 부드러운 단맛과 토마토, 모짜렐라의 산뜻한 고소함", ["구이", "가지", "토마토"]),
            recipe_spec("토마토 소고기 미트볼 조림", "조림", 90, 0, [ing("beef", 220, "g", variant_detail="소고기 다짐육"), ing("tomato", 2, "개"), ing("egg", 1, "개"), ing("onion", 0.4, "개")], "flour", "소고기 미트볼 육향과 토마토 소스의 산미", ["조림", "미트볼", "토마토"], servings=2),
            recipe_spec("버터 양송이 브로콜리 팬구이", "팬구이", 76, 1, [ing("mushroom", 6, "개"), ing("broccoli", 130, "g"), ing("butter", 18, "g"), ing("garlic", 2, "쪽")], "lemon", "양송이버섯 우마미와 브로콜리의 구운 향, 버터 고소함", ["팬구이", "양송이버섯", "브로콜리"]),
            recipe_spec("돼지고기 양송이 후추구이", "팬구이", 85, 0, [ing("pork", 260, "g"), ing("mushroom", 6, "개"), ing("garlic", 5, "쪽"), ing("onion", 0.4, "개")], "herb", "돼지고기 구운 지방감과 양송이버섯, 후추 향", ["팬구이", "돼지고기", "쉬라즈"], servings=2),
            recipe_spec("구운 토마토 체다 프리타타", "팬구이", 77, 1, [ing("egg", 3, "개"), ing("tomato", 6, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("onion", 0.2, "개")], "herb", "구운 토마토 산미와 체다 달걀의 부드러운 질감", ["프리타타", "토마토", "체다"]),
            recipe_spec("베이컨 표고 감자구이", "팬구이", 80, 0, [ing("bacon", 3, "줄"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="도톰하게 썬 생표고버섯"), ing("potato", 1.5, "개"), ing("garlic")], "salt", "베이컨 훈연향과 표고버섯, 감자의 고소한 구운 맛", ["팬구이", "표고버섯", "감자"]),
            recipe_spec("소고기 버섯 치즈그라탕", "그라탕", 86, 1, [ing("beef", 180, "g"), ing("mushroom", 6, "개"), ing("cheese", 60, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("milk", 70, "ml")], "cream", "소고기 육향과 버섯 우마미, 치즈의 녹진함", ["그라탕", "소고기", "버섯"], servings=2),
            recipe_spec("돼지고기 파프리카 스테이크팬구이", "팬구이", 83, 0, [ing("pork", 250, "g", variant_detail="두툼한 구이용 돼지목살"), ing("pepper", 1, "개"), ing("onion"), ing("garlic")], "herb", "돼지목살의 구운 향과 파프리카의 달큰한 채즙", ["팬구이", "돼지목살", "파프리카"], servings=2),
            recipe_spec("가지 소고기 라구풍 조림", "조림", 88, 1, [ing("beef", 180, "g", variant_detail="소고기 다짐육"), ing("eggplant", 1.5, "개"), ing("tomato", 2, "개"), ing("onion")], "herb", "가지와 소고기, 토마토가 만든 농축된 감칠맛", ["조림", "가지", "소고기"], servings=2),
            recipe_spec("닭고기 토마토 버섯스튜", "스튜", 84, 0, [ing("chicken", 240, "g"), ing("tomato", 2, "개"), ing("mushroom", 5, "개"), ing("onion")], "herb", "닭고기와 토마토, 버섯이 만든 부드러운 산미와 우마미", ["스튜", "닭고기", "버섯"], servings=2),
            recipe_spec("양배추 베이컨 토마토찜", "찜", 79, 1, [ing("cabbage", 200, "g"), ing("bacon", 3, "줄"), ing("tomato", 1.5, "개"), ing("onion")], "herb", "양배추 단맛과 베이컨, 토마토의 짭짤한 산미", ["찜", "양배추", "베이컨"], servings=2),
            recipe_spec("연어 버터 토마토팬구이", "팬구이", 78, 0, [ing("fish", 150, "g", display_name="연어", variant_detail="구이용 연어 필렛"), ing("tomato", 1, "개"), ing("butter", 10, "g"), ing("garlic", 1, "쪽")], "lemon", "연어 지방감과 토마토 산미, 버터의 고소함", ["팬구이", "연어", "피노누아"]),
            recipe_spec("소고기 시금치 치즈롤", "말이구이", 82, 1, [ing("beef", 180, "g", variant_detail="얇게 썬 구이용 소고기"), ing("spinach", 80, "g"), ing("cheese", 40, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("garlic")], "herb", "소고기 육향과 시금치, 치즈의 부드러운 한입감", ["말이구이", "소고기", "시금치"]),
            recipe_spec("돼지목살 양송이 양파 버터조림", "조림", 85, 0, [ing("pork", 260, "g", variant_detail="구이용 돼지목살"), ing("mushroom", 4, "개"), ing("onion", 1, "개"), ing("butter", 14, "g")], "soy", "돼지목살 지방감과 양송이버섯, 양파 버터의 달큰한 윤기", ["조림", "돼지목살", "양송이버섯"], servings=2),
            recipe_spec("파프리카 양송이 치즈그라탕", "그라탕", 75, 1, [ing("pepper", 1, "개"), ing("mushroom", 6, "개"), ing("cheese", 60, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("milk", 60, "ml")], "cream", "파프리카 단맛과 양송이버섯, 치즈의 부드러운 고소함", ["그라탕", "파프리카", "양송이버섯"]),
            recipe_spec("감자 소고기 허브구이", "에어프라이어", 81, 0, [ing("potato", 2, "개"), ing("beef", 180, "g", variant_detail="구이용 소고기 큐브"), ing("onion"), ing("garlic")], "herb", "감자의 구운 고소함과 소고기 큐브의 진한 육향", ["에어프라이어", "감자", "소고기"], servings=2),
            recipe_spec("토마토 가지 달걀프리타타", "팬구이", 74, 1, [ing("tomato", 1, "개"), ing("eggplant"), ing("egg", 3, "개"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "herb", "토마토 산미와 가지, 달걀의 부드러운 식감", ["프리타타", "토마토", "가지"]),
            recipe_spec("표고 닭다리살 간장구이", "팬구이", 83, 0, [ing("chicken", 240, "g"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="도톰하게 썬 생표고버섯"), ing("green_onion", 0.7, "대"), ing("garlic")], "soy", "표고버섯 우마미와 닭다리살 간장 구운 향", ["팬구이", "닭다리살", "표고버섯"], servings=2),
            recipe_spec("브로콜리 베이컨 체다구이", "에어프라이어", 77, 1, [ing("broccoli", 130, "g"), ing("bacon", 3, "줄"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("garlic", 1, "쪽")], "parsley", "브로콜리와 베이컨, 체다의 짭짤한 구운 향", ["에어프라이어", "브로콜리", "체다"]),
            recipe_spec("상추 소고기 토마토샐러드", "샐러드", 72, 0, [ing("beef", 150, "g", variant_detail="얇게 구운 소고기 채끝"), ing("lettuce", 6, "장"), ing("tomato", 1, "개"), ing("onion", 0.2, "개")], "vinegar", "소고기 구운 향과 상추, 토마토의 가벼운 산미", ["샐러드", "소고기", "토마토"]),
        ],
        "whisky": [
            recipe_spec("후추 소고기 베이컨 팽이버섯말이", "말이구이", 94, 0, [ing("beef", 110, "g", variant_detail="얇게 썬 불고기감 설도"), ing("bacon", 3, "줄"), ing("mushroom", 70, "g", display_name="팽이버섯", variant_detail="밑동을 제거한 팽이버섯")], "soy", "소고기와 베이컨의 훈연감, 팽이버섯의 촉촉한 식감", ["말이구이", "베이컨", "피트위스키"]),
            recipe_spec("브라운버터 대구살 팬구이", "팬구이", 91, 1, [ing("fish", 170, "g", display_name="대구살", variant_detail="가시 없는 냉동 또는 냉장 대구 필렛"), ing("butter", 28, "g"), ing("garlic", 3, "쪽")], ("flour", "lemon"), "브라운버터의 고소한 향과 대구살의 담백함", ["팬구이", "대구살", "브라운버터"]),
            recipe_spec("베이컨 브로콜리 후추구이", "구이", 86, 0, [ing("bacon", 3, "줄", variant_detail="도톰한 슬라이스 베이컨"), ing("broccoli", 140, "g"), ing("garlic", 2, "쪽")], "salt", "베이컨 훈연향과 브로콜리의 구운 가장자리, 후추 향", ["베이컨", "브로콜리", "피트위스키"]),
            recipe_spec("양송이 양파 밀크딥과 토스트", "딥", 83, 1, [ing("mushroom", 6, "개"), ing("onion", 0.6, "개"), ing("bread", 4, "조각"), ing("milk", 70, "ml"), ing("butter", 18, "g")], "cream", "양송이버섯과 양파를 오래 볶은 단짠 밀크딥", ["딥", "양송이버섯", "버번"]),
            recipe_spec("베이컨 애호박 말이 팬구이", "말이구이", 85, 0, [ing("zucchini", 0.7, "개"), ing("bacon", 6, "줄"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "salt", "애호박의 촉촉한 단맛과 베이컨의 짭짤한 구운 향", ["말이구이", "베이컨", "애호박"]),
            recipe_spec("후추버터 닭다리살 팬구이", "팬구이", 88, 1, [ing("chicken", 280, "g"), ing("butter", 16, "g"), ing("garlic", 4, "쪽"), ing("onion", 0.4, "개")], "herb", "닭다리살의 구운 지방감과 버터, 후추 향", ["팬구이", "닭다리살", "싱글몰트"], servings=2),
            recipe_spec("체다 소시지 달걀 에어프라이어컵", "에어프라이어", 73, 0, [ing("sausage", 5, "개"), ing("egg", 2, "개"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈")], "salt", "소시지 짠맛과 체다 달걀의 부드러운 지방감", ["에어프라이어", "소시지", "하이볼"]),
            recipe_spec("우유 치즈 감자 팬그라탕", "그라탕", 82, 1, [ing("potato", 2, "개"), ing("milk", 120, "ml"), ing("cheese", 55, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("butter", 12, "g")], "cream", "감자의 전분감과 우유, 치즈의 크리미한 고소함", ["그라탕", "감자", "셰리캐스크"]),
            recipe_spec("올리고당 버터 양배추 베이컨구이", "에어프라이어", 84, 0, [ing("cabbage", 0.25, "통", variant_detail="심지가 붙은 양배추 웨지"), ing("bacon", 3, "줄"), ing("butter", 20, "g")], "soy", "구운 양배추의 단맛과 베이컨, 버터의 단짠 향", ["에어프라이어", "양배추", "버번"], servings=2),
            recipe_spec("표고 돼지목살 꼬치구이", "꼬치구이", 88, 1, [ing("pork", 220, "g", variant_detail="도톰한 구이용 돼지목살"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="살이 두꺼운 생표고버섯"), ing("garlic", 6, "쪽")], "soy", "목살 구운 지방감과 표고버섯의 깊은 우마미", ["꼬치구이", "돼지목살", "표고버섯"], servings=2),
            recipe_spec("흰살생선 감자 베이컨 해시", "팬구이", 82, 0, [ing("fish", 120, "g", display_name="흰살생선", variant_detail="대구살 또는 동태살 순살"), ing("potato"), ing("bacon", 2, "줄")], "parsley", "베이컨 훈연감과 감자, 흰살생선의 바삭한 조각감", ["해시", "흰살생선", "하이볼"]),
            recipe_spec("캐러멜 양파 돼지목살 구이", "팬구이", 90, 1, [ing("pork", 300, "g", variant_detail="두툼한 구이용 돼지목살"), ing("onion", 1, "개"), ing("butter", 15, "g")], "salt", "천천히 볶은 양파 단맛과 돼지목살 구운 향", ["팬구이", "돼지목살", "버번"], servings=2),
            recipe_spec("체다 양파 돼지고기 미니볼", "팬구이", 84, 0, [ing("pork", 220, "g", variant_detail="돼지고기 앞다리살 다짐육"), ing("onion", 0.3, "개"), ing("egg", 1, "개"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("garlic", 1, "쪽")], "starch", "돼지고기 미니볼의 구운 육향과 체다의 짭짤한 고소함", ["미니볼", "돼지고기", "체다"], servings=2),
            recipe_spec("간장버터 표고 감자조림", "조림", 80, 1, [ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="살이 두꺼운 생표고버섯"), ing("potato"), ing("butter", 14, "g"), ing("garlic", 2, "쪽")], "soy", "표고버섯 우마미와 감자, 간장버터의 농축된 윤기", ["조림", "표고버섯", "감자"]),
            recipe_spec("체다 양송이 달걀 팬그라탕", "그라탕", 76, 1, [ing("egg", 2, "개"), ing("mushroom", 4, "개"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("milk", 40, "ml")], "salt", "양송이버섯 우마미와 체다 달걀의 부드러운 짠맛", ["팬그라탕", "달걀", "양송이버섯"]),
            recipe_spec("버터갈릭 소고기 감자구이", "팬구이", 89, 0, [ing("beef", 200, "g", variant_detail="구이용 소고기 큐브"), ing("potato", 1.5, "개"), ing("butter", 16, "g"), ing("garlic", 4, "쪽")], "salt", "소고기 육향과 감자, 마늘버터의 고소한 구운 맛", ["팬구이", "소고기", "감자"]),
            recipe_spec("베이컨 토마토 체다구이", "에어프라이어", 77, 1, [ing("bacon", 3, "줄"), ing("tomato", 6, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("onion", 0.2, "개")], "parsley", "베이컨 짠맛과 토마토 산미, 체다의 녹진함", ["에어프라이어", "베이컨", "체다"]),
            recipe_spec("훈연풍 소시지 파프리카꼬치", "꼬치구이", 78, 0, [ing("sausage", 6, "개"), ing("pepper", 1, "개"), ing("onion"), ing("mushroom", 4, "개")], "herb", "소시지 훈연감과 파프리카의 구운 단맛", ["꼬치구이", "소시지", "파프리카"], servings=2),
            recipe_spec("닭고기 체다 양배추구이", "에어프라이어", 81, 1, [ing("chicken", 220, "g"), ing("cabbage", 160, "g"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("garlic")], "herb", "닭고기와 양배추 구운 단맛, 체다의 짭짤함", ["에어프라이어", "닭고기", "체다"], servings=2),
            recipe_spec("돼지고기 브로콜리 버터볶음", "볶음", 79, 0, [ing("pork", 200, "g"), ing("broccoli", 130, "g"), ing("butter", 12, "g"), ing("garlic")], "salt", "돼지고기 구운 향과 브로콜리, 버터의 고소함", ["볶음", "돼지고기", "브로콜리"], servings=2),
            recipe_spec("표고 양파 버터감자딥", "딥", 75, 1, [ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="잘게 다진 생표고버섯"), ing("onion", 0.7, "개"), ing("potato", 1, "개"), ing("butter", 14, "g")], "cream", "표고와 양파의 농축된 단맛, 감자 딥의 되직함", ["딥", "표고버섯", "양파"]),
            recipe_spec("감자 베이컨 달걀전", "전", 72, 0, [ing("potato", 1.5, "개"), ing("bacon", 2, "줄"), ing("egg", 2, "개"), ing("onion", 0.2, "개")], "pancake", "감자전의 바삭함과 베이컨 달걀의 짭짤한 고소함", ["전", "감자", "베이컨"]),
            recipe_spec("연어 후추버터 팬구이", "팬구이", 83, 1, [ing("fish", 150, "g", display_name="연어", variant_detail="구이용 연어 필렛"), ing("butter", 14, "g"), ing("garlic", 2, "쪽"), ing("onion", 0.3, "개")], "lemon", "연어 지방감과 후추버터의 묵직한 고소함", ["팬구이", "연어", "후추버터"]),
            recipe_spec("소고기 표고 간장꼬치", "꼬치구이", 86, 0, [ing("beef", 200, "g", variant_detail="구이용 소고기 큐브"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="살이 두꺼운 생표고버섯"), ing("garlic", 5, "쪽")], "soy", "소고기 육향과 표고버섯의 짙은 감칠맛", ["꼬치구이", "소고기", "표고버섯"], servings=2),
            recipe_spec("양배추 체다 미니그라탕", "그라탕", 74, 1, [ing("cabbage", 180, "g"), ing("cheese", 2, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("milk", 70, "ml"), ing("bacon", 2, "줄")], "cream", "양배추 단맛과 체다, 베이컨의 짭짤한 그라탕감", ["그라탕", "양배추", "체다"]),
            recipe_spec("가지 베이컨 치즈말이", "말이구이", 80, 0, [ing("eggplant", 1.5, "개"), ing("bacon", 4, "줄"), ing("cheese", 50, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("garlic", 1, "쪽")], "herb", "가지의 부드러움과 베이컨, 치즈의 진한 한입감", ["말이구이", "가지", "베이컨"]),
            recipe_spec("닭고기 감자 간장버터조림", "조림", 82, 1, [ing("chicken", 230, "g"), ing("potato", 1.5, "개"), ing("butter", 12, "g"), ing("garlic")], "soy", "닭고기와 감자에 배인 간장버터의 단짠 윤기", ["조림", "닭고기", "감자"], servings=2),
            recipe_spec("돼지목살 파프리카 후추구이", "팬구이", 84, 0, [ing("pork", 260, "g", variant_detail="구이용 돼지목살"), ing("pepper", 1, "개"), ing("onion"), ing("garlic")], "herb", "돼지목살 구운 지방감과 파프리카, 후추 향", ["팬구이", "돼지목살", "파프리카"], servings=2),
            recipe_spec("양송이 버터 브로콜리구이", "에어프라이어", 73, 1, [ing("mushroom", 6, "개"), ing("broccoli", 130, "g"), ing("butter", 14, "g"), ing("garlic", 2, "쪽")], "parsley", "양송이버섯과 브로콜리의 구운 향, 버터리한 고소함", ["에어프라이어", "양송이버섯", "브로콜리"]),
            recipe_spec("소시지 감자 치즈팬구이", "팬구이", 76, 0, [ing("sausage", 6, "개"), ing("potato", 1.5, "개"), ing("cheese", 1, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("onion", 0.3, "개")], "salt", "소시지와 감자, 체다의 짭짤하고 고소한 팬구이맛", ["팬구이", "소시지", "감자"]),
        ],
        "sparkling_wine": [
            recipe_spec("오이 요거트 레몬 샐러드", "샐러드", 88, 0, [ing("cucumber"), ing("yogurt", 4, "큰술"), ing("garlic", 0.2, "쪽", variant_detail="생마늘을 아주 곱게 다져 사용")], "lemon", "오이의 수분감과 요거트 레몬 소스의 산뜻함", ["샐러드", "오이", "프로세코"]),
            recipe_spec("도미살 레몬 카르파초", "샐러드", 96, 1, [ing("fish", 120, "g", display_name="도미살", variant_detail="생식 가능한 횟감용 도미 필렛"), ing("onion", 0.2, "개"), ing("tomato", 4, "알", display_name="방울토마토", variant_detail="붉고 단단한 방울토마토")], "lemon", "도미살의 섬세한 감칠맛과 레몬 산미", ["카르파초", "도미", "샴페인"]),
            recipe_spec("파마산 베이컨 에그컵", "에어프라이어", 84, 0, [ing("bacon", 3, "줄"), ing("egg", 3, "개"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루")], "salt", "베이컨 짠맛과 달걀, 파마산의 고소한 핑거푸드감", ["에그컵", "베이컨", "카바"]),
            recipe_spec("파프리카 리코타 치즈보트", "에어프라이어", 87, 1, [ing("pepper", 3, "개", variant_detail="빨간 미니 파프리카 또는 작은 파프리카"), ing("cheese", 100, "g", display_name="리코타 치즈", variant_detail="수분감이 적당한 리코타 치즈"), ing("onion", 1, "큰술", variant_detail="곱게 다진 흰 양파")], "lemon", "파프리카의 아삭한 단맛과 리코타 치즈의 밀키함", ["핑거푸드", "파프리카", "리코타"]),
            recipe_spec("애호박 파마산 리본무침", "무침", 76, 0, [ing("zucchini", 0.5, "개", variant_detail="생식용으로 단단한 주키니형 애호박"), ing("cheese", 2, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루"), ing("garlic", 0.2, "쪽", variant_detail="생마늘을 아주 곱게 다져 사용")], "lemon", "얇은 애호박 리본과 파마산, 레몬의 가벼운 산미", ["무침", "애호박", "카바"]),
            recipe_spec("양송이 마늘버터 브루스케타", "오픈샌드", 80, 1, [ing("bread", 3, "조각"), ing("mushroom", 5, "개"), ing("butter", 18, "g"), ing("garlic", 1, "쪽")], "parsley", "구운 빵과 양송이버섯, 마늘버터의 고소함", ["브루스케타", "양송이버섯", "샴페인"]),
            recipe_spec("시금치 베이컨 미니 프리타타", "팬구이", 83, 0, [ing("spinach", 60, "g"), ing("egg", 2, "개"), ing("bacon", 1, "줄"), ing("milk", 1, "큰술")], "salt", "시금치의 은은한 단맛과 베이컨 달걀의 짭짤한 부드러움", ["프리타타", "시금치", "카바"]),
            recipe_spec("전분구이 닭안심 상추컵", "팬구이", 79, 1, [ing("chicken", 150, "g", display_name="닭안심", variant_detail="힘줄을 제거한 냉장 닭안심"), ing("lettuce", 4, "장"), ing("tomato", 0.5, "개")], ("starch", "mayo"), "바삭한 닭안심과 상추컵의 신선한 대비", ["핑거푸드", "닭안심", "프로세코"]),
            recipe_spec("모짜렐라 토마토 오이 레몬핀초", "샐러드", 82, 0, [ing("tomato", 6, "알", display_name="방울토마토", variant_detail="붉고 단단한 방울토마토"), ing("cucumber", 0.5, "개"), ing("cheese", 6, "알", display_name="모짜렐라 치즈", variant_detail="펄 또는 보코치니 생모짜렐라 치즈"), ing("onion", 0.15, "개")], "lemon", "모짜렐라와 토마토, 오이의 차가운 한입감", ["핀초", "모짜렐라", "프로세코"]),
            recipe_spec("당근 리본 리코타 샐러드", "샐러드", 74, 0, [ing("carrot", 1, "개"), ing("cheese", 80, "g", display_name="리코타 치즈", variant_detail="수분감이 적당한 리코타 치즈"), ing("yogurt", 2, "큰술")], "lemon", "당근의 은은한 단맛과 리코타, 요거트의 부드러운 산미", ["샐러드", "당근", "리코타"]),
            recipe_spec("브로콜리 체다 감자볼", "에어프라이어", 82, 1, [ing("broccoli", 100, "g"), ing("cheese", 2, "장", display_name="체다 치즈", variant_detail="체다 슬라이스 치즈"), ing("potato", 1, "개"), ing("egg", 1, "개")], "starch", "감자볼의 포슬함과 체다, 브로콜리의 고소한 한입감", ["감자볼", "브로콜리", "샴페인"]),
            recipe_spec("파마산 양배추 에어프라이어칩", "에어프라이어", 78, 0, [ing("cabbage", 120, "g"), ing("cheese", 2, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루"), ing("butter", 12, "g"), ing("garlic", 0.5, "쪽")], "salt", "양배추 가장자리의 바삭함과 파마산의 짭짤한 우마미", ["에어프라이어", "양배추", "브뤼"]),
            recipe_spec("감자 요거트 에그 샐러드", "샐러드", 73, 1, [ing("potato", 1, "개"), ing("egg", 1, "개"), ing("yogurt", 2, "큰술")], ("mayo", "lemon"), "감자와 달걀을 요거트로 가볍게 묶은 크리미함", ["샐러드", "감자", "프로세코"]),
            recipe_spec("흰살생선 파프리카 한입구이", "팬구이", 85, 0, [ing("fish", 220, "g", display_name="흰살생선", variant_detail="대구살 또는 동태살 순살"), ing("pepper", 1, "개"), ing("onion", 0.4, "개")], ("starch", "lemon"), "흰살생선의 담백함과 파프리카의 구운 단맛", ["팬구이", "흰살생선", "카바"], servings=2),
            recipe_spec("대구살 양배추 레몬마요 샐러드", "샐러드", 80, 0, [ing("fish", 140, "g", display_name="대구살", variant_detail="가시 없는 대구살 순살"), ing("cabbage", 180, "g"), ing("carrot", 30, "g")], "mayo", "대구살의 담백함과 양배추 레몬마요의 아삭한 산미", ["샐러드", "대구살", "샴페인"], servings=2),
            recipe_spec("연어 오이 레몬무침", "무침", 86, 1, [ing("fish", 120, "g", display_name="연어", variant_detail="생식 가능한 횟감용 연어 슬라이스"), ing("cucumber"), ing("onion", 0.15, "개"), ing("lettuce", 3, "장")], "lemon", "연어의 고소함과 오이, 레몬의 상쾌한 산미", ["무침", "연어", "프로세코"]),
            recipe_spec("닭고기 파프리카 콜드샐러드", "샐러드", 78, 0, [ing("chicken", 160, "g", variant_detail="익혀 찢은 닭안심"), ing("pepper", 1, "개"), ing("lettuce", 4, "장"), ing("cucumber", 0.5, "개")], "lemon", "닭안심과 파프리카를 차갑게 먹는 산뜻한 식감", ["샐러드", "닭고기", "파프리카"]),
            recipe_spec("토마토 리코타 달걀컵", "에어프라이어", 77, 1, [ing("tomato", 6, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("cheese", 70, "g", display_name="리코타 치즈", variant_detail="수분감이 적당한 리코타 치즈"), ing("egg", 2, "개"), ing("onion", 0.2, "개")], "parsley", "토마토 산미와 리코타, 달걀의 부드러운 고소함", ["에어프라이어", "리코타", "토마토"]),
            recipe_spec("브로콜리 요거트 딥볼", "딥", 72, 0, [ing("broccoli", 130, "g"), ing("yogurt", 4, "큰술"), ing("cucumber", 0.5, "개"), ing("garlic", 0.2, "쪽")], "lemon", "브로콜리와 요거트 딥의 가벼운 산미와 아삭함", ["딥", "브로콜리", "요거트"]),
            recipe_spec("양배추 당근 식초샐러드", "샐러드", 70, 1, [ing("cabbage", 180, "g"), ing("carrot", 0.5, "개"), ing("onion", 0.15, "개"), ing("cucumber", 0.5, "개")], "vinegar", "양배추와 당근의 아삭함, 식초 드레싱의 깔끔함", ["샐러드", "양배추", "당근"]),
            recipe_spec("대구살 오이 핀초", "샐러드", 81, 0, [ing("fish", 120, "g", display_name="대구살", variant_detail="익혀 식힌 대구살 순살"), ing("cucumber"), ing("cheese", 6, "알", display_name="모짜렐라 치즈", variant_detail="펄 생모짜렐라 치즈"), ing("tomato", 4, "알", display_name="방울토마토", variant_detail="단단한 방울토마토")], "lemon", "대구살과 오이, 모짜렐라를 한입에 먹는 산뜻함", ["핀초", "대구살", "오이"]),
            recipe_spec("상추 베이컨 토마토롤", "말이구이", 74, 1, [ing("lettuce", 6, "장"), ing("bacon", 3, "줄"), ing("tomato", 1, "개"), ing("cucumber", 0.5, "개")], "mayo", "상추와 토마토의 신선함, 베이컨의 짭짤한 포인트", ["말이구이", "상추", "베이컨"]),
            recipe_spec("애호박 달걀 미니전", "전", 71, 0, [ing("zucchini", 0.6, "개"), ing("egg", 2, "개"), ing("cheese", 1, "큰술", display_name="파마산 치즈", variant_detail="파마산 치즈 가루"), ing("green_onion", 0.2, "대")], "pancake", "애호박의 단맛과 달걀, 파마산의 얇은 고소함", ["전", "애호박", "달걀"]),
            recipe_spec("파프리카 모짜렐라 꼬치", "꼬치구이", 83, 1, [ing("pepper", 1, "개"), ing("cheese", 8, "알", display_name="모짜렐라 치즈", variant_detail="한입 크기 보코치니 모짜렐라"), ing("tomato", 8, "알", display_name="방울토마토", variant_detail="단단한 방울토마토"), ing("cucumber", 0.5, "개")], "lemon", "파프리카와 모짜렐라, 토마토의 화사한 한입감", ["꼬치", "모짜렐라", "스파클링로제"]),
            recipe_spec("시금치 리코타 레몬무침", "무침", 75, 0, [ing("spinach", 90, "g"), ing("cheese", 70, "g", display_name="리코타 치즈", variant_detail="수분감이 적당한 리코타 치즈"), ing("onion", 0.15, "개")], "lemon", "시금치의 은은한 단맛과 리코타 레몬의 부드러운 산미", ["무침", "시금치", "리코타"]),
            recipe_spec("감자 브로콜리 레몬마요", "샐러드", 73, 1, [ing("potato", 1, "개"), ing("broccoli", 100, "g"), ing("egg", 1, "개"), ing("yogurt", 1, "큰술")], "mayo", "감자와 브로콜리를 레몬마요로 묶은 포근한 산미", ["샐러드", "감자", "브로콜리"]),
            recipe_spec("흰살생선 토마토 냉샐러드", "샐러드", 84, 0, [ing("fish", 130, "g", display_name="흰살생선", variant_detail="익혀 식힌 대구살 또는 광어살"), ing("tomato", 1, "개"), ing("lettuce", 4, "장"), ing("onion", 0.15, "개")], "lemon", "차가운 흰살생선과 토마토 산미가 만든 깔끔함", ["샐러드", "흰살생선", "토마토"]),
            recipe_spec("오이 당근 요거트스틱딥", "딥", 69, 1, [ing("cucumber"), ing("carrot", 1, "개"), ing("yogurt", 4, "큰술"), ing("garlic", 0.2, "쪽")], "lemon", "오이와 당근 스틱에 찍는 요거트 딥의 산뜻함", ["딥", "오이", "당근"]),
            recipe_spec("닭안심 레몬 허브구이", "팬구이", 80, 0, [ing("chicken", 180, "g", display_name="닭안심", variant_detail="힘줄을 제거한 냉장 닭안심"), ing("garlic", 1, "쪽"), ing("lettuce", 3, "장"), ing("tomato", 0.5, "개")], "lemon", "닭안심의 담백함과 레몬 허브의 깔끔한 향", ["팬구이", "닭안심", "레몬"]),
            recipe_spec("양송이 토마토 치즈그라탕", "그라탕", 78, 1, [ing("mushroom", 6, "개"), ing("tomato", 1, "개"), ing("cheese", 60, "g", display_name="모짜렐라 치즈", variant_detail="슈레드 모짜렐라 치즈"), ing("garlic", 1, "쪽")], "parsley", "양송이버섯 채수와 토마토, 모짜렐라의 산뜻한 고소함", ["그라탕", "양송이버섯", "토마토"]),
        ],
        "sake": [
            recipe_spec("버터간장 양송이 볶음", "볶음", 92, 0, [ing("mushroom", 6, "개"), ing("butter", 10, "g"), ing("garlic", 3, "쪽")], "soy", "양송이버섯의 우마미와 버터간장 향", ["볶음", "양송이버섯", "준마이"]),
            recipe_spec("닭다리살 대파 간장구이", "팬구이", 94, 1, [ing("chicken", 220, "g"), ing("green_onion", 1, "대"), ing("garlic", 1, "쪽", variant_detail="생마늘을 곱게 다져 사용")], "soy", "구운 대파 단맛과 닭다리살의 고소함", ["구이", "닭다리살", "긴조"]),
            recipe_spec("양배추 돼지목살 겹찜", "찜", 88, 0, [ing("pork", 220, "g", variant_detail="얇게 슬라이스한 돼지목살"), ing("cabbage", 300, "g"), ing("mushroom", 0.5, "봉", display_name="팽이버섯", variant_detail="신선한 팽이버섯")], "vinegar", "양배추 단맛과 돼지목살의 담백한 지방감", ["찜", "돼지목살", "준마이"], servings=2),
            recipe_spec("애호박 대파 달걀전", "전", 74, 1, [ing("zucchini", 0.5, "개"), ing("egg", 2, "개"), ing("green_onion", 0.3, "대")], "pancake", "애호박의 달큰함과 대파 달걀의 고소함", ["전", "애호박", "긴조"]),
            recipe_spec("맑은 대구살 느타리탕", "탕", 96, 0, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살 필렛"), ing("mushroom", 60, "g", display_name="느타리버섯", variant_detail="결대로 찢은 느타리버섯"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽")], "salt", "대구살의 맑은 감칠맛과 느타리버섯 우마미", ["탕", "대구살", "다이긴조"]),
            recipe_spec("간장 가지 대파조림", "조림", 84, 1, [ing("eggplant"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽", variant_detail="생마늘을 굵게 다져 사용")], "soy", "가지가 머금은 간장 감칠맛과 대파 향", ["조림", "가지", "준마이"]),
            recipe_spec("오이 횟감 흰살생선 초무침", "무침", 73, 0, [ing("fish", 90, "g", display_name="흰살생선", variant_detail="생식 가능한 횟감용 광어 또는 도미 슬라이스"), ing("cucumber"), ing("onion", 0.25, "개")], "vinegar", "흰살생선의 담백함과 오이의 아삭한 산미", ["무침", "횟감", "긴조"]),
            recipe_spec("브로콜리 팽이버섯 간장무침", "무침", 76, 1, [ing("broccoli", 120, "g"), ing("mushroom", 80, "g", display_name="팽이버섯", variant_detail="밑동을 제거한 신선한 팽이버섯"), ing("green_onion", 0.2, "대")], "vinegar", "브로콜리의 단맛과 팽이버섯의 가벼운 감칠맛", ["무침", "브로콜리", "팽이버섯"]),
            recipe_spec("시금치 달걀 부드러운 볶음", "볶음", 72, 0, [ing("spinach", 100, "g"), ing("egg", 2, "개"), ing("garlic", 1, "쪽")], "salt", "시금치의 은은한 단맛과 몽글한 달걀 식감", ["볶음", "시금치", "달걀"]),
            recipe_spec("표고 대파 달걀찜", "달걀찜", 87, 1, [ing("egg", 2, "개"), ing("mushroom", 2, "개", display_name="표고버섯", variant_detail="얇게 편 썬 생표고버섯"), ing("green_onion", 1, "큰술"), ing("milk", 40, "ml")], "soy", "표고버섯 우마미와 대파 달걀찜의 부드러움", ["달걀찜", "표고버섯", "준마이"]),
            recipe_spec("닭고기 표고버섯 맑은 전골", "전골", 93, 0, [ing("chicken", 260, "g"), ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="신선한 생표고버섯"), ing("cabbage", 140, "g"), ing("garlic", 1, "쪽")], "salt", "표고버섯 향과 닭고기, 양배추가 만든 맑은 국물감", ["전골", "닭고기", "표고버섯"], servings=2),
            recipe_spec("연어 파프리카 호일구이", "에어프라이어", 87, 1, [ing("fish", 150, "g", display_name="연어", variant_detail="구이용 연어 필렛"), ing("pepper", 0.5, "개"), ing("butter", 10, "g")], "herb", "연어 지방감과 파프리카 채수, 버터의 부드러운 향", ["에어프라이어", "연어", "니고리"]),
            recipe_spec("표고 대파 감자조림", "조림", 80, 0, [ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="살이 두꺼운 생표고버섯"), ing("potato", 1, "개"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽")], "soy", "표고버섯과 감자, 대파에 밴 간장 우마미", ["조림", "표고버섯", "감자"]),
            recipe_spec("돼지고기 양배추 샤부샐러드", "샐러드", 82, 1, [ing("pork", 160, "g", variant_detail="얇은 대패 목살 또는 앞다리살"), ing("cabbage", 160, "g"), ing("cucumber", 0.5, "개")], "vinegar", "데친 돼지고기와 양배추, 오이의 가벼운 산미", ["샐러드", "돼지고기", "긴조"], servings=2),
            recipe_spec("대파 우유 달걀말이", "달걀말이", 90, 0, [ing("egg", 3, "개"), ing("green_onion", 2, "큰술"), ing("milk", 2, "큰술")], "salt", "우유를 넣어 부드러운 대파 달걀말이의 은은한 단맛", ["달걀말이", "대파", "준마이"]),
            recipe_spec("대구살 양파 간장찜", "찜", 85, 1, [ing("fish", display_name="대구살", variant_detail="뼈 없는 대구살 순살"), ing("onion", 0.7, "개"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽")], "soy", "대구살의 담백함과 양파 간장 채수의 은은한 감칠맛", ["찜", "대구살", "양파"]),
            recipe_spec("닭안심 양송이 소금구이", "팬구이", 81, 0, [ing("chicken", 180, "g", display_name="닭안심", variant_detail="힘줄을 제거한 닭안심"), ing("mushroom", 5, "개"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽")], "salt", "닭안심의 담백함과 양송이버섯의 은은한 구운 향", ["팬구이", "닭안심", "양송이버섯"]),
            recipe_spec("오이 양파 식초무침", "무침", 68, 1, [ing("cucumber"), ing("onion", 0.3, "개"), ing("carrot", 0.3, "개")], "vinegar", "오이와 양파, 당근의 깔끔한 아삭함", ["무침", "오이", "긴조"]),
            recipe_spec("연어 양배추 맑은찜", "찜", 86, 0, [ing("fish", 150, "g", display_name="연어", variant_detail="구이용 연어 필렛"), ing("cabbage", 160, "g"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽")], "salt", "연어 지방감과 양배추 채수의 차분한 단맛", ["찜", "연어", "니고리"]),
            recipe_spec("표고 브로콜리 간장구이", "팬구이", 78, 1, [ing("mushroom", 4, "개", display_name="표고버섯", variant_detail="도톰하게 썬 생표고버섯"), ing("broccoli", 120, "g"), ing("garlic", 1, "쪽"), ing("green_onion", 0.3, "대")], "soy", "표고버섯 우마미와 브로콜리의 가벼운 구운 향", ["팬구이", "표고버섯", "브로콜리"]),
            recipe_spec("가지 달걀 소이찜", "찜", 75, 0, [ing("eggplant"), ing("egg", 2, "개"), ing("green_onion", 0.4, "대"), ing("milk", 30, "ml")], "soy", "가지의 촉촉함과 달걀찜 같은 부드러운 간장 향", ["찜", "가지", "달걀"]),
            recipe_spec("흰살생선 토마토 맑은탕", "탕", 83, 1, [ing("fish", display_name="흰살생선", variant_detail="가시 없는 대구살 또는 광어살"), ing("tomato", 1, "개"), ing("green_onion", 0.5, "대"), ing("garlic", 1, "쪽")], "salt", "흰살생선의 맑은 감칠맛과 토마토의 가벼운 산미", ["탕", "흰살생선", "토마토"]),
            recipe_spec("돼지고기 대파 소금구이", "팬구이", 79, 0, [ing("pork", 220, "g", variant_detail="얇게 썬 돼지 앞다리살"), ing("green_onion", 1, "대"), ing("onion", 0.4, "개"), ing("garlic", 2, "쪽")], "salt", "돼지고기와 대파의 단순하고 담백한 구운 향", ["팬구이", "돼지고기", "대파"]),
            recipe_spec("양송이 시금치 간장무침", "무침", 74, 1, [ing("mushroom", 5, "개"), ing("spinach", 80, "g"), ing("green_onion", 0.2, "대"), ing("garlic", 0.5, "쪽")], "soy", "양송이버섯과 시금치의 부드러운 감칠맛", ["무침", "양송이버섯", "시금치"]),
            recipe_spec("닭고기 감자 맑은조림", "조림", 82, 0, [ing("chicken", 220, "g"), ing("potato", 1, "개"), ing("carrot", 0.4, "개"), ing("green_onion", 0.4, "대")], "soy", "닭고기와 감자를 자극 없이 조린 담백한 단짠 맛", ["조림", "닭고기", "감자"], servings=2),
            recipe_spec("달걀 토마토 사케풍찜", "달걀찜", 73, 1, [ing("egg", 2, "개"), ing("tomato", 0.8, "개"), ing("green_onion", 0.3, "대"), ing("milk", 40, "ml")], "salt", "토마토 산미와 달걀의 부드러운 수분감", ["달걀찜", "토마토", "달걀"]),
            recipe_spec("팽이버섯 닭고기 말이구이", "말이구이", 80, 0, [ing("mushroom", 90, "g", display_name="팽이버섯", variant_detail="밑동을 제거한 팽이버섯"), ing("chicken", 180, "g", variant_detail="얇게 펼친 닭다리살 정육"), ing("garlic", 1, "쪽")], "soy", "팽이버섯의 촉촉한 식감과 닭고기 간장 구운 향", ["말이구이", "팽이버섯", "닭고기"]),
            recipe_spec("오이 대구살 당근 레몬초무침", "무침", 77, 1, [ing("cucumber"), ing("fish", 100, "g", display_name="대구살", variant_detail="익혀 식힌 대구살 순살"), ing("carrot", 0.3, "개"), ing("onion", 0.15, "개")], "lemon", "대구살의 담백함과 오이, 당근, 레몬의 깔끔한 산미", ["무침", "대구살", "오이"]),
            recipe_spec("양배추 대파 달걀탕", "탕", 72, 0, [ing("cabbage", 140, "g"), ing("green_onion", 0.7, "대"), ing("egg", 2, "개"), ing("garlic", 0.5, "쪽")], "salt", "양배추 단맛과 대파 달걀이 만든 맑은 국물감", ["탕", "양배추", "달걀"]),
            recipe_spec("연어 양송이 버터간장구이", "팬구이", 84, 1, [ing("fish", 150, "g", display_name="연어", variant_detail="구이용 연어 필렛"), ing("mushroom", 5, "개"), ing("butter", 10, "g"), ing("garlic", 1, "쪽")], "soy", "연어의 고소한 지방감과 양송이버섯 버터간장 향", ["팬구이", "연어", "양송이버섯"]),
        ],
    }


def build_recipes() -> list[dict[str, Any]]:
    specs_by_liquor = build_specs()
    recipes: list[dict[str, Any]] = []
    for liquor_name, specs in specs_by_liquor.items():
        for index, spec in enumerate(specs):
            recipes.append(make_recipe(liquor_name, spec, index))
    return recipes


def validate(recipes: list[dict[str, Any]]) -> None:
    errors: list[str] = []
    counts = Counter(recipe["liquor_name"] for recipe in recipes)
    expected_liquors = set(LIQUOR_PROFILES)

    if set(counts) != expected_liquors:
        errors.append(f"liquor set mismatch: {sorted(counts)}")
    for liquor in sorted(expected_liquors):
        if counts[liquor] != 30:
            errors.append(f"{liquor} count must be 30, got {counts[liquor]}")

    names = [recipe["name"] for recipe in recipes]
    duplicate_names = [name for name, count in Counter(names).items() if count > 1]
    if duplicate_names:
        errors.append(f"duplicate recipe names: {duplicate_names}")

    per_liquor_methods: dict[str, Counter[str]] = defaultdict(Counter)
    per_liquor_bread: Counter[str] = Counter()
    per_liquor_jeon: Counter[str] = Counter()
    per_liquor_combos: dict[str, set[tuple[str, ...]]] = defaultdict(set)

    for recipe in recipes:
        liquor = recipe["liquor_name"]
        name = recipe["name"]
        method = recipe["tags"][0]
        per_liquor_methods[liquor][method] += 1

        if recipe["refresh_group"] not in {0, 1}:
            errors.append(f"{name}: invalid refresh_group")
        if not 60 <= recipe["rank_hint"] <= 100:
            errors.append(f"{name}: invalid rank_hint")
        if len(recipe["ingredient_details"]) < 3:
            errors.append(f"{name}: ingredient_details must have at least 3 items")
        if len(recipe["pantry_items"]) < 2:
            errors.append(f"{name}: pantry_items must have at least 2 items")
        if len(recipe["recipe_steps"]) < 4:
            errors.append(f"{name}: recipe_steps must have at least 4 steps")

        combo = tuple(sorted(item["item_name"] for item in recipe["ingredient_details"]))
        if combo in per_liquor_combos[liquor]:
            errors.append(f"{liquor}/{name}: duplicate core ingredient combo {combo}")
        per_liquor_combos[liquor].add(combo)

        if "bread" in combo:
            per_liquor_bread[liquor] += 1
        if method == "전":
            per_liquor_jeon[liquor] += 1

        for ingredient in recipe["ingredient_details"]:
            item_name = ingredient["item_name"]
            if item_name not in ALLOWED_KEYS:
                errors.append(f"{name}: invalid ingredient key {item_name}")
            if item_name in {"fish", "mushroom", "cheese"} and not ingredient.get("variant_detail"):
                errors.append(f"{name}: {item_name} requires variant_detail")
            if item_name == "pepper":
                text = f"{ingredient.get('display_name', '')} {ingredient.get('variant_detail', '')}"
                if "파프리카" not in text or "고추" in text:
                    errors.append(f"{name}: pepper must mean paprika only")

        for pantry_item in recipe["pantry_items"]:
            if pantry_item["name"] not in PANTRY_ALLOWED:
                errors.append(f"{name}: invalid pantry item {pantry_item['name']}")

        expected_step_numbers = list(range(1, len(recipe["recipe_steps"]) + 1))
        actual_step_numbers = [step["step_number"] for step in recipe["recipe_steps"]]
        if actual_step_numbers != expected_step_numbers:
            errors.append(f"{name}: step numbers are not sequential")
        for step in recipe["recipe_steps"]:
            if step["heat_level"] not in HEAT_LEVELS:
                errors.append(f"{name}: invalid heat_level {step['heat_level']}")
            for field in ("instruction", "success_cue"):
                text = step[field]
                if text.endswith("다.") or text.endswith("한다."):
                    errors.append(f"{name}: {field} is not user-friendly polite tone")

        tone_fields = [
            recipe["reason"],
            recipe["pairing_knowledge"]["flavor_logic"],
            recipe["pairing_knowledge"]["ingredient_logic"],
            recipe["pairing_knowledge"]["why_this_liquor"],
            recipe["tip"],
        ]
        if any(text.endswith("다.") or "안주다" in text for text in tone_fields):
            errors.append(f"{name}: user-facing tone needs polite service copy")

    for liquor, method_counts in per_liquor_methods.items():
        if len(method_counts) < 5:
            errors.append(f"{liquor}: must include at least 5 cooking methods")
        if method_counts["볶음"] > 4:
            errors.append(f"{liquor}: stir-fry recipes exceed 4")
        if per_liquor_bread[liquor] > 1:
            errors.append(f"{liquor}: bread-based recipes exceed 1")
        if per_liquor_jeon[liquor] > 1:
            errors.append(f"{liquor}: jeon recipes exceed 1")

    if errors:
        raise SystemExit("\n".join(errors))


def main() -> None:
    recipes = build_recipes()
    validate(recipes)
    payload = polish_payload({"recipes": recipes})
    SEED_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    counts = Counter(recipe["liquor_name"] for recipe in recipes)
    print(f"wrote {len(recipes)} recipes to {SEED_PATH}")
    for liquor in sorted(counts):
        methods = Counter(recipe["tags"][0] for recipe in recipes if recipe["liquor_name"] == liquor)
        print(f"{liquor}: {counts[liquor]} recipes, methods={dict(sorted(methods.items()))}")


if __name__ == "__main__":
    main()
