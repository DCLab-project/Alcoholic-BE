from __future__ import annotations

import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.config.settings import Settings, get_settings
from app.schemas.recommendation import (
    RecommendationIngredientDetail,
    RecommendationItem,
    RecommendationPairingKnowledge,
    RecommendationPantryItem,
    RecommendationRecipeStep,
    RecommendationScoreBreakdown,
    RecommendationSubstitutionTip,
)
from app.services.name_mapping import (
    INGREDIENT_DISPLAY_NAMES,
    ingredient_display_name,
    liquor_display_name,
    normalize_ingredient_key,
)


ALLOWED_INGREDIENT_KEYS = set(INGREDIENT_DISPLAY_NAMES)
_FORBIDDEN_EXTRA_PATTERN = re.compile(r"외\s*\d+\s*가지")
_VALID_DIFFICULTIES = {"easy", "medium", "hard"}
_VALID_HEAT_LEVELS = {"없음", "약불", "중약불", "중불", "중강불", "강불"}


class GeminiIngredient(BaseModel):
    item_name: str = Field(description="One of the allowed ingredient keys.")
    variant_detail: str = Field(description="Concrete ingredient cut or type.")
    amount: float = Field(gt=0, description="Required amount for 1-2 servings.")
    unit: str = Field(min_length=1, description="Korean unit, such as g, 개, 쪽, 대.")


class GeminiPantryItem(BaseModel):
    name: str = Field(description="Basic pantry item name.")
    amount: float = Field(gt=0)
    unit: str = Field(min_length=1)


class GeminiRecipeStep(BaseModel):
    step_number: int = Field(ge=1, le=9)
    title: str = Field(min_length=1)
    instruction: str = Field(min_length=12)
    time_minutes: int = Field(ge=0, le=60)
    heat_level: str = Field(description="없음, 약불, 중약불, 중불, 중강불, 강불 중 하나")
    success_cue: str = Field(min_length=8)


class GeminiPairingKnowledge(BaseModel):
    flavor_logic: str = Field(min_length=10)
    ingredient_logic: str = Field(min_length=10)
    why_this_liquor: str = Field(min_length=10)


class GeminiRecipeCandidate(BaseModel):
    name: str = Field(min_length=2, max_length=40)
    reason: str = Field(min_length=10, max_length=180)
    servings: int = Field(ge=1, le=2)
    cook_time_minutes: int = Field(ge=5, le=60)
    difficulty: str = Field(description="easy, medium, hard 중 하나")
    pairing_knowledge: GeminiPairingKnowledge
    ingredient_details: list[GeminiIngredient] = Field(min_length=1, max_length=6)
    pantry_items: list[GeminiPantryItem] = Field(min_length=1, max_length=8)
    recipe_steps: list[GeminiRecipeStep] = Field(min_length=6, max_length=9)
    tip: str = Field(min_length=8, max_length=180)
    tags: list[str] = Field(min_length=2, max_length=8)

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in _VALID_DIFFICULTIES:
            raise ValueError("difficulty must be easy, medium, or hard")
        return normalized


class GeminiRecommendationBatch(BaseModel):
    recommendations: list[GeminiRecipeCandidate] = Field(min_length=0, max_length=3)


class GeminiRecommendationService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.api_key = self.settings.gemini_api_key.strip()
        self.model = self.settings.gemini_model.strip() or "gemini-2.5-flash-lite"
        self.timeout_seconds = self.settings.gemini_timeout_seconds

    def generate_fallback_recommendations(
        self,
        *,
        liquor_key: str,
        inventory_counts: dict[str, int],
        needed_count: int,
        start_rank: int,
        existing_names: list[str],
        selected_names: list[str],
        available_only: bool,
        max_missing_count: int | None,
        max_cook_time_minutes: int | None,
        difficulty: str | None,
    ) -> list[RecommendationItem]:
        if not self.api_key or needed_count <= 0:
            return []

        recommendations: list[RecommendationItem] = []
        blocked_names = {
            self._name_signature(name)
            for name in [*existing_names, *selected_names]
            if name
        }

        for attempt in range(2):
            prompt = self._build_prompt(
                liquor_key=liquor_key,
                inventory_counts=inventory_counts,
                needed_count=needed_count - len(recommendations),
                existing_names=existing_names,
                selected_names=[*selected_names, *[item.name for item in recommendations]],
                available_only=available_only,
                max_missing_count=max_missing_count,
                max_cook_time_minutes=max_cook_time_minutes,
                difficulty=difficulty,
                retry=attempt > 0,
            )
            raw_payload = self._call_gemini(prompt)
            if not raw_payload:
                continue

            try:
                parsed = GeminiRecommendationBatch.model_validate(raw_payload)
            except ValidationError:
                continue

            for candidate in parsed.recommendations:
                if len(recommendations) >= needed_count:
                    break
                if self._name_signature(candidate.name) in blocked_names:
                    continue
                item = self._candidate_to_recommendation(
                    candidate,
                    liquor_key=liquor_key,
                    inventory_counts=inventory_counts,
                    rank=start_rank + len(recommendations),
                    available_only=available_only,
                    max_missing_count=max_missing_count,
                    max_cook_time_minutes=max_cook_time_minutes,
                    difficulty=difficulty,
                )
                if item is None:
                    continue
                blocked_names.add(self._name_signature(item.name))
                recommendations.append(item)

            if len(recommendations) >= needed_count:
                break

        return recommendations

    def _call_gemini(self, prompt: str) -> dict[str, Any] | None:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.35,
                "topP": 0.9,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json",
                "responseJsonSchema": self._response_schema(),
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    url,
                    headers={
                        "x-goog-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                response_payload = response.json()
        except (httpx.HTTPError, ValueError):
            return None

        text = self._extract_response_text(response_payload)
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _response_schema() -> dict[str, Any]:
        string_array = {"type": "array", "items": {"type": "string"}}
        ingredient_key = {
            "type": "string",
            "enum": sorted(ALLOWED_INGREDIENT_KEYS),
        }
        heat_level = {
            "type": "string",
            "enum": sorted(_VALID_HEAT_LEVELS),
        }
        return {
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "reason": {"type": "string"},
                            "servings": {"type": "integer"},
                            "cook_time_minutes": {"type": "integer"},
                            "difficulty": {"type": "string"},
                            "pairing_knowledge": {
                                "type": "object",
                                "properties": {
                                    "flavor_logic": {"type": "string"},
                                    "ingredient_logic": {"type": "string"},
                                    "why_this_liquor": {"type": "string"},
                                },
                                "required": [
                                    "flavor_logic",
                                    "ingredient_logic",
                                    "why_this_liquor",
                                ],
                            },
                            "ingredient_details": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item_name": ingredient_key,
                                        "variant_detail": {"type": "string"},
                                        "amount": {"type": "number"},
                                        "unit": {"type": "string"},
                                    },
                                    "required": [
                                        "item_name",
                                        "variant_detail",
                                        "amount",
                                        "unit",
                                    ],
                                },
                            },
                            "pantry_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "amount": {"type": "number"},
                                        "unit": {"type": "string"},
                                    },
                                    "required": ["name", "amount", "unit"],
                                },
                            },
                            "recipe_steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "step_number": {"type": "integer"},
                                        "title": {"type": "string"},
                                        "instruction": {"type": "string"},
                                        "time_minutes": {"type": "integer"},
                                        "heat_level": heat_level,
                                        "success_cue": {"type": "string"},
                                    },
                                    "required": [
                                        "step_number",
                                        "title",
                                        "instruction",
                                        "time_minutes",
                                        "heat_level",
                                        "success_cue",
                                    ],
                                },
                            },
                            "tip": {"type": "string"},
                            "tags": string_array,
                        },
                        "required": [
                            "name",
                            "reason",
                            "servings",
                            "cook_time_minutes",
                            "difficulty",
                            "pairing_knowledge",
                            "ingredient_details",
                            "pantry_items",
                            "recipe_steps",
                            "tip",
                            "tags",
                        ],
                    },
                }
            },
            "required": ["recommendations"],
        }

    @staticmethod
    def _extract_response_text(response_payload: dict[str, Any]) -> str:
        candidates = response_payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return ""
        content = candidates[0].get("content") if isinstance(candidates[0], dict) else None
        parts = content.get("parts") if isinstance(content, dict) else None
        if not isinstance(parts, list) or not parts:
            return ""
        text = parts[0].get("text") if isinstance(parts[0], dict) else ""
        return text if isinstance(text, str) else ""

    def _build_prompt(
        self,
        *,
        liquor_key: str,
        inventory_counts: dict[str, int],
        needed_count: int,
        existing_names: list[str],
        selected_names: list[str],
        available_only: bool,
        max_missing_count: int | None,
        max_cook_time_minutes: int | None,
        difficulty: str | None,
        retry: bool = False,
    ) -> str:
        fridge_keys = sorted(key for key, count in inventory_counts.items() if count > 0)
        fridge_key_text = ", ".join(fridge_keys) if fridge_keys else "none"
        inventory_lines = [
            f"- {key} ({ingredient_display_name(key)}): {count}"
            for key, count in sorted(inventory_counts.items())
            if count > 0
        ]
        inventory_text = "\n".join(inventory_lines) if inventory_lines else "- 없음"
        allowed_key_text = ", ".join(sorted(ALLOWED_INGREDIENT_KEYS))
        blocked_name_text = ", ".join(existing_names[:120])
        selected_name_text = ", ".join(selected_names)
        filter_text = [
            f"available_only={available_only}",
            f"max_missing_count={max_missing_count}",
            f"max_cook_time_minutes={max_cook_time_minutes}",
            f"difficulty={difficulty or 'any'}",
        ]
        strict_filter_lines: list[str] = []
        if available_only:
            strict_filter_lines.append(
                f"- available_only is true, so ingredient_details[].item_name MUST be only these fridge keys: {fridge_key_text}. Do not add any other core ingredient."
            )
        if max_missing_count is not None:
            strict_filter_lines.append(
                f"- missing core ingredient count MUST be <= {max_missing_count} after comparing with fridge keys: {fridge_key_text}."
            )
        if max_cook_time_minutes is not None:
            strict_filter_lines.append(
                f"- cook_time_minutes MUST be <= {max_cook_time_minutes}."
            )
        if difficulty:
            strict_filter_lines.append(
                f"- difficulty MUST be exactly \"{difficulty}\"."
            )
        strict_filter_text = "\n".join(strict_filter_lines) if strict_filter_lines else "- No extra strict filters."
        retry_text = (
            "\nPrevious output did not pass backend validation. Retry with stricter compliance to every filter and schema field."
            if retry
            else ""
        )

        return f"""
You are a senior Korean home-cooking alcohol pairing recipe editor.
Generate {needed_count} Korean snack recipe recommendation(s) for a 1-2 person AI fridge service.

Liquor:
- key: {liquor_key}
- display: {liquor_display_name(liquor_key)}

Current fridge inventory:
{inventory_text}

Allowed core ingredient keys:
{allowed_key_text}

Important ingredient rules:
- Use only allowed core ingredient keys in ingredient_details[].item_name.
- pepper means paprika, not chili pepper.
- leek means Korean 대파. Do not use green_onion in new output.
- fish means general fish fillet; salmon means salmon.
- Pantry items may include common seasoning/oil/salt/sugar/soy sauce/vinegar/pepper powder in pantry_items only.
- Do not put pantry items in ingredient_details.
- Never put salt, soy sauce, sugar, vinegar, cooking oil, black pepper powder, gochugaru, gochujang, doenjang, or oyster sauce in ingredient_details.

Avoid these existing or already shown recipe names:
{blocked_name_text}
{selected_name_text}

Filters:
{"; ".join(filter_text)}

Strict filter requirements:
{strict_filter_text}

Quality rules:
- Return realistic Korean home-cooking snacks, not artificial names.
- Do not create near-duplicate names or method flows from the blocked names.
- Each recipe must have 6-9 recipe_steps.
- Each step must include concrete quantity, time_minutes, heat_level, and success_cue.
- No "외 N가지" wording.
- The recipe name must match the actual cooking method and ingredients.
- If available_only is true, use only fridge ingredients as core ingredients.
- If max_missing_count is set, missing core ingredients must not exceed it.
- Difficulty should be easy unless the filter explicitly requests another value.
- Write all user-facing text in Korean.
- pantry_items[].name and pantry_items[].unit must be Korean user-facing words, such as 식용유/간장/후추 and 큰술/작은술.
- heat_level must be Korean only: 없음, 약불, 중약불, 중불, 중강불, 강불.
{retry_text}
""".strip()

    def _candidate_to_recommendation(
        self,
        candidate: GeminiRecipeCandidate,
        *,
        liquor_key: str,
        inventory_counts: dict[str, int],
        rank: int,
        available_only: bool,
        max_missing_count: int | None,
        max_cook_time_minutes: int | None,
        difficulty: str | None,
    ) -> RecommendationItem | None:
        if self._contains_forbidden_extra_text(candidate):
            return None
        if max_cook_time_minutes is not None and candidate.cook_time_minutes > max_cook_time_minutes:
            return None
        if difficulty and candidate.difficulty != difficulty:
            return None

        recipe_steps = sorted(candidate.recipe_steps, key=lambda step: step.step_number)
        if not 6 <= len(recipe_steps) <= 9:
            return None
        if any(step.heat_level not in _VALID_HEAT_LEVELS for step in recipe_steps):
            return None

        ingredient_details: list[RecommendationIngredientDetail] = []
        seen_keys: set[str] = set()
        for ingredient in candidate.ingredient_details:
            key = normalize_ingredient_key(ingredient.item_name)
            if key not in ALLOWED_INGREDIENT_KEYS or key in seen_keys:
                return None
            seen_keys.add(key)
            status = "available" if inventory_counts.get(key, 0) > 0 else "missing"
            ingredient_details.append(
                RecommendationIngredientDetail(
                    item_name=key,
                    display_name=ingredient_display_name(key),
                    variant_detail=ingredient.variant_detail,
                    amount=ingredient.amount,
                    unit=ingredient.unit,
                    status=status,
                )
            )

        ingredient_yes = [
            detail.display_name for detail in ingredient_details if detail.status == "available"
        ]
        ingredient_no = [
            detail.display_name for detail in ingredient_details if detail.status == "missing"
        ]
        if available_only and ingredient_no:
            return None
        if max_missing_count is not None and len(ingredient_no) > max_missing_count:
            return None

        recipe_step_items = [
            RecommendationRecipeStep(
                step_number=index,
                title=step.title,
                instruction=step.instruction,
                time_minutes=step.time_minutes,
                heat_level=step.heat_level,
                success_cue=step.success_cue,
            )
            for index, step in enumerate(recipe_steps, start=1)
        ]
        recipe_text = [
            f"{step.step_number}. {step.title}: {step.instruction}"
            for step in recipe_step_items
        ]
        pantry_item_details = [
            RecommendationPantryItem(
                name=item.name,
                amount=item.amount,
                unit=item.unit,
            )
            for item in candidate.pantry_items
        ]
        pantry_items = [
            f"{item.name} {item.amount:g}{item.unit}" for item in pantry_item_details
        ]
        score = (len(ingredient_yes) * 3) - (len(ingredient_no) * 2) + 70

        return RecommendationItem(
            name=candidate.name,
            reason=candidate.reason,
            recommendation_source="llm_fallback",
            priority_rank=rank,
            priority_reason=(
                "기존 seed 후보가 부족해 현재 냉장고 재료와 주류 페어링 조건에 맞춰 "
                "실시간으로 보완한 추천입니다."
            ),
            selection_factors=[
                f"핵심 재료 {len(ingredient_details)}개 중 {len(ingredient_yes)}개를 냉장고에서 활용할 수 있어요.",
                f"부족한 핵심 재료는 {len(ingredient_no)}개예요.",
                "BE가 응답 형식과 재료 상태를 다시 검증한 추천이에요.",
            ],
            score_breakdown=RecommendationScoreBreakdown(
                available_ingredient_count=len(ingredient_yes),
                missing_ingredient_count=len(ingredient_no),
                rank_hint=70,
                total_score=score,
            ),
            servings=candidate.servings,
            cook_time_minutes=candidate.cook_time_minutes,
            difficulty=candidate.difficulty,
            pairing_knowledge=RecommendationPairingKnowledge(
                flavor_logic=candidate.pairing_knowledge.flavor_logic,
                ingredient_logic=candidate.pairing_knowledge.ingredient_logic,
                why_this_liquor=candidate.pairing_knowledge.why_this_liquor,
            ),
            ingredient_yes=ingredient_yes,
            ingredient_no=ingredient_no,
            ingredient_details=ingredient_details,
            pantry_items=pantry_items,
            pantry_item_details=pantry_item_details,
            shopping_items=ingredient_no,
            substitution_tips=[
                RecommendationSubstitutionTip(
                    missing_ingredient=missing_item,
                    suggestion="구매 권장",
                    note="이 재료가 있으면 추천된 맛과 식감에 가장 가깝게 만들 수 있어요.",
                )
                for missing_item in ingredient_no
            ],
            recipe=recipe_text,
            recipe_steps=recipe_step_items,
            missing_ingredients=ingredient_no,
            tip=candidate.tip,
            tags=candidate.tags,
        )

    @staticmethod
    def _contains_forbidden_extra_text(candidate: GeminiRecipeCandidate) -> bool:
        payload = candidate.model_dump(mode="json")
        text = json.dumps(payload, ensure_ascii=False)
        return bool(_FORBIDDEN_EXTRA_PATTERN.search(text))

    @staticmethod
    def _name_signature(name: str) -> str:
        return re.sub(r"\s+", "", name.strip().lower())
