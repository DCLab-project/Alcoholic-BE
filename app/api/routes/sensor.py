from fastapi import APIRouter

from app.schemas.sensor import SensorEventAcceptedResponse, SensorEventCreate
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/api/v1/sensors", tags=["센서 이벤트"])


@router.post(
    "/events",
    response_model=SensorEventAcceptedResponse,
    summary="Arduino 센서 이벤트 수신",
    description=(
        "Jetson에 연결된 Arduino 센서 입력을 백엔드에 전달합니다. "
        "문열림이 감지되면 식재료 인식 준비 상태로, 문닫힘 상태에서 사용자 접근이 감지되면 "
        "주류 인식 준비 상태로 판단합니다. 실제 식재료/주류 인식 결과는 기존 "
        "`/api/v1/recognitions/ingredients`, `/api/v1/recognitions/liquor` API로 전달됩니다."
    ),
    response_description="정규화된 센서 이벤트와 권장 인식 모드를 반환합니다.",
)
async def create_sensor_event(
    payload: SensorEventCreate,
) -> SensorEventAcceptedResponse:
    event = await SensorService().publish_sensor_event(payload)
    return SensorEventAcceptedResponse(
        message="센서 이벤트가 수신되었습니다.",
        event=event,
    )
