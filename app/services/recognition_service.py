import asyncio
from datetime import datetime, timezone

from app.schemas.recognition import (
    IngredientLiveRecognitionCreate,
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
from app.services.recommendation_service import RecommendationService


class RecognitionService:
    async def publish_ingredient_live_result(
        self, payload: IngredientLiveRecognitionCreate
    ) -> LiveRecognitionAcceptedResponse:
        event_payload = IngredientStreamEvent(
            ingredient_name=payload.ingredient_name,
            timestamp=payload.timestamp,
        )
        await ingredient_event_broker.publish(event_payload.model_dump(mode="json"))
        return LiveRecognitionAcceptedResponse(
            status="success",
            message="Ingredient live event published.",
        )

    async def publish_liquor_live_result(
        self, payload: LiquorLiveRecognitionCreate
    ) -> LiveRecognitionAcceptedResponse:
        event_payload = LiquorStreamEvent(
            liquor_name=payload.liquor_name,
            timestamp=payload.timestamp,
        )
        await liquor_event_broker.publish(event_payload.model_dump(mode="json"))
        asyncio.create_task(self._publish_recommendation_event(payload.liquor_name))
        return LiveRecognitionAcceptedResponse(
            status="success",
            message="Liquor live event published.",
        )

    async def start_liquor_scan(
        self, payload: LiquorScanStartRequest
    ) -> LiquorScanStartResponse:
        scan_request_id = (
            f"liquor-scan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]}"
        )
        asyncio.create_task(self._mock_liquor_scan_flow(payload.device_id))
        return LiquorScanStartResponse(
            status="accepted",
            message="주류 스캔을 시작했습니다.",
            scan_request_id=scan_request_id,
        )

    async def _mock_liquor_scan_flow(self, device_id: str) -> None:
        # FE가 스캔 중 상태를 잠깐 보여줄 수 있도록 약간의 지연 후
        # mock 주류 인식 결과를 발행합니다.
        await asyncio.sleep(3.0)
        payload = LiquorLiveRecognitionCreate(
            liquor_name="soju",
            timestamp=datetime.now(timezone.utc),
            confidence=0.99,
            source=f"manual_scan_mock:{device_id}",
        )
        await self.publish_liquor_live_result(payload)

    async def _publish_recommendation_event(self, liquor_name: str) -> None:
        recommendation_service = RecommendationService()
        recommendations = await asyncio.to_thread(
            recommendation_service.get_recommendations,
            liquor_name,
            False,
        )
        await recommendation_event_broker.publish(
            recommendations.model_dump(mode="json")
        )
