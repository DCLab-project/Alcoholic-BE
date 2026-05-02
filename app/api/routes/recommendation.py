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
        "현재는 seed 레시피 DB와 현재 재고를 비교해 추천 3개를 반환하며, refresh=true이면 보조 추천 세트를 다시 조회합니다. "
        "필요하면 부족 재료 수, 조리 시간, 난이도 조건으로 결과를 좁힐 수 있습니다."
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
    available_only: bool = Query(
        False,
        description="true이면 현재 냉장고 재료만으로 만들 수 있는 추천만 반환합니다.",
    ),
    max_missing_count: int | None = Query(
        None,
        ge=0,
        le=30,
        description="허용할 부족 핵심 재료 최대 개수입니다. 예: 1이면 부족 재료가 1개 이하인 추천만 반환합니다.",
    ),
    max_cook_time_minutes: int | None = Query(
        None,
        ge=1,
        le=240,
        description="허용할 최대 조리 시간(분)입니다.",
    ),
    difficulty: str | None = Query(
        None,
        description="원하는 난이도입니다. easy, medium, hard 중 하나를 보냅니다.",
    ),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    service = RecommendationService(db)
    return service.get_recommendations(
        liquor=liquor,
        refresh=refresh,
        available_only=available_only,
        max_missing_count=max_missing_count,
        max_cook_time_minutes=max_cook_time_minutes,
        difficulty=difficulty,
    )


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
