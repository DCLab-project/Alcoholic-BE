from app.config.settings import Settings
from app.services.gemini_recommendation_service import (
    GeminiIngredient,
    GeminiPairingKnowledge,
    GeminiPantryItem,
    GeminiRecipeCandidate,
    GeminiRecipeStep,
    GeminiRecommendationService,
)
from app.services.name_mapping import ingredient_display_name, normalize_ingredient_key


def _candidate(item_name: str = "egg") -> GeminiRecipeCandidate:
    return GeminiRecipeCandidate(
        name="대파 달걀 간장구이",
        reason="대파와 달걀을 노릇하게 구워 소주와 잘 맞는 담백한 안주입니다.",
        servings=1,
        cook_time_minutes=18,
        difficulty="easy",
        pairing_knowledge=GeminiPairingKnowledge(
            flavor_logic="구운 대파의 단맛과 달걀의 고소함이 술맛을 부드럽게 받쳐줍니다.",
            ingredient_logic="달걀은 풀어서 굽고 대파는 마지막에 넣어 향을 살립니다.",
            why_this_liquor="소주의 깔끔한 끝맛이 간장 양념과 구운 향을 정리해줍니다.",
        ),
        ingredient_details=[
            GeminiIngredient(
                item_name="green_onion",
                variant_detail="굵은 대파",
                amount=1,
                unit="대",
            ),
            GeminiIngredient(
                item_name=item_name,
                variant_detail="잘 풀어둔 달걀",
                amount=2,
                unit="개",
            ),
        ],
        pantry_items=[
            GeminiPantryItem(name="식용유", amount=1, unit="큰술"),
            GeminiPantryItem(name="간장", amount=1, unit="큰술"),
        ],
        recipe_steps=[
            GeminiRecipeStep(
                step_number=index,
                title=f"{index}단계",
                instruction=f"재료 {index}가 잘 보이도록 1분 동안 천천히 준비하세요.",
                time_minutes=1,
                heat_level="없음" if index <= 2 else "중불",
                success_cue="재료 상태가 고르게 맞으면 좋아요.",
            )
            for index in range(1, 7)
        ],
        tip="달걀은 약불에서 천천히 익히면 팬에 덜 달라붙습니다.",
        tags=["구이", "소주"],
    )


def test_green_onion_is_canonical_and_leek_is_legacy_alias() -> None:
    assert normalize_ingredient_key("green_onion") == "green_onion"
    assert normalize_ingredient_key("leek") == "green_onion"
    assert ingredient_display_name("green_onion") == "대파"


def test_candidate_to_recommendation_recomputes_inventory_status() -> None:
    service = GeminiRecommendationService(Settings(gemini_api_key=""))

    item = service._candidate_to_recommendation(
        _candidate(),
        liquor_key="soju",
        inventory_counts={"green_onion": 1},
        rank=2,
        available_only=False,
        max_missing_count=None,
        max_cook_time_minutes=None,
        difficulty=None,
    )

    assert item is not None
    assert item.recommendation_source == "llm_fallback"
    assert item.priority_rank == 2
    assert item.ingredient_yes == ["대파"]
    assert item.ingredient_no == ["달걀"]
    assert item.missing_ingredients == ["달걀"]
    assert item.shopping_items == ["달걀"]
    assert [detail.status for detail in item.ingredient_details] == [
        "available",
        "missing",
    ]
    assert len(item.recipe_steps) == 6


def test_candidate_to_recommendation_rejects_retired_ingredient_key() -> None:
    service = GeminiRecommendationService(Settings(gemini_api_key=""))

    item = service._candidate_to_recommendation(
        _candidate("bacon"),
        liquor_key="soju",
        inventory_counts={"green_onion": 1},
        rank=1,
        available_only=False,
        max_missing_count=None,
        max_cook_time_minutes=None,
        difficulty=None,
    )

    assert item is None


def test_generate_fallback_returns_empty_without_api_key() -> None:
    service = GeminiRecommendationService(Settings(gemini_api_key=""))

    assert (
        service.generate_fallback_recommendations(
            liquor_key="soju",
            inventory_counts={"green_onion": 1},
            needed_count=1,
            start_rank=3,
            existing_names=[],
            selected_names=[],
            available_only=False,
            max_missing_count=None,
            max_cook_time_minutes=None,
            difficulty=None,
        )
        == []
    )


def test_build_prompt_includes_strict_filter_requirements() -> None:
    service = GeminiRecommendationService(Settings(gemini_api_key=""))

    prompt = service._build_prompt(
        liquor_key="soju",
        inventory_counts={"green_onion": 2, "pork": 1},
        needed_count=1,
        existing_names=[],
        selected_names=[],
        available_only=True,
        max_missing_count=0,
        max_cook_time_minutes=10,
        difficulty="easy",
    )

    assert "ingredient_details[].item_name MUST be only these fridge keys: green_onion, pork" in prompt
    assert "missing core ingredient count MUST be <= 0" in prompt
    assert "cook_time_minutes MUST be <= 10" in prompt
    assert 'difficulty MUST be exactly "easy"' in prompt
    assert "pantry_items[].name and pantry_items[].unit must be Korean" in prompt


def test_build_prompt_limits_existing_name_examples() -> None:
    service = GeminiRecommendationService(Settings(gemini_api_key=""))
    existing_names = [f"기존 레시피 {index}" for index in range(20)]

    prompt = service._build_prompt(
        liquor_key="soju",
        inventory_counts={"green_onion": 2},
        needed_count=1,
        existing_names=existing_names,
        selected_names=[],
        available_only=False,
        max_missing_count=None,
        max_cook_time_minutes=None,
        difficulty=None,
    )

    assert "기존 레시피 11" in prompt
    assert "기존 레시피 12" not in prompt


def test_generate_fallback_retries_after_failed_payload(monkeypatch) -> None:
    service = GeminiRecommendationService(Settings(gemini_api_key="test-key"))
    payloads = [None, {"recommendations": [_candidate().model_dump(mode="json")]}]

    def fake_call_gemini(prompt: str):
        return payloads.pop(0)

    monkeypatch.setattr(service, "_call_gemini", fake_call_gemini)

    items = service.generate_fallback_recommendations(
        liquor_key="soju",
        inventory_counts={"green_onion": 1},
        needed_count=1,
        start_rank=1,
        existing_names=[],
        selected_names=[],
        available_only=False,
        max_missing_count=None,
        max_cook_time_minutes=None,
        difficulty="easy",
    )

    assert len(items) == 1
    assert items[0].recommendation_source == "llm_fallback"
    assert payloads == []
