from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        "description": "현재 식재료 재고를 조회하고, 저장하거나 수량을 수동 조절하는 API입니다.",
    },
    {
        "name": "실시간 스트림",
        "description": "프론트엔드가 구독하는 SSE 스트림 API입니다. 식재료, 주류, 추천 결과를 실시간으로 전달합니다.",
    },
    {
        "name": "추천",
        "description": "현재 재고와 주류 기준으로 추천 결과를 조회하는 API입니다.",
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
        "현재는 식재료/주류 실시간 이벤트 수신, 재고 관리, 수동 스캔 fallback, "
        "seed 레시피 기반 추천 반환 흐름을 우선 구현했습니다.\n\n"
        "Swagger 문서에는 프론트가 직접 사용하는 API 중심으로 노출하며, "
        "Jetson/AI 내부 입력용 API는 문서에서 숨겨져 있습니다."
    ),
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
