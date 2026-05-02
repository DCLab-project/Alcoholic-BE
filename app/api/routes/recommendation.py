from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.recommendation import (
    RecommendationRefreshRequest,
    RecommendationRefreshResponse,
    RecommendationsResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["추천"])


@router.get(
    "",
    response_model=RecommendationsResponse,
    summary="안주 추천 조회 및 재요청",
    description=(
        "감지된 주류와 현재 재고를 기준으로 안주 추천 결과를 반환합니다. "
        "현재는 seed 레시피 DB와 현재 재고를 비교해 추천 3개를 반환하며, refresh=true이면 보조 추천 세트를 다시 조회합니다."
    ),
    response_description="주류 기준 추천 안주 목록을 반환합니다.",
)
def get_recommendations(
    liquor: str = Query(
        ...,
        description="추천 기준이 되는 주류 이름입니다. 한글명과 내부 key를 모두 허용합니다.",
        examples=["소주"],
    ),
    refresh: bool = Query(False, description="true이면 다른 추천 세트를 다시 요청합니다"),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    service = RecommendationService(db)
    return service.get_recommendations(liquor=liquor, refresh=refresh)


@router.post(
    "/refresh",
    response_model=RecommendationRefreshResponse,
    summary="고정 추천 제외 재추천",
    description="고정된 추천은 유지하고 나머지만 새 추천으로 채워 총 3개를 반환합니다.",
)
def refresh_recommendations(
    payload: RecommendationRefreshRequest,
    db: Session = Depends(get_db),
) -> RecommendationRefreshResponse:
    service = RecommendationService(db)
    return service.refresh_with_keep(payload)
