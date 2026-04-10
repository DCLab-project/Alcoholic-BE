from fastapi import APIRouter, status

from app.schemas.recognition import (
    IngredientLiveRecognitionCreate,
    LiquorLiveRecognitionCreate,
    LiveRecognitionAcceptedResponse,
)
from app.services.recognition_service import RecognitionService

router = APIRouter(prefix="/api/v1/recognitions", tags=["내부용 API (AI 입력)"])


@router.post(
    "/ingredients",
    response_model=LiveRecognitionAcceptedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="식재료 실시간 인식 이벤트 수신",
    description=(
        "Jetson/AI가 감지한 식재료 인식 결과를 수신하고, "
        "즉시 SSE 식재료 스트림으로 전달합니다. "
        "이 단계에서는 재고 DB에 최종 저장하지 않고, 프론트 화면의 임시 리스트 표시용 이벤트만 발행합니다."
    ),
    response_description="식재료 실시간 인식 이벤트 발행 결과를 반환합니다.",
    include_in_schema=False,
)
async def publish_ingredient_recognition(
    payload: IngredientLiveRecognitionCreate,
) -> LiveRecognitionAcceptedResponse:
    service = RecognitionService()
    return await service.publish_ingredient_live_result(payload)


@router.post(
    "/liquor",
    response_model=LiveRecognitionAcceptedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="주류 실시간 인식 이벤트 수신",
    description=(
        "Jetson/AI가 감지한 주류 인식 결과를 수신하고, "
        "즉시 SSE 주류 스트림으로 전달합니다."
    ),
    response_description="주류 실시간 인식 이벤트 발행 결과를 반환합니다.",
    include_in_schema=False,
)
async def publish_liquor_recognition(
    payload: LiquorLiveRecognitionCreate,
) -> LiveRecognitionAcceptedResponse:
    service = RecognitionService()
    return await service.publish_liquor_live_result(payload)
