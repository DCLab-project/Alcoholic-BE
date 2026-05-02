import asyncio
from datetime import datetime, timezone
from random import choice

from app.db import SessionLocal
from app.schemas.recognition import (
    IngredientLiveRecognitionCreate,
    IngredientScanStartRequest,
    IngredientScanStartResponse,
    IngredientStreamEvent,
    LiquorLiveRecognitionCreate,
    LiquorScanStartRequest,
    LiquorScanStartResponse,
    LiquorStreamEvent,
    LiveRecognitionAcceptedResponse,
)
from app.services.event_stream import (
    ingredient_event_broker,
    liquor_event_broker,
    recommendation_event_broker,
)
from app.services.name_mapping import (
    ingredient_display_name,
    liquor_display_name,
    normalize_ingredient_key,
    normalize_liquor_key,
)
from app.services.recommendation_service import RecommendationService


MOCK_LIQUOR_SCAN_CANDIDATES: tuple[str, ...] = (
    "soju",
    "beer",
    "red_wine",
    "white_wine",
    "sparkling_wine",
    "whisky",
    "sake",
)

MOCK_INGREDIENT_SCAN_CANDIDATES: tuple[str, ...] = (
    "green_onion",
    "onion",
    "garlic",
    "egg",
    "pork",
    "potato",
    "mushroom",
)


class RecognitionService:
    async def publish_ingredient_live_result(
        self, payload: IngredientLiveRecognitionCreate
    ) -> LiveRecognitionAcceptedResponse:
        ingredient_key = normalize_ingredient_key(payload.ingredient_name)
        event_payload = IngredientStreamEvent(
            ingredient_name=ingredient_display_name(ingredient_key),
            timestamp=payload.timestamp,
            scan_request_id=payload.scan_request_id,
        )
        await ingredient_event_broker.publish(event_payload.model_dump(mode="json"))
        return LiveRecognitionAcceptedResponse(
            status="success",
            message="식재료 인식 이벤트가 발행되었습니다.",
        )

    async def publish_liquor_live_result(
        self, payload: LiquorLiveRecognitionCreate
    ) -> LiveRecognitionAcceptedResponse:
        liquor_key = normalize_liquor_key(payload.liquor_name)
        event_payload = LiquorStreamEvent(
            liquor_name=liquor_display_name(liquor_key),
            timestamp=payload.timestamp,
            scan_request_id=payload.scan_request_id,
        )
        await liquor_event_broker.publish(event_payload.model_dump(mode="json"))
        asyncio.create_task(self._publish_recommendation_event(liquor_key))
        return LiveRecognitionAcceptedResponse(
            status="success",
            message="주류 인식 이벤트가 발행되었습니다.",
        )

    async def start_liquor_scan(
        self, payload: LiquorScanStartRequest
    ) -> LiquorScanStartResponse:
        scan_request_id = (
            f"liquor-scan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]}"
        )
        asyncio.create_task(self._mock_liquor_scan_flow(payload.device_id, scan_request_id))
        return LiquorScanStartResponse(
            status="accepted",
            message="주류 스캔을 시작했습니다.",
            scan_request_id=scan_request_id,
        )

    async def start_ingredient_scan(
        self, payload: IngredientScanStartRequest
    ) -> IngredientScanStartResponse:
        scan_request_id = (
            f"ingredient-scan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]}"
        )
        asyncio.create_task(
            self._mock_ingredient_scan_flow(payload.device_id, scan_request_id)
        )
        return IngredientScanStartResponse(
            status="accepted",
            message="식재료 스캔을 시작했습니다.",
            scan_request_id=scan_request_id,
        )

    async def _mock_liquor_scan_flow(self, device_id: str, scan_request_id: str) -> None:
        # FE가 스캔 중 상태를 잠깐 보여줄 수 있도록 약간의 지연 후
        # mock 주류 인식 결과를 발행합니다.
        await asyncio.sleep(3.0)
        payload = LiquorLiveRecognitionCreate(
            liquor_name=choice(MOCK_LIQUOR_SCAN_CANDIDATES),
            timestamp=datetime.now(timezone.utc),
            confidence=0.99,
            source=f"manual_scan_mock:{device_id}",
            scan_request_id=scan_request_id,
        )
        await self.publish_liquor_live_result(payload)

    async def _mock_ingredient_scan_flow(
        self, device_id: str, scan_request_id: str
    ) -> None:
        await asyncio.sleep(1.0)
        payload = IngredientLiveRecognitionCreate(
            ingredient_name=choice(MOCK_INGREDIENT_SCAN_CANDIDATES),
            timestamp=datetime.now(timezone.utc),
            confidence=0.98,
            source=f"manual_scan_mock:{device_id}",
            scan_request_id=scan_request_id,
        )
        await self.publish_ingredient_live_result(payload)

    async def _publish_recommendation_event(self, liquor_name: str) -> None:
        liquor_key = normalize_liquor_key(liquor_name)
        db = SessionLocal()
        try:
            recommendation_service = RecommendationService(db)
            recommendations = await asyncio.to_thread(
                recommendation_service.get_recommendations,
                liquor_key,
                False,
            )
            await recommendation_event_broker.publish(
                recommendations.model_dump(mode="json")
            )
        finally:
            db.close()
