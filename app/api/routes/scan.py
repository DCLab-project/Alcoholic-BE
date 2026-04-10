from fastapi import APIRouter

from app.schemas.recognition import LiquorScanStartRequest, LiquorScanStartResponse
from app.services.recognition_service import RecognitionService

router = APIRouter(prefix="/api/v1/scan", tags=["스캔 요청"])


@router.post(
    "/liquor/start",
    response_model=LiquorScanStartResponse,
    summary="주류 스캔 요청",
    description=(
        "홈 화면에서 주류 스캔 버튼을 누르면 백엔드가 주류 스캔 요청을 접수합니다. "
        "현재는 FE 테스트를 위해 mock 스캔 흐름을 실행하며, 접수 후 잠시 뒤 주류 SSE와 추천 SSE를 순차적으로 발행합니다."
    ),
    response_description="주류 스캔 요청 접수 결과와 scan_request_id를 반환합니다.",
)
async def start_liquor_scan(
    payload: LiquorScanStartRequest,
) -> LiquorScanStartResponse:
    service = RecognitionService()
    return await service.start_liquor_scan(payload)
