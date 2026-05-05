import json
import time
from typing import Any

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import (
    RecommendationIngredientDetail,
    RecommendationItem,
    RecommendationPairingKnowledge,
    RecommendationPantryItem,
    RecommendationRecipeStep,
    RecommendationRefreshRequest,
    RecommendationRefreshResponse,
    RecommendationScoreBreakdown,
    RecommendationSubstitutionTip,
    RecommendationsResponse,
)
from app.services.gemini_recommendation_service import GeminiRecommendationService
from app.services.name_mapping import (
    ingredient_display_name,
    liquor_display_name,
    normalize_ingredient_key,
    normalize_liquor_key,
)


_RECOMMENDATION_REFRESH_CURSORS: dict[str, int] = {}

_SUBSTITUTION_TIP_BY_DISPLAY_NAME: dict[str, tuple[str, str]] = {
    "돼지고기": (
        "소고기 또는 닭고기",
        "고기 종류가 바뀌면 같은 크기로 썰고 중심까지 익혀주세요.",
    ),
    "소고기": (
        "돼지고기 또는 닭고기",
        "기름기가 달라질 수 있으니 처음에는 중불로 익혀주세요.",
    ),
    "닭고기": (
        "돼지고기 또는 두부",
        "닭고기 대신 다른 단백질을 쓰면 속까지 익는 시간을 다시 확인해주세요.",
    ),
    "생선": (
        "연어 또는 닭고기",
        "생선 대신 고기를 쓰면 비린내 잡는 양념은 줄여도 좋아요.",
    ),
    "생선살": (
        "연어 또는 닭고기",
        "생선살 대신 고기를 쓰면 비린내 잡는 양념은 줄여도 좋아요.",
    ),
    "연어": (
        "생선 또는 닭고기",
        "연어 대신 흰살생선을 쓰면 굽는 시간을 1분 정도 줄여주세요.",
    ),
    "달걀": (
        "두부 또는 치즈",
        "달걀을 빼면 결착력이 약해질 수 있어 재료를 작게 썰어주세요.",
    ),
    "두부": (
        "달걀 또는 닭고기",
        "두부 대신 고기를 쓰면 간을 조금 약하게 시작하세요.",
    ),
    "버섯": (
        "가지 또는 애호박",
        "버섯의 감칠맛이 줄어들 수 있어 간장이나 마늘을 조금 보강하세요.",
    ),
    "가지": (
        "버섯 또는 애호박",
        "수분이 많은 재료로 바뀌면 센불보다 중불에서 천천히 구워주세요.",
    ),
    "양파": (
        "대파 또는 마늘",
        "단맛이 덜하면 마지막에 약불로 1분 더 볶아주세요.",
    ),
    "대파": (
        "양파 또는 마늘",
        "대파 향이 줄어드니 팬에 먼저 볶아 향을 내주세요.",
    ),
    "마늘": (
        "대파 또는 양파",
        "마늘 향이 빠지면 후추나 버터를 조금 더해도 좋아요.",
    ),
    "파프리카": (
        "당근 또는 양배추",
        "식감이 달라지므로 너무 오래 볶지 않는 쪽이 좋아요.",
    ),
    "당근": (
        "파프리카 또는 양배추",
        "당근 대신 다른 채소를 쓰면 볶는 시간을 조금 줄여도 좋아요.",
    ),
    "양배추": (
        "양파 또는 무",
        "단맛과 수분이 달라질 수 있으니 마지막 간을 다시 확인하세요.",
    ),
    "브로콜리": (
        "양배추 또는 애호박",
        "브로콜리 대신 부드러운 채소를 쓰면 데치는 시간은 생략해도 좋아요.",
    ),
    "토마토": (
        "레몬 또는 파프리카",
        "산미가 부족하면 레몬즙을 아주 조금 더해도 좋아요.",
    ),
    "레몬": (
        "토마토 또는 식초",
        "레몬이 없으면 산미를 조금만 넣고 맛을 보며 조절하세요.",
    ),
    "치즈": (
        "버터 또는 우유",
        "고소함은 유지되지만 짠맛이 줄어들 수 있어 간을 확인하세요.",
    ),
    "버터": (
        "식용유 또는 치즈",
        "버터 향이 줄어드니 마지막에 고소한 재료를 조금 더해도 좋아요.",
    ),
    "빵": (
        "감자 또는 양배추",
        "포만감이 달라지므로 양을 조금 넉넉히 잡아주세요.",
    ),
    "우유": (
        "치즈 또는 버터",
        "부드러움이 달라질 수 있으니 소스 농도를 보며 조금씩 넣어주세요.",
    ),
    "감자": (
        "빵 또는 애호박",
        "감자 대신 수분 많은 재료를 쓰면 굽는 시간을 줄여주세요.",
    ),
    "무": (
        "양배추 또는 오이",
        "시원한 맛은 줄어들 수 있어 간을 마지막에 다시 맞춰주세요.",
    ),
    "오이": (
        "무 또는 상추",
        "아삭함을 살리려면 조리 마지막에 넣거나 생으로 곁들이세요.",
    ),
    "상추": (
        "오이 또는 양배추",
        "상추 대신 단단한 채소를 쓰면 소스 양을 조금 늘려도 좋아요.",
    ),
    "애호박": (
        "가지 또는 버섯",
        "애호박 대신 수분이 적은 재료를 쓰면 팬에 식용유를 조금 더하세요.",
    ),
    "소시지": (
        "돼지고기 또는 닭고기",
        "소시지 대신 생고기를 쓰면 소금 간을 조금 더하고 속까지 익혀주세요.",
    ),
    "아보카도": (
        "치즈 또는 두부",
        "부드러운 질감은 유지되지만 느끼함이 달라질 수 있어 산미를 더해도 좋아요.",
    ),
    "생강": (
        "마늘 또는 대파",
        "생강 향이 빠지면 잡내 제거가 약해질 수 있어 마늘을 조금 더하세요.",
    ),
}


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.inventory_repository = InventoryRepository(db)
        self.recommendation_repository = RecommendationRepository(db)

    @staticmethod
    def _build_selection_factors(
        *,
        available_count: int,
        missing_count: int,
        rank_hint: int,
        total_required: int,
    ) -> list[str]:
        factors: list[str] = []

        if total_required > 0:
            factors.append(f"핵심 재료 {total_required}개 중 {available_count}개를 지금 냉장고 재료로 바로 활용할 수 있어요.")

        if missing_count == 0:
            factors.append("추가 장보기 없이 바로 만들기 좋은 레시피예요.")
        else:
            factors.append(f"부족한 핵심 재료가 {missing_count}개라 준비 부담이 비교적 적어요.")

        if rank_hint >= 90:
            factors.append("이 주류와의 기본 페어링 점수가 아주 높은 후보예요.")
        elif rank_hint >= 80:
            factors.append("현재 고른 술과 잘 맞는 상위권 페어링 레시피예요.")
        else:
            factors.append("현재 고른 술과 편하게 곁들이기 좋은 보조 후보예요.")

        return factors

    @staticmethod
    def _build_priority_reason(
        *,
        rank: int,
        available_count: int,
        missing_count: int,
        rank_hint: int,
    ) -> str:
        availability_phrase = (
            "현재 재고만으로 바로 만들 수 있고"
            if missing_count == 0
            else f"현재 재고에서 {available_count}개 재료를 활용할 수 있고 부족 재료는 {missing_count}개지만"
        )

        pairing_phrase = (
            "페어링 기본 점수도 높아서"
            if rank_hint >= 85
            else "다른 후보와 비교해 전체 균형이 좋아서"
        )

        return f"{availability_phrase} {pairing_phrase} {rank}순위로 골랐어요."

    @staticmethod
    def _load_json_list(value: str | None) -> list[Any]:
        if not value:
            return []

        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return []

        return loaded if isinstance(loaded, list) else []

    @classmethod
    def _build_pantry_item_details(cls, recipe) -> list[RecommendationPantryItem]:
        details: list[RecommendationPantryItem] = []
        for item in cls._load_json_list(recipe.pantry_item_details_text):
            if not isinstance(item, dict):
                continue
            details.append(
                RecommendationPantryItem(
                    name=str(item.get("name") or ""),
                    amount=float(item.get("amount") or 0),
                    unit=str(item.get("unit") or ""),
                )
            )
        return details

    @classmethod
    def _build_recipe_steps(cls, recipe) -> list[RecommendationRecipeStep]:
        structured_steps: list[RecommendationRecipeStep] = []
        for item in cls._load_json_list(recipe.recipe_steps_text):
            if not isinstance(item, dict):
                continue
            structured_steps.append(
                RecommendationRecipeStep(
                    step_number=int(
                        item.get("step_number") or len(structured_steps) + 1
                    ),
                    title=str(item.get("title") or f"{len(structured_steps) + 1}단계"),
                    instruction=str(item.get("instruction") or ""),
                    time_minutes=int(item.get("time_minutes") or 0),
                    heat_level=str(item.get("heat_level") or "없음"),
                    success_cue=str(item.get("success_cue") or ""),
                )
            )

        if structured_steps:
            return structured_steps

        legacy_steps = [
            step for step in recipe.instructions_text.splitlines() if step.strip()
        ]
        return [
            RecommendationRecipeStep(
                step_number=index,
                title=f"{index}단계",
                instruction=step,
                time_minutes=0,
                heat_level="없음",
                success_cue="설명한 상태가 되면 다음 단계로 넘어가면 좋아요.",
            )
            for index, step in enumerate(legacy_steps, start=1)
        ]

    @staticmethod
    def _build_pairing_knowledge(recipe) -> RecommendationPairingKnowledge:
        return RecommendationPairingKnowledge(
            flavor_logic=recipe.pairing_flavor_logic or recipe.reason,
            ingredient_logic=recipe.pairing_ingredient_logic or "",
            why_this_liquor=recipe.pairing_why_this_liquor or "",
        )

    @classmethod
    def _build_tags(cls, recipe) -> list[str]:
        return [
            str(tag)
            for tag in cls._load_json_list(recipe.tags_text)
            if isinstance(tag, str) and tag.strip()
        ]

    @staticmethod
    def _inventory_signature(inventory_counts: dict[str, int]) -> str:
        return "|".join(
            f"{ingredient_key}:{inventory_counts[ingredient_key]}"
            for ingredient_key in sorted(inventory_counts)
        )

    @staticmethod
    def _build_filter_signature(
        *,
        available_only: bool,
        max_missing_count: int | None,
        max_cook_time_minutes: int | None,
        difficulty: str | None,
    ) -> str:
        return "|".join(
            [
                f"available_only:{available_only}",
                f"max_missing_count:{max_missing_count}",
                f"max_cook_time_minutes:{max_cook_time_minutes}",
                f"difficulty:{difficulty or ''}",
            ]
        )

    @staticmethod
    def _matches_recommendation_filters(
        candidate: dict[str, Any],
        *,
        available_only: bool,
        max_missing_count: int | None,
        max_cook_time_minutes: int | None,
        difficulty: str | None,
    ) -> bool:
        recipe = candidate["recipe"]
        if available_only and candidate["missing_count"] > 0:
            return False
        if (
            max_missing_count is not None
            and candidate["missing_count"] > max_missing_count
        ):
            return False
        if (
            max_cook_time_minutes is not None
            and recipe.cook_time_minutes > max_cook_time_minutes
        ):
            return False
        if difficulty and recipe.difficulty != difficulty:
            return False
        return True

    @staticmethod
    def _build_substitution_tips(
        missing_items: list[str],
    ) -> list[RecommendationSubstitutionTip]:
        tips: list[RecommendationSubstitutionTip] = []
        for missing_item in missing_items:
            suggestion, note = _SUBSTITUTION_TIP_BY_DISPLAY_NAME.get(
                missing_item,
                (
                    "구매 권장",
                    "추천 맛을 가장 안정적으로 내려면 해당 재료를 준비하는 쪽이 좋아요.",
                ),
            )
            tips.append(
                RecommendationSubstitutionTip(
                    missing_ingredient=missing_item,
                    suggestion=suggestion,
                    note=note,
                )
            )
        return tips

    @classmethod
    def _select_ranked_candidates(
        cls,
        ranked_candidates: list[dict[str, Any]],
        *,
        liquor_key: str,
        refresh: bool,
        inventory_counts: dict[str, int],
        filter_signature: str = "",
    ) -> list[dict[str, Any]]:
        if not ranked_candidates:
            return []

        cursor_key = (
            f"{liquor_key}:{cls._inventory_signature(inventory_counts)}:"
            f"{filter_signature}"
        )
        page_size = min(3, len(ranked_candidates))

        if not refresh:
            _RECOMMENDATION_REFRESH_CURSORS[cursor_key] = page_size % len(ranked_candidates)
            return ranked_candidates[:page_size]

        start_index = _RECOMMENDATION_REFRESH_CURSORS.get(cursor_key, page_size)
        selected = [
            ranked_candidates[(start_index + offset) % len(ranked_candidates)]
            for offset in range(page_size)
        ]
        _RECOMMENDATION_REFRESH_CURSORS[cursor_key] = (
            start_index + page_size
        ) % len(ranked_candidates)
        return selected

    def get_recommendations(
        self,
        liquor: str,
        refresh: bool,
        *,
        available_only: bool = False,
        max_missing_count: int | None = None,
        max_cook_time_minutes: int | None = None,
        difficulty: str | None = None,
        llm_fallback: bool = False,
    ) -> RecommendationsResponse:
        normalized = normalize_liquor_key(liquor or "soju") or "soju"
        difficulty_filter = difficulty.strip().lower() if difficulty else None
        inventory_counts: dict[str, int] = {}
        for item in self.inventory_repository.list_inventory_items():
            if item.count <= 0:
                continue
            ingredient_key = normalize_ingredient_key(item.item_name)
            inventory_counts[ingredient_key] = (
                inventory_counts.get(ingredient_key, 0) + item.count
            )
        candidates = self.recommendation_repository.list_recipe_candidates(normalized)
        ranked_candidates: list[dict] = []

        for recipe in candidates:
            required_ingredients = [
                normalize_ingredient_key(ingredient.ingredient_name)
                for ingredient in recipe.ingredients
            ]
            missing_ingredients = [
                ingredient_name
                for ingredient_name in required_ingredients
                if inventory_counts.get(ingredient_name, 0) <= 0
            ]
            available_count = len(required_ingredients) - len(missing_ingredients)
            score = (available_count * 3) - (len(missing_ingredients) * 2) + recipe.rank_hint
            ingredient_details = [
                RecommendationIngredientDetail(
                    item_name=normalize_ingredient_key(ingredient.ingredient_name),
                    display_name=(
                        ingredient.display_name
                        or ingredient_display_name(ingredient.ingredient_name)
                    ),
                    variant_detail=ingredient.variant_detail or "",
                    amount=ingredient.amount,
                    unit=ingredient.unit,
                    status=(
                        "available"
                        if inventory_counts.get(
                            normalize_ingredient_key(ingredient.ingredient_name),
                            0,
                        )
                        > 0
                        else "missing"
                    ),
                )
                for ingredient in recipe.ingredients
            ]
            ingredient_yes = [
                detail.display_name
                for detail in ingredient_details
                if detail.status == "available"
            ]
            ingredient_no = [
                detail.display_name
                for detail in ingredient_details
                if detail.status == "missing"
            ]
            ranked_candidates.append(
                {
                    "score": score,
                    "missing_count": len(missing_ingredients),
                    "rank_hint": recipe.rank_hint,
                    "name": recipe.name,
                    "available_count": available_count,
                    "total_required": len(required_ingredients),
                    "missing_ingredients": missing_ingredients,
                    "ingredient_yes": ingredient_yes,
                    "ingredient_no": ingredient_no,
                    "ingredient_details": ingredient_details,
                    "recipe": recipe,
                }
            )

        ranked_candidates = [
            candidate
            for candidate in ranked_candidates
            if self._matches_recommendation_filters(
                candidate,
                available_only=available_only,
                max_missing_count=max_missing_count,
                max_cook_time_minutes=max_cook_time_minutes,
                difficulty=difficulty_filter,
            )
        ]
        ranked_candidates.sort(
            key=lambda candidate: (
                -candidate["score"],
                candidate["missing_count"],
                -candidate["rank_hint"],
                candidate["name"],
            )
        )
        selected_candidates = self._select_ranked_candidates(
            ranked_candidates,
            liquor_key=normalized,
            refresh=refresh,
            inventory_counts=inventory_counts,
            filter_signature=self._build_filter_signature(
                available_only=available_only,
                max_missing_count=max_missing_count,
                max_cook_time_minutes=max_cook_time_minutes,
                difficulty=difficulty_filter,
            ),
        )

        recommendations: list[RecommendationItem] = []
        for index, candidate in enumerate(selected_candidates, start=1):
            recipe = candidate["recipe"]
            recommendations.append(
                RecommendationItem(
                    name=recipe.name,
                    reason=recipe.reason,
                    recommendation_source="seed",
                    priority_rank=index,
                    priority_reason=self._build_priority_reason(
                        rank=index,
                        available_count=candidate["available_count"],
                        missing_count=candidate["missing_count"],
                        rank_hint=candidate["rank_hint"],
                    ),
                    selection_factors=self._build_selection_factors(
                        available_count=candidate["available_count"],
                        missing_count=candidate["missing_count"],
                        rank_hint=candidate["rank_hint"],
                        total_required=candidate["total_required"],
                    ),
                    score_breakdown=RecommendationScoreBreakdown(
                        available_ingredient_count=candidate["available_count"],
                        missing_ingredient_count=candidate["missing_count"],
                        rank_hint=candidate["rank_hint"],
                        total_score=candidate["score"],
                    ),
                    servings=recipe.servings,
                    cook_time_minutes=recipe.cook_time_minutes,
                    difficulty=recipe.difficulty,
                    pairing_knowledge=self._build_pairing_knowledge(recipe),
                    ingredient_yes=candidate["ingredient_yes"],
                    ingredient_no=candidate["ingredient_no"],
                    ingredient_details=candidate["ingredient_details"],
                    pantry_items=[
                        item for item in recipe.pantry_items_text.splitlines() if item.strip()
                    ],
                    pantry_item_details=self._build_pantry_item_details(recipe),
                    shopping_items=candidate["ingredient_no"],
                    substitution_tips=self._build_substitution_tips(
                        candidate["ingredient_no"]
                    ),
                    recipe=[step for step in recipe.instructions_text.splitlines() if step],
                    recipe_steps=self._build_recipe_steps(recipe),
                    missing_ingredients=candidate["ingredient_no"],
                    tip=recipe.tip,
                    tags=self._build_tags(recipe),
                )
            )

        if llm_fallback and len(recommendations) < 3:
            generated_recommendations = GeminiRecommendationService(
                self.settings
            ).generate_fallback_recommendations(
                liquor_key=normalized,
                inventory_counts=inventory_counts,
                needed_count=3 - len(recommendations),
                start_rank=len(recommendations) + 1,
                existing_names=[recipe.name for recipe in candidates],
                selected_names=[item.name for item in recommendations],
                available_only=available_only,
                max_missing_count=max_missing_count,
                max_cook_time_minutes=max_cook_time_minutes,
                difficulty=difficulty_filter,
            )
            recommendations.extend(generated_recommendations)

        if self.settings.recommendation_response_delay_seconds > 0:
            time.sleep(self.settings.recommendation_response_delay_seconds)

        return RecommendationsResponse(
            liquor=liquor_display_name(normalized),
            recommendations=recommendations,
        )

    def refresh_with_keep(
        self, payload: RecommendationRefreshRequest
    ) -> RecommendationRefreshResponse:
        normalized = normalize_liquor_key(payload.liquor or "soju") or "soju"
        kept = payload.keep_recommendations[:3]
        kept_names = {
            str(item.get("name"))
            for item in kept
            if isinstance(item, dict) and item.get("name")
        }
        needed_count = min(payload.refresh_count, max(3 - len(kept), 0))
        fresh_items: list[dict[str, Any]] = []

        for attempt in range(10):
            if len(fresh_items) >= needed_count:
                break

            response = self.get_recommendations(
                normalized,
                refresh=True,
                llm_fallback=payload.llm_fallback,
            )
            for recommendation in response.recommendations:
                item = recommendation.model_dump(mode="json")
                name = str(item.get("name") or "")
                if not name or name in kept_names:
                    continue
                if any(existing.get("name") == name for existing in fresh_items):
                    continue

                fresh_items.append(item)
                if len(fresh_items) >= needed_count:
                    break

            if attempt >= 2 and not fresh_items:
                break

        combined = kept + fresh_items
        if len(combined) < 3:
            response = self.get_recommendations(
                normalized,
                refresh=True,
                llm_fallback=payload.llm_fallback,
            )
            for recommendation in response.recommendations:
                item = recommendation.model_dump(mode="json")
                name = str(item.get("name") or "")
                if name in kept_names:
                    continue
                if any(existing.get("name") == name for existing in combined):
                    continue
                combined.append(item)
                if len(combined) >= 3:
                    break

        return RecommendationRefreshResponse(
            liquor=liquor_display_name(normalized),
            recommendations=combined[:3],
        )
