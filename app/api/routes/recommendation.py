from fastapi import APIRouter, Query

from app.schemas.recommendation import RecommendationsResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["추천"])


@router.get(
    "",
    response_model=RecommendationsResponse,
    summary="안주 추천 조회 및 재요청",
    description=(
        "감지된 주류와 현재 재고를 기준으로 안주 추천 결과를 반환합니다. "
        "현재는 프론트 UI 테스트를 위한 mock 추천 결과를 내려주며, refresh=true이면 다른 추천 세트를 반환합니다."
    ),
    response_description="주류 기준 추천 안주 목록을 반환합니다.",
)
def get_recommendations(
    liquor: str = Query(..., description="추천 기준이 되는 주류 이름", examples=["soju"]),
    refresh: bool = Query(False, description="true이면 다른 추천 세트를 다시 요청합니다"),
) -> RecommendationsResponse:
    service = RecommendationService()
    return service.get_recommendations(liquor=liquor, refresh=refresh)
