from __future__ import annotations

import json
import re
import time
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from pydantic import ValidationError
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
from app.services.recognition_service import MOCK_LIQUOR_SCAN_CANDIDATES
from app.services.recommendation_service import RecommendationService


ROOT_DIR = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT_DIR / "seeds" / "recommendations.json"
POLICY_PATH = ROOT_DIR / "docs" / "recommendation_policy.md"
README_PATH = ROOT_DIR / "README.md"
EVENT_ROUTE_PATH = ROOT_DIR / "app" / "api" / "routes" / "events.py"
OPERATIONS_READINESS_PATH = ROOT_DIR / "docs" / "operations_readiness.md"
DB_INIT_SCRIPT_PATH = ROOT_DIR / "scripts" / "initialize_database.py"
FE_API_CONTRACT_PATH = ROOT_DIR / "docs" / "api_contract_fe.md"
AI_API_CONTRACT_PATH = ROOT_DIR / "docs" / "api_contract_ai.md"
API_CHANGE_WORKFLOW_PATH = ROOT_DIR / "docs" / "api_change_workflow.md"

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
    "먹기 좋은 크기",
    "양념 재료",
    "준비한 양념",
    "단단한 재료",
    "부드러운 재료",
    "향을 낼 채소",
    "기름이나 버터",
    "재료가 속까지 익도록",
    "설명한 상태",
    "채소나 버섯",
    "나머지 채소",
    "두꺼운 채소",
}

FORBIDDEN_BAD_GRAMMAR_PHRASES = {
    "소고기을",
    "돼지고기을",
    "닭고기을",
    "흰살생선을 겹치지",
    "가지을",
    "감자을",
    "오이은",
    "상추은",
    "토마토은",
    "방울토마토은",
    "양파은",
    "마늘이 있으면",
}

BROAD_KEY_UNSAFE_TERMS = {
    "fish": {"흰살생선", "흰살", "대구", "대구살", "동태", "연어", "도미", "광어"},
    "pork": {"목살", "삼겹살", "앞다리살", "대패", "돼지안심"},
    "chicken": {"닭다리살", "닭가슴살", "닭안심"},
    "mushroom": {"팽이버섯", "느타리", "양송이", "표고"},
    "cheese": {"체다", "모짜렐라", "파마산", "리코타", "크림치즈"},
}

FORBIDDEN_OPAQUE_INGREDIENT_COUNT_PATTERN = re.compile(r"외 \d+가지")

FORBIDDEN_PLACEHOLDER_STEP_TITLES = {
    "나머지 손질",
    "잠깐 식히기",
}

METHOD_NAME_RULES = {
    "호일구이": {"호일"},
    "에어프라이어": {"에어프라이어"},
    "팬구이": {"팬"},
    "꼬치": {"꼬치"},
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
        forbidden = (
            FORBIDDEN_BAD_PHRASES
            | FORBIDDEN_GENERIC_PHRASES
            | FORBIDDEN_BAD_GRAMMAR_PHRASES
        )
        found = [term for term in sorted(forbidden) if term in self.seed_text]
        self.assertEqual([], found)

    def test_seed_has_no_opaque_ingredient_count_phrases(self) -> None:
        found = []
        for recipe in self.recipes:
            recipe_text = " ".join(flatten_strings(recipe))
            if FORBIDDEN_OPAQUE_INGREDIENT_COUNT_PATTERN.search(recipe_text):
                found.append(recipe["name"])
        self.assertEqual([], found)

    def test_recipe_steps_do_not_use_placeholder_titles(self) -> None:
        found = []
        for recipe in self.recipes:
            for step in recipe["recipe_steps"]:
                if step["title"] in FORBIDDEN_PLACEHOLDER_STEP_TITLES:
                    found.append((recipe["name"], step["title"]))
        self.assertEqual([], found)

    def test_recipe_names_match_core_cooking_method(self) -> None:
        for recipe in self.recipes:
            recipe_text = " ".join(
                f"{step['title']} {step['instruction']}"
                for step in recipe["recipe_steps"]
            )
            for method_name, required_terms in METHOD_NAME_RULES.items():
                if method_name not in recipe["name"]:
                    continue
                with self.subTest(recipe=recipe["name"], method_name=method_name):
                    self.assertTrue(
                        any(term in recipe_text for term in required_terms),
                        f"{recipe['name']} must mention one of {sorted(required_terms)} in steps",
                    )

    def test_all_recipes_have_service_grade_cooking_steps(self) -> None:
        for recipe in self.recipes:
            with self.subTest(recipe=recipe["name"]):
                self.assertGreaterEqual(len(recipe["recipe_steps"]), 6)
                recipe_text = " ".join(flatten_strings(recipe))
                found = [
                    phrase
                    for phrase in sorted(FORBIDDEN_GENERIC_PHRASES)
                    if phrase in recipe_text
                ]
                self.assertEqual([], found)

                for step in recipe["recipe_steps"]:
                    self.assertRegex(step["instruction"], r"\d")

    def test_recipes_do_not_overclaim_broad_ingredient_variants(self) -> None:
        for recipe in self.recipes:
            recipe_text = " ".join(
                [
                    recipe["name"],
                    recipe["reason"],
                    recipe["pairing_knowledge"]["flavor_logic"],
                    recipe["pairing_knowledge"]["ingredient_logic"],
                    recipe["pairing_knowledge"]["why_this_liquor"],
                    " ".join(step["instruction"] for step in recipe["recipe_steps"]),
                    " ".join(ingredient["display_name"] for ingredient in recipe["ingredient_details"]),
                ]
            )
            ingredient_keys = {
                ingredient["item_name"] for ingredient in recipe["ingredient_details"]
            }

            for ingredient_key, unsafe_terms in BROAD_KEY_UNSAFE_TERMS.items():
                if ingredient_key not in ingredient_keys:
                    continue
                with self.subTest(recipe=recipe["name"], ingredient_key=ingredient_key):
                    found = [term for term in sorted(unsafe_terms) if term in recipe_text]
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
                self.assertGreaterEqual(len(recipe["ingredient_details"]), 1)
                self.assertLessEqual(len(recipe["ingredient_details"]), 30)
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
        self.assertEqual("green_onion", normalize_ingredient_key("leek"))
        self.assertEqual("green_onion", normalize_ingredient_key("scallion"))
        self.assertEqual("green_onion", normalize_ingredient_key("spring_onion"))
        self.assertEqual("pepper", normalize_ingredient_key("파프리카"))
        self.assertEqual("대파", ingredient_display_name("green_onion"))
        self.assertEqual("파프리카", ingredient_display_name("pepper"))

    def test_liquor_mapping_accepts_korean_and_internal_keys(self) -> None:
        self.assertEqual("red_wine", normalize_liquor_key("레드와인"))
        self.assertEqual("red_wine", normalize_liquor_key("red_wine"))
        self.assertEqual("red_wine", normalize_liquor_key("와인"))
        self.assertEqual("red_wine", normalize_liquor_key("wine"))
        self.assertEqual("beer", normalize_liquor_key("beer"))
        self.assertEqual("whisky", normalize_liquor_key("whisky"))
        self.assertEqual("sparkling_wine", normalize_liquor_key("스파클링와인"))
        self.assertEqual("스파클링와인", liquor_display_name("sparkling_wine"))

    def test_manual_scan_mock_covers_all_seed_liquors(self) -> None:
        self.assertEqual(
            set(EXPECTED_LIQUOR_COUNTS),
            set(MOCK_LIQUOR_SCAN_CANDIDATES),
        )
        self.assertEqual(7, len(MOCK_LIQUOR_SCAN_CANDIDATES))


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
    def test_inventory_bulk_accepts_one_to_thirty_items(self) -> None:
        self.assertEqual(["대파"], InventoryBulkCreate(items=["대파"]).items)
        self.assertEqual(30, len(InventoryBulkCreate(items=["대파"] * 30).items))

        with self.assertRaises(ValidationError):
            InventoryBulkCreate(items=[])

        with self.assertRaises(ValidationError):
            InventoryBulkCreate(items=["대파"] * 31)

    def test_recommendation_response_schema_has_realistic_example(self) -> None:
        schema = RecommendationsResponse.model_json_schema()
        example = schema.get("example")
        recommendation_schema = schema["$defs"]["RecommendationItem"]["properties"][
            "ingredient_details"
        ]

        self.assertEqual(1, recommendation_schema["minItems"])
        self.assertEqual(30, recommendation_schema["maxItems"])

        self.assertIsInstance(example, dict)
        self.assertEqual("소주", example["liquor"])
        self.assertEqual(1, len(example["recommendations"]))

        first = example["recommendations"][0]
        self.assertEqual(["돼지고기"], first["missing_ingredients"])
        self.assertEqual(["대파", "상추"], first["ingredient_yes"])
        self.assertEqual(["돼지고기"], first["ingredient_no"])
        self.assertIn("recipe_steps", first)
        self.assertIn("pairing_knowledge", first)
        self.assertIn("score_breakdown", first)

        first_ingredient = first["ingredient_details"][0]
        self.assertEqual("pork", first_ingredient["item_name"])
        self.assertEqual("돼지고기", first_ingredient["display_name"])

        example_text = json.dumps(example, ensure_ascii=False)
        self.assertNotIn('"liquor": "soju"', example_text)
        self.assertNotIn('"missing_ingredients": ["pork"', example_text)

    def test_api_contract_docs_cover_fe_and_ai_handoff_fields(self) -> None:
        fe_contract = FE_API_CONTRACT_PATH.read_text(encoding="utf-8")
        ai_contract = AI_API_CONTRACT_PATH.read_text(encoding="utf-8")
        workflow = API_CHANGE_WORKFLOW_PATH.read_text(encoding="utf-8")

        fe_required_terms = [
            "`/api/v1/recommendations`",
            "`/api/v1/stream/recommendations`",
            "ingredient_yes",
            "ingredient_no",
            "missing_ingredients",
            "ingredient_details[].status",
            "pepper`는 고추가 아니라 파프리카",
        ]
        ai_required_terms = [
            "POST `/api/v1/recognitions/ingredients`",
            "POST `/api/v1/recognitions/liquor`",
            "leek`, `scallion`, `spring_onion`",
            "BE에서 `green_onion`으로 정규화",
            "ginger`는 AI label에는 있을 수 있지만 추천 seed core ingredient로 사용하지 않습니다",
            "soju, beer, red_wine, white_wine, sparkling_wine, whisky, sake",
        ]
        workflow_required_terms = [
            "main 직접 push/merge 금지",
            "새 기능/수정은 GitHub issue 먼저 생성",
            "Sheet Template",
            "기존 FE 응답 필드는 깨지지 않게 additive change 우선",
        ]

        for term in fe_required_terms:
            with self.subTest(doc="fe", term=term):
                self.assertIn(term, fe_contract)
        for term in ai_required_terms:
            with self.subTest(doc="ai", term=term):
                self.assertIn(term, ai_contract)
        for term in workflow_required_terms:
            with self.subTest(doc="workflow", term=term):
                self.assertIn(term, workflow)

    def test_readme_recommendation_example_uses_display_values(self) -> None:
        readme_text = README_PATH.read_text(encoding="utf-8")

        self.assertIn('"liquor": "소주"', readme_text)
        self.assertIn('"missing_ingredients": ["돼지고기", "마늘"]', readme_text)
        self.assertNotIn('"liquor": "soju"', readme_text)
        self.assertNotIn('"missing_ingredients": ["pork", "garlic"]', readme_text)

    def test_recommendation_stream_docs_do_not_claim_fixed_delay(self) -> None:
        events_route_text = EVENT_ROUTE_PATH.read_text(encoding="utf-8")

        self.assertNotIn("약간의 지연 후 생성된 추천 결과", events_route_text)


class OperationsReadinessQualityGateTest(unittest.TestCase):
    def test_readiness_doc_covers_environment_database_and_seed_flow(self) -> None:
        doc_text = OPERATIONS_READINESS_PATH.read_text(encoding="utf-8")

        required_terms = [
            "python -m venv .venv",
            "DATABASE_URL=mysql+pymysql://",
            "scripts\\initialize_database.py",
            "RECOMMENDATION_RESPONSE_DELAY_SECONDS=0",
            "FE smoke test",
            "SQLite",
            "MySQL",
            "Seed 확장",
        ]

        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, doc_text)

    def test_database_initializer_creates_tables_and_loads_seed_data(self) -> None:
        script_text = DB_INIT_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("Base.metadata.create_all(bind=engine)", script_text)
        self.assertIn("seed_recommendation_data(db)", script_text)
        self.assertIn("render_as_string(hide_password=True)", script_text)

    def test_readme_links_operations_readiness_assets(self) -> None:
        readme_text = README_PATH.read_text(encoding="utf-8")

        self.assertIn("docs/operations_readiness.md", readme_text)
        self.assertIn("scripts/initialize_database.py", readme_text)


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

    def test_recommendation_exposes_simple_ingredient_availability_lists(self) -> None:
        self.db.add_all(
            [
                InventoryItem(item_name="green_onion", count=1),
                InventoryItem(item_name="garlic", count=1),
            ]
        )
        self.db.commit()

        response = RecommendationService(self.db).get_recommendations("소주", False)

        self.assertEqual(3, len(response.recommendations))
        for recommendation in response.recommendations:
            expected_yes = [
                detail.display_name
                for detail in recommendation.ingredient_details
                if detail.status == "available"
            ]
            expected_no = [
                detail.display_name
                for detail in recommendation.ingredient_details
                if detail.status == "missing"
            ]

            self.assertEqual(expected_yes, recommendation.ingredient_yes)
            self.assertEqual(expected_no, recommendation.ingredient_no)
            self.assertEqual(expected_no, recommendation.missing_ingredients)

    def test_refresh_rotates_beyond_two_recommendation_sets(self) -> None:
        service = RecommendationService(self.db)
        seen_names: list[str] = []

        response = service.get_recommendations("소주", False)
        seen_names.extend(item.name for item in response.recommendations)

        for _ in range(3):
            response = service.get_recommendations("소주", True)
            seen_names.extend(item.name for item in response.recommendations)

        self.assertEqual(12, len(seen_names))
        self.assertGreaterEqual(len(set(seen_names)), 9)

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
