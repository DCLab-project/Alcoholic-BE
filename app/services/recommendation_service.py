import time

from app.schemas.recommendation import RecommendationItem, RecommendationsResponse


class RecommendationService:
    def get_recommendations(self, liquor: str, refresh: bool) -> RecommendationsResponse:
        liquor_value = liquor or "soju"
        normalized = liquor_value.strip().lower()

        recommendation_sets = {
            "soju": {
                False: [
                    RecommendationItem(
                        name="대파 삼겹살 볶음",
                        reason="소주의 알싸한 맛과 잘 어울리고, 짭짤한 볶음 풍미가 잘 받쳐줍니다.",
                        recipe=["1: 대파를 길게 썹니다", "2: 삼겹살을 노릇하게 굽습니다", "3: 대파와 함께 볶아 간을 맞춥니다"],
                        missing_ingredients=["pork", "oyster_sauce"],
                    ),
                    RecommendationItem(
                        name="양파 참치전",
                        reason="부담 없이 만들 수 있고 소주와 함께 먹기 좋은 담백한 안주입니다.",
                        recipe=["1: 양파를 잘게 썹니다", "2: 참치와 반죽을 섞습니다", "3: 팬에 노릇하게 부칩니다"],
                        missing_ingredients=["tuna", "flour"],
                    ),
                    RecommendationItem(
                        name="토마토 달걀볶음",
                        reason="새콤한 토마토가 소주와 함께 먹을 때 느끼함을 줄여줍니다.",
                        recipe=["1: 토마토를 썹니다", "2: 달걀을 스크램블합니다", "3: 함께 볶아 마무리합니다"],
                        missing_ingredients=["egg"],
                    ),
                ],
                True: [
                    RecommendationItem(
                        name="감자 버터구이",
                        reason="짭짤하고 고소해서 소주와 함께 가볍게 즐기기 좋습니다.",
                        recipe=["1: 감자를 삶습니다", "2: 버터에 굽습니다", "3: 소금과 후추로 마무리합니다"],
                        missing_ingredients=["butter"],
                    ),
                    RecommendationItem(
                        name="오이 무침",
                        reason="상큼하고 아삭해서 소주와 잘 어울리는 기본 안주입니다.",
                        recipe=["1: 오이를 썹니다", "2: 양념을 넣고 버무립니다", "3: 참깨를 뿌립니다"],
                        missing_ingredients=["gochugaru", "vinegar"],
                    ),
                    RecommendationItem(
                        name="소시지 채소볶음",
                        reason="짭짤한 소시지와 채소 조합이 소주 안주로 무난합니다.",
                        recipe=["1: 소시지와 채소를 썹니다", "2: 팬에 함께 볶습니다", "3: 케첩 또는 간장으로 마무리합니다"],
                        missing_ingredients=["sausage", "ketchup"],
                    ),
                ],
            }
        }

        selected = recommendation_sets.get(normalized, recommendation_sets["soju"])
        recommendations = selected[bool(refresh)]

        time.sleep(5)
        return RecommendationsResponse(liquor=liquor_value, recommendations=recommendations)
