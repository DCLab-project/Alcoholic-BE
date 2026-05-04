from fastapi import APIRouter

from app.schemas.recognition import (
    IngredientScanStartRequest,
    IngredientScanStartResponse,
    LiquorScanStartRequest,
    LiquorScanStartResponse,
)
from app.services.recognition_service import RecognitionService

router = APIRouter(prefix="/api/v1/scan", tags=["스캔 요청"])


@router.post(
    "/liquor/start",
    response_model=LiquorScanStartResponse,
    summary="주류 스캔 요청",
    description=(
        "홈 화면에서 주류 스캔 버튼을 누르면 백엔드가 주류 스캔 요청을 접수합니다. "
        "이 API는 scan_request_id만 발급하며, 실제 인식 결과는 AI/Jetson이 "
        "`/api/v1/recognitions/liquor`로 POST할 때 SSE로 발행됩니다."
    ),
    response_description="주류 스캔 요청 접수 결과와 scan_request_id를 반환합니다.",
)
async def start_liquor_scan(
    payload: LiquorScanStartRequest,
) -> LiquorScanStartResponse:
    service = RecognitionService()
    return await service.start_liquor_scan(payload)


@router.post(
    "/ingredients/start",
    response_model=IngredientScanStartResponse,
    summary="식재료 스캔 요청",
    description=(
        "홈 화면에서 식재료 스캔 버튼을 누르면 백엔드가 식재료 스캔 요청을 접수합니다. "
        "이 API는 scan_request_id만 발급하며, 실제 인식 결과는 AI/Jetson이 "
        "`/api/v1/recognitions/ingredients`로 POST할 때 SSE로 발행됩니다."
    ),
    response_description="식재료 스캔 요청 접수 결과와 scan_request_id를 반환합니다.",
)
async def start_ingredient_scan(
    payload: IngredientScanStartRequest,
) -> IngredientScanStartResponse:
    service = RecognitionService()
    return await service.start_ingredient_scan(payload)
