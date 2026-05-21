from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.event_stream import (
    ingredient_event_broker,
    liquor_event_broker,
    recommendation_event_broker,
    sensor_event_broker,
)

router = APIRouter(prefix="/api/v1/stream", tags=["실시간 스트림"])


@router.get(
    "/ingredients",
    summary="실시간 식재료 감지 스트림",
    description=(
        "식재료 인식 이벤트를 Server-Sent Events(SSE) 방식으로 실시간 스트리밍합니다. "
        "프론트는 이 스트림을 구독한 상태에서 새 식재료 감지 결과가 들어오면 리스트 UI를 즉시 갱신하면 됩니다."
    ),
    response_description="ingredient 이벤트가 SSE 형식으로 지속적으로 전달됩니다.",
)
async def stream_ingredient_events() -> StreamingResponse:
    queue = ingredient_event_broker.subscribe()
    return StreamingResponse(
        ingredient_event_broker.stream(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get(
    "/liquor",
    summary="실시간 주류 감지 스트림",
    description=(
        "주류 인식 이벤트를 Server-Sent Events(SSE) 방식으로 실시간 스트리밍합니다. "
        "카메라에 술을 가져다대면 프론트는 이 스트림에서 술 종류를 먼저 즉시 받을 수 있습니다."
    ),
    response_description="liquor 이벤트가 SSE 형식으로 지속적으로 전달됩니다.",
)
async def stream_liquor_events() -> StreamingResponse:
    queue = liquor_event_broker.subscribe()
    return StreamingResponse(
        liquor_event_broker.stream(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get(
    "/recommendations",
    summary="실시간 추천 결과 스트림",
    description=(
        "주류 감지 이벤트가 들어온 뒤 생성된 추천 결과를 Server-Sent Events(SSE) 방식으로 실시간 스트리밍합니다. "
        "프론트는 이 스트림을 구독하면 술 이름을 먼저 보여주고, 추천 카드 3개를 자동으로 갱신할 수 있습니다."
    ),
    response_description="recommendation 이벤트가 SSE 형식으로 지속적으로 전달됩니다.",
)
async def stream_recommendation_events() -> StreamingResponse:
    queue = recommendation_event_broker.subscribe()
    return StreamingResponse(
        recommendation_event_broker.stream(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get(
    "/sensors",
    summary="실시간 센서 이벤트 스트림",
    description=(
        "Jetson에 연결된 Arduino 센서 이벤트를 Server-Sent Events(SSE) 방식으로 스트리밍합니다. "
        "문열림, 사용자 접근 여부와 백엔드가 계산한 recommended_mode를 확인할 수 있습니다."
    ),
    response_description="sensor 이벤트가 SSE 형식으로 지속적으로 전달됩니다.",
)
async def stream_sensor_events() -> StreamingResponse:
    queue = sensor_event_broker.subscribe()
    return StreamingResponse(
        sensor_event_broker.stream(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
