from __future__ import annotations

import json
import time
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.domain.models import InventoryItem
from app.repositories.inventory_repository import InventoryRepository
from app.seeds.recommendation_seed import seed_recommendation_data
from app.schemas.inventory import InventoryBulkCreate
from app.schemas.recommendation import RecommendationsResponse
from app.services.inventory_service import InventoryService
from app.services.name_mapping import (
    ingredient_display_name,
    liquor_display_name,
    normalize_ingredient_key,
    normalize_liquor_key,
)
from app.services.recommendation_service import RecommendationService


ROOT_DIR = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT_DIR / "seeds" / "recommendations.json"
POLICY_PATH = ROOT_DIR / "docs" / "recommendation_policy.md"
README_PATH = ROOT_DIR / "README.md"
EVENT_ROUTE_PATH = ROOT_DIR / "app" / "api" / "routes" / "events.py"

ALLOWED_INGREDIENT_KEYS = {
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

EXPECTED_LIQUOR_COUNTS = {
    "soju": 30,
    "beer": 30,
    "red_wine": 30,
    "white_wine": 30,
    "sparkling_wine": 30,
    "whisky": 30,
    "sake": 30,
}

LIQUOR_DISPLAY_NAMES = {
    "soju": "소주",
    "beer": "맥주",
    "red_wine": "레드와인",
    "white_wine": "화이트와인",
    "sparkling_wine": "스파클링와인",
    "whisky": "위스키",
    "sake": "사케",
}

HEAT_LEVELS = {"없음", "약불", "중불", "중강불", "센 불"}
DIFFICULTIES = {"easy", "medium", "hard"}

FORBIDDEN_UNDETECTED_STYLE_TERMS = {
    "카베르네",
    "카베르네 소비뇽",
    "피노 누아",
    "쉬라즈",
    "메를로",
    "산지오베제",
    "키안티",
    "치안티",
    "말벡",
    "소비뇽 블랑",
    "샤르도네",
    "리슬링",
    "피노 그리지오",
    "샴페인",
    "프로세코",
    "카바",
    "스파클링 로제",
    "브뤼",
    "버번",
    "싱글몰트",
    "블렌디드",
    "피트 위스키",
    "셰리 캐스크",
    "하이볼",
    "준마이",
    "긴조",
    "다이긴조",
    "니고리",
}

FORBIDDEN_BAD_PHRASES = {
    "레드와인는",
    "화이트와인는",
    "스파클링와인는",
    "소고기은",
    "돼지고기은",
    "닭고기은",
    "집안주예요",
    "포인트를 살린",
    "포인트가 살아",
    "포인트 포인트",
}

FORBIDDEN_GENERIC_PHRASES = {
    "주재료",
    "나머지 재료",
    "준비한 재료",
    "향이 나는 재료",
}


def load_seed_payload() -> dict:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def flatten_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        flattened: list[str] = []
        for item in value:
            flattened.extend(flatten_strings(item))
        return flattened
    if isinstance(value, dict):
        flattened: list[str] = []
        for item in value.values():
            flattened.extend(flatten_strings(item))
        return flattened
    return []


def assert_display_safe(test_case: unittest.TestCase, visible_payload) -> None:
    visible_text = " ".join(flatten_strings(visible_payload))
    for term in FORBIDDEN_UNDETECTED_STYLE_TERMS:
        test_case.assertNotIn(term, visible_text)
    for phrase in FORBIDDEN_BAD_PHRASES | FORBIDDEN_GENERIC_PHRASES:
        test_case.assertNotIn(phrase, visible_text)


def make_test_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return engine, testing_session()


class SeedQualityGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = load_seed_payload()
        cls.recipes = cls.payload["recipes"]
        cls.seed_text = SEED_PATH.read_text(encoding="utf-8")

    def test_seed_has_expected_liquor_counts(self) -> None:
        counts = Counter(recipe["liquor_name"] for recipe in self.recipes)
        self.assertEqual(EXPECTED_LIQUOR_COUNTS, dict(counts))
        self.assertEqual(sum(EXPECTED_LIQUOR_COUNTS.values()), len(self.recipes))

    def test_seed_has_no_user_visible_unrecognized_style_terms(self) -> None:
        found = [
            term
            for term in sorted(FORBIDDEN_UNDETECTED_STYLE_TERMS)
            if term in self.seed_text
        ]
        self.assertEqual([], found)

    def test_seed_has_no_bad_or_template_phrases(self) -> None:
        forbidden = FORBIDDEN_BAD_PHRASES | FORBIDDEN_GENERIC_PHRASES
        found = [term for term in sorted(forbidden) if term in self.seed_text]
        self.assertEqual([], found)

    def test_recipe_names_are_unique_per_liquor(self) -> None:
        names_by_liquor: dict[str, list[str]] = defaultdict(list)
        for recipe in self.recipes:
            names_by_liquor[recipe["liquor_name"]].append(recipe["name"])

        for liquor_name, names in names_by_liquor.items():
            with self.subTest(liquor_name=liquor_name):
                self.assertEqual(len(names), len(set(names)))

    def test_recipe_schema_and_content_constraints(self) -> None:
        for recipe in self.recipes:
            with self.subTest(recipe=recipe["name"]):
                self.assertIn(recipe["refresh_group"], {0, 1})
                self.assertGreaterEqual(recipe["rank_hint"], 60)
                self.assertLessEqual(recipe["rank_hint"], 100)
                self.assertIn(recipe["difficulty"], DIFFICULTIES)
                self.assertGreaterEqual(len(recipe["ingredient_details"]), 3)
                self.assertGreaterEqual(len(recipe["pantry_items"]), 2)
                self.assertGreaterEqual(len(recipe["recipe_steps"]), 4)
                self.assertTrue(recipe["reason"].endswith("요."))
                self.assertTrue(recipe["tip"].endswith("요."))

                for detail in recipe["ingredient_details"]:
                    self.assertIn(detail["item_name"], ALLOWED_INGREDIENT_KEYS)
                    self.assertTrue(detail["display_name"])
                    self.assertTrue(detail["unit"])
                    if detail["item_name"] in {"fish", "mushroom", "cheese"}:
                        self.assertTrue(detail["variant_detail"])

                for step_number, step in enumerate(recipe["recipe_steps"], start=1):
                    self.assertEqual(step_number, step["step_number"])
                    self.assertTrue(step["title"])
                    self.assertTrue(step["instruction"])
                    self.assertIsInstance(step["time_minutes"], int)
                    self.assertGreaterEqual(step["time_minutes"], 0)
                    self.assertIn(step["heat_level"], HEAT_LEVELS)
                    self.assertTrue(step["success_cue"])


class MappingQualityGateTest(unittest.TestCase):
    def test_ingredient_mapping_accepts_korean_and_internal_keys(self) -> None:
        self.assertEqual("green_onion", normalize_ingredient_key("대파"))
        self.assertEqual("green_onion", normalize_ingredient_key("green_onion"))
        self.assertEqual("pepper", normalize_ingredient_key("파프리카"))
        self.assertEqual("대파", ingredient_display_name("green_onion"))
        self.assertEqual("파프리카", ingredient_display_name("pepper"))

    def test_liquor_mapping_accepts_korean_and_internal_keys(self) -> None:
        self.assertEqual("red_wine", normalize_liquor_key("레드와인"))
        self.assertEqual("red_wine", normalize_liquor_key("red_wine"))
        self.assertEqual("sparkling_wine", normalize_liquor_key("스파클링와인"))
        self.assertEqual("스파클링와인", liquor_display_name("sparkling_wine"))


class PolicyDocumentationQualityGateTest(unittest.TestCase):
    def test_recommendation_policy_documents_seed_and_scoring_rules(self) -> None:
        policy_text = POLICY_PATH.read_text(encoding="utf-8")

        required_terms = [
            "추천 seed 선정 및 점수 정책",
            "실시간 LLM 생성 방식이 아닙니다",
            "검수된 레시피 풀",
            "total_score = available_ingredient_count * 3",
            "- missing_ingredient_count * 2",
            "+ rank_hint",
            "refresh_group=0",
            "refresh_group=1",
            "missing_ingredients",
            "품질 게이트 테스트",
        ]

        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, policy_text)


class SwaggerDocumentationQualityGateTest(unittest.TestCase):
    def test_recommendation_response_schema_has_realistic_example(self) -> None:
        schema = RecommendationsResponse.model_json_schema()
        example = schema.get("example")

        self.assertIsInstance(example, dict)
        self.assertEqual("소주", example["liquor"])
        self.assertEqual(1, len(example["recommendations"]))

        first = example["recommendations"][0]
        self.assertEqual(["돼지고기"], first["missing_ingredients"])
        self.assertIn("recipe_steps", first)
        self.assertIn("pairing_knowledge", first)
        self.assertIn("score_breakdown", first)

        first_ingredient = first["ingredient_details"][0]
        self.assertEqual("pork", first_ingredient["item_name"])
        self.assertEqual("돼지고기", first_ingredient["display_name"])

        example_text = json.dumps(example, ensure_ascii=False)
        self.assertNotIn('"liquor": "soju"', example_text)
        self.assertNotIn('"missing_ingredients": ["pork"', example_text)

    def test_readme_recommendation_example_uses_display_values(self) -> None:
        readme_text = README_PATH.read_text(encoding="utf-8")

        self.assertIn('"liquor": "소주"', readme_text)
        self.assertIn('"missing_ingredients": ["돼지고기", "마늘"]', readme_text)
        self.assertNotIn('"liquor": "soju"', readme_text)
        self.assertNotIn('"missing_ingredients": ["pork", "garlic"]', readme_text)

    def test_recommendation_stream_docs_do_not_claim_fixed_delay(self) -> None:
        events_route_text = EVENT_ROUTE_PATH.read_text(encoding="utf-8")

        self.assertNotIn("약간의 지연 후 생성된 추천 결과", events_route_text)


class ServiceQualityGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine, self.db = make_test_session()
        seed_recommendation_data(self.db)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_inventory_groups_legacy_korean_and_internal_keys(self) -> None:
        self.db.add_all(
            [
                InventoryItem(item_name="대파", count=2),
                InventoryItem(item_name="green_onion", count=3),
                InventoryItem(item_name="양파", count=1),
            ]
        )
        self.db.commit()

        service = InventoryService(self.db, InventoryRepository(self.db))
        response = service.list_inventory()
        quantities = {item.ingredient_name: item.quantity for item in response.data}

        self.assertEqual("success", response.status)
        self.assertEqual(5, quantities["대파"])
        self.assertEqual(1, quantities["양파"])

    def test_inventory_bulk_save_accepts_korean_and_internal_keys(self) -> None:
        service = InventoryService(self.db, InventoryRepository(self.db))
        response = service.bulk_save_inventory(
            InventoryBulkCreate(items=["대파", "green_onion", "양파"])
        )
        quantities = {
            item.ingredient_name: item.quantity
            for item in service.list_inventory().data
        }

        self.assertEqual("success", response.status)
        self.assertEqual("보관함에 저장되었습니다.", response.message)
        self.assertEqual(3, response.saved_count)
        self.assertEqual(2, quantities["대파"])
        self.assertEqual(1, quantities["양파"])

    def test_recommendation_accepts_korean_liquor_and_returns_display_safe_text(self) -> None:
        response = RecommendationService(self.db).get_recommendations("레드와인", False)

        self.assertEqual("레드와인", response.liquor)
        self.assertEqual(3, len(response.recommendations))

        assert_display_safe(self, response.model_dump())

        first = response.recommendations[0]
        self.assertFalse(any("_" in item for item in first.missing_ingredients))
        self.assertTrue(all(detail.display_name for detail in first.ingredient_details))
        self.assertTrue(all(step.title for step in first.recipe_steps))
        self.assertIn("레드와인", first.tags)

    def test_recommendation_default_response_has_no_artificial_delay(self) -> None:
        started_at = time.perf_counter()
        response = RecommendationService(self.db).get_recommendations("레드와인", False)
        elapsed_seconds = time.perf_counter() - started_at

        self.assertEqual(3, len(response.recommendations))
        self.assertLess(elapsed_seconds, 1.0)

    def test_all_liquor_recommendation_responses_are_display_safe(self) -> None:
        service = RecommendationService(self.db)

        for liquor_key, display_name in LIQUOR_DISPLAY_NAMES.items():
            for refresh in (False, True):
                with self.subTest(liquor=liquor_key, refresh=refresh):
                    response = service.get_recommendations(display_name, refresh)
                    self.assertEqual(display_name, response.liquor)
                    self.assertEqual(3, len(response.recommendations))
                    assert_display_safe(self, response.model_dump())


if __name__ == "__main__":
    unittest.main()
