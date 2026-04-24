from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.config.settings import get_settings
from app.db import Base, SessionLocal, engine
from app.seeds.recommendation_seed import seed_recommendation_data

settings = get_settings()

openapi_tags = [
    {
        "name": "상태 확인",
        "description": "백엔드 서버가 정상적으로 동작 중인지 확인하는 API입니다.",
    },
    {
        "name": "스캔 요청",
        "description": "프론트가 수동으로 식재료 또는 주류 스캔을 요청할 때 사용하는 API입니다.",
    },
    {
        "name": "재고 관리",
        "description": "현재 식재료 재고를 조회하고, 일괄 저장하거나 수량을 수동 조절하는 API입니다.",
    },
    {
        "name": "실시간 스트림",
        "description": "프론트엔드가 구독하는 SSE 스트림 API입니다. 식재료/주류 감지 결과를 실시간으로 받을 때 사용합니다.",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_recommendation_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "술안주 추천 AI 냉장고 프로젝트의 백엔드 서버입니다.\n\n"
        "현재는 식재료/주류 실시간 인식 이벤트 수신, 재고 일괄 저장, "
        "재고 조회, 수량 수동 조절, SSE 기반 실시간 스트림을 우선 제공합니다.\n\n"
        "프론트엔드 테스트용 Swagger 문서에는 FE가 직접 사용하는 API만 표시합니다. "
        "Jetson/AI가 호출하는 내부용 인식 입력 API는 실제로 존재하지만 문서에서는 숨겨둔 상태입니다."
    ),
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

app.include_router(api_router)
