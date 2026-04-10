from fastapi import APIRouter

router = APIRouter(tags=["상태 확인"])


@router.get(
    "/health",
    summary="서버 상태 확인",
    description="백엔드 서버가 정상적으로 실행 중인지 확인합니다.",
    response_description="서버 정상 동작 여부를 반환합니다.",
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}
