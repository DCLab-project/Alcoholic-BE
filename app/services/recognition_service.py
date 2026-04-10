import asyncio

from app.schemas.recognition import (
    IngredientLiveRecognitionCreate,
    IngredientStreamEvent,
    LiquorLiveRecognitionCreate,
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
