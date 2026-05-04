import asyncio
from datetime import datetime, timezone

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
        _ = payload
        scan_request_id = (
            f"liquor-scan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]}"
        )
        return LiquorScanStartResponse(
            status="accepted",
            message="주류 스캔을 시작했습니다.",
            scan_request_id=scan_request_id,
        )

    async def start_ingredient_scan(
        self, payload: IngredientScanStartRequest
    ) -> IngredientScanStartResponse:
        _ = payload
        scan_request_id = (
            f"ingredient-scan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]}"
        )
        return IngredientScanStartResponse(
            status="accepted",
            message="식재료 스캔을 시작했습니다.",
            scan_request_id=scan_request_id,
        )

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
