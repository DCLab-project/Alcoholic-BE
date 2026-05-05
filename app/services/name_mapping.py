from __future__ import annotations

from typing import Mapping


INGREDIENT_DISPLAY_NAMES: dict[str, str] = {
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

LIQUOR_DISPLAY_NAMES: dict[str, str] = {
    "soju": "소주",
    "beer": "맥주",
    "white_wine": "화이트와인",
    "red_wine": "레드와인",
    "whisky": "위스키",
    "sparkling_wine": "스파클링와인",
    "sake": "사케",
}

_INGREDIENT_ALIASES: dict[str, tuple[str, ...]] = {
    "beef": ("소고기", "쇠고기"),
    "bread": ("빵", "식빵", "바게트", "토스트"),
    "broccoli": ("브로콜리",),
    "butter": ("버터",),
    "cabbage": ("양배추",),
    "carrot": ("당근",),
    "cheese": ("치즈", "모짜렐라", "모차렐라", "체다", "파마산", "리코타"),
    "chicken": ("닭고기", "닭", "닭다리살", "닭안심", "닭가슴살"),
    "cucumber": ("오이",),
    "egg": ("달걀", "계란"),
    "eggplant": ("가지",),
    "fish": (
        "생선살",
        "생선",
        "흰살생선",
        "대구",
        "대구살",
        "고등어",
        "참치",
        "광어",
        "동태",
        "동태살",
    ),
    "garlic": ("마늘", "다진마늘", "다진 마늘", "통마늘"),
    "leek": (
        "대파",
        "파",
        "leek",
        "green_onion",
        "green onion",
        "spring_onion",
        "spring onion",
        "scallion",
    ),
    "lettuce": ("상추", "쌈상추", "로메인"),
    "milk": ("우유",),
    "mushroom": (
        "버섯",
        "양송이",
        "양송이버섯",
        "표고",
        "표고버섯",
        "팽이",
        "팽이버섯",
        "새송이",
        "새송이버섯",
    ),
    "onion": ("양파",),
    "pepper": (
        "파프리카",
        "빨간파프리카",
        "노란파프리카",
        "빨간 파프리카",
        "노란 파프리카",
        "bellpepper",
        "bell pepper",
    ),
    "pork": (
        "돼지고기",
        "돼지",
        "돼지목살",
        "목살",
        "삼겹살",
        "대패삼겹살",
        "돼지안심",
        "돼지앞다리살",
    ),
    "potato": ("감자",),
    "sausage": ("소시지", "소세지", "비엔나", "비엔나소시지", "비엔나 소시지"),
    "tomato": ("토마토", "방울토마토"),
    "zucchini": ("애호박", "주키니", "쥬키니", "호박"),
    "lemon": ("레몬",),
    "avocado": ("아보카도",),
    "radish": ("무", "무우", "조선무"),
    "tofu": ("두부",),
    "ginger": ("생강",),
    "salmon": ("연어", "연어살"),
}

_LIQUOR_ALIASES: dict[str, tuple[str, ...]] = {
    "soju": ("소주",),
    "beer": ("맥주",),
    "white_wine": ("화이트와인", "화이트 와인", "whitewine"),
    "red_wine": ("레드와인", "레드 와인", "와인", "redwine", "wine"),
    "whisky": ("위스키", "whiskey"),
    "sparkling_wine": (
        "스파클링와인",
        "스파클링 와인",
        "스파클링",
        "샴페인",
        "프로세코",
        "카바",
        "sparklingwine",
    ),
    "sake": ("사케", "청주"),
}


def _token(value: str) -> str:
    return value.strip().lower().replace(" ", "").replace("-", "").replace("_", "")


def _build_alias_map(
    display_names: Mapping[str, str],
    aliases: Mapping[str, tuple[str, ...]],
) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for key, display_name in display_names.items():
        alias_map[_token(key)] = key
        alias_map[_token(display_name)] = key
        for alias in aliases.get(key, ()):
            alias_map[_token(alias)] = key
    return alias_map


_INGREDIENT_ALIAS_MAP = _build_alias_map(INGREDIENT_DISPLAY_NAMES, _INGREDIENT_ALIASES)
_LIQUOR_ALIAS_MAP = _build_alias_map(LIQUOR_DISPLAY_NAMES, _LIQUOR_ALIASES)


def _unknown_key(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return stripped
    return stripped.lower().replace(" ", "_") if stripped.isascii() else stripped


def normalize_ingredient_key(value: str) -> str:
    return _INGREDIENT_ALIAS_MAP.get(_token(value), _unknown_key(value))


def normalize_liquor_key(value: str) -> str:
    return _LIQUOR_ALIAS_MAP.get(_token(value), _unknown_key(value))


def ingredient_display_name(value: str) -> str:
    key = normalize_ingredient_key(value)
    return INGREDIENT_DISPLAY_NAMES.get(key, value.strip())


def liquor_display_name(value: str) -> str:
    key = normalize_liquor_key(value)
    return LIQUOR_DISPLAY_NAMES.get(key, value.strip())
