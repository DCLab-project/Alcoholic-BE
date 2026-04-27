# Seed Expansion Plan - Issue 20

Existing `seeds/recommendations.json` was indexed by normalized name, core ingredient key set, cooking method, and filtered tags before these candidates were accepted.

| # | liquor | name | core_keys | method | tags | review |
|---:|---|---|---|---|---|---|
| 1 | soju | 닭대파 맑은탕 | chicken, green_onion, onion, garlic | 탕 | 탕, 닭고기, 대파, 소주 | pass |
| 2 | soju | 감자 돼지고기 짭조림 | pork, potato, onion, garlic | 조림 | 조림, 돼지고기, 감자, 소주 | pass |
| 3 | soju | 오이 닭고기 초무침 | chicken, cucumber, carrot, onion | 무침 | 무침, 닭고기, 오이, 소주 | pass |
| 4 | soju | 애호박 소고기 달걀전 | zucchini, beef, egg, green_onion | 전 | 전, 애호박, 소고기, 소주 | pass |
| 5 | soju | 버섯 돼지고기 마늘찜 | pork, mushroom, garlic, green_onion | 찜 | 찜, 돼지고기, 버섯, 소주 | pass |
| 6 | soju | 토마토 닭고기 대파볶음 | chicken, tomato, green_onion, garlic | 볶음 | 볶음, 닭고기, 토마토, 소주 | pass |
| 7 | soju | 양배추 소시지 팬구이 | sausage, cabbage, onion, garlic | 팬구이 | 팬구이, 소시지, 양배추, 소주 | pass |
| 8 | soju | 시금치 베이컨 달걀말이 | spinach, bacon, egg, milk | 달걀말이 | 달걀말이, 시금치, 베이컨, 소주 | pass |
| 9 | soju | 상추 소고기 겨자샐러드 | beef, lettuce, cucumber, onion | 샐러드 | 샐러드, 소고기, 상추, 소주 | pass |
| 10 | soju | 파프리카 생선살 맑은찜 | fish, pepper, green_onion, garlic | 찜 | 찜, 생선살, 파프리카, 소주 | pass |
| 11 | beer | 양파 베이컨 감자전 | potato, bacon, onion, egg | 전 | 전, 감자, 베이컨, 맥주 | pass |
| 12 | beer | 마늘버터 소시지 버섯구이 | sausage, mushroom, butter, garlic | 팬구이 | 팬구이, 소시지, 버섯, 맥주 | pass |
| 13 | beer | 양배추 닭고기 치즈그라탕 | chicken, cabbage, cheese, milk | 그라탕 | 그라탕, 닭고기, 양배추, 맥주 | pass |
| 14 | beer | 오이 당근 크림딥 | cucumber, carrot, yogurt, garlic | 딥 | 딥, 오이, 당근, 맥주 | pass |
| 15 | beer | 토마토 소시지 달걀컵 | sausage, tomato, egg, cheese | 에어프라이어 | 에어프라이어, 소시지, 토마토, 맥주 | pass |
| 16 | beer | 브로콜리 돼지고기 바삭구이 | pork, broccoli, egg, garlic | 팬구이 | 팬구이, 돼지고기, 브로콜리, 맥주 | pass |
| 17 | beer | 버터 감자 요거트샐러드 | potato, butter, cucumber, yogurt | 샐러드 | 샐러드, 감자, 요거트, 맥주 | pass |
| 18 | beer | 대파 소고기 간장꼬치 | beef, green_onion, onion, garlic | 꼬치구이 | 꼬치구이, 소고기, 대파, 맥주 | pass |
| 19 | beer | 가지 치즈 오픈토스트 | bread, eggplant, cheese, tomato | 오픈샌드 | 오픈샌드, 가지, 치즈, 맥주 | pass |
| 20 | beer | 파프리카 베이컨 양배추볶음 | bacon, pepper, cabbage, onion | 볶음 | 볶음, 베이컨, 파프리카, 맥주 | pass |
| 21 | white_wine | 오이 토마토 생선살 냉채 | fish, cucumber, tomato, onion | 냉채 | 냉채, 생선살, 오이, 화이트와인 | pass |
| 22 | white_wine | 브로콜리 버섯 우유수프 | broccoli, mushroom, milk, onion | 수프 | 수프, 브로콜리, 버섯, 화이트와인 | pass |
| 23 | white_wine | 닭고기 시금치 레몬찜 | chicken, spinach, garlic, onion | 찜 | 찜, 닭고기, 시금치, 화이트와인 | pass |
| 24 | white_wine | 애호박 치즈 달걀프리타타 | zucchini, egg, cheese, milk | 팬구이 | 팬구이, 프리타타, 애호박, 화이트와인 | pass |
| 25 | white_wine | 감자 오이 요거트딥 | potato, cucumber, yogurt, garlic | 딥 | 딥, 감자, 오이, 화이트와인 | pass |
| 26 | white_wine | 토마토 양파 생선살스튜 | fish, tomato, onion, carrot | 스튜 | 스튜, 생선살, 토마토, 화이트와인 | pass |
| 27 | white_wine | 양배추 닭고기 허브말이 | chicken, cabbage, cheese, garlic | 말이구이 | 말이구이, 닭고기, 양배추, 화이트와인 | pass |
| 28 | white_wine | 파프리카 버섯 레몬무침 | pepper, mushroom, cucumber, onion | 무침 | 무침, 파프리카, 버섯, 화이트와인 | pass |
| 29 | white_wine | 상추 달걀 치즈샐러드 | lettuce, egg, cheese, tomato | 샐러드 | 샐러드, 달걀, 상추, 화이트와인 | pass |
| 30 | white_wine | 버터대파 생선살 팬구이 | fish, butter, green_onion, garlic | 팬구이 | 팬구이, 생선살, 대파, 화이트와인 | pass |
| 31 | red_wine | 소고기 양파 버터찜 | beef, onion, butter, garlic | 찜 | 찜, 소고기, 양파, 레드와인 | pass |
| 32 | red_wine | 돼지고기 버섯 토마토스튜 | pork, mushroom, tomato, onion | 스튜 | 스튜, 돼지고기, 버섯, 레드와인 | pass |
| 33 | red_wine | 가지 베이컨 토마토조림 | eggplant, bacon, tomato, garlic | 조림 | 조림, 가지, 베이컨, 레드와인 | pass |
| 34 | red_wine | 브로콜리 소고기 치즈구이 | beef, broccoli, cheese, garlic | 에어프라이어 | 에어프라이어, 소고기, 브로콜리, 레드와인 | pass |
| 35 | red_wine | 파프리카 돼지고기 말이구이 | pork, pepper, cheese, onion | 말이구이 | 말이구이, 돼지고기, 파프리카, 레드와인 | pass |
| 36 | red_wine | 버섯 감자 치즈그라탕 | mushroom, potato, cheese, milk | 그라탕 | 그라탕, 버섯, 감자, 레드와인 | pass |
| 37 | red_wine | 토마토 닭고기 버터구이 | chicken, tomato, butter, garlic | 팬구이 | 팬구이, 닭고기, 토마토, 레드와인 | pass |
| 38 | red_wine | 시금치 소고기 달걀전 | beef, spinach, egg, onion | 전 | 전, 소고기, 시금치, 레드와인 | pass |
| 39 | red_wine | 양배추 베이컨 식초볶음 | cabbage, bacon, onion, garlic | 볶음 | 볶음, 양배추, 베이컨, 레드와인 | pass |
| 40 | red_wine | 상추 토마토 돼지고기샐러드 | pork, lettuce, tomato, onion | 샐러드 | 샐러드, 돼지고기, 토마토, 레드와인 | pass |
| 41 | whisky | 베이컨 양파 버터감자조림 | bacon, onion, potato, butter | 조림 | 조림, 베이컨, 감자, 위스키 | pass |
| 42 | whisky | 소고기 마늘 치즈미니볼 | beef, garlic, cheese, egg | 팬구이 | 팬구이, 미니볼, 소고기, 위스키 | pass |
| 43 | whisky | 소시지 양배추 후추볶음 | sausage, cabbage, onion, garlic | 볶음 | 볶음, 소시지, 양배추, 위스키 | pass |
| 44 | whisky | 버터버섯 닭고기 꼬치구이 | chicken, mushroom, butter, garlic | 꼬치구이 | 꼬치구이, 닭고기, 버섯, 위스키 | pass |
| 45 | whisky | 감자 치즈 베이컨달걀컵 | potato, cheese, bacon, egg | 에어프라이어 | 에어프라이어, 감자, 베이컨, 위스키 | pass |
| 46 | whisky | 돼지고기 토마토 캐러멜양파구이 | pork, tomato, onion, butter | 팬구이 | 팬구이, 돼지고기, 토마토, 위스키 | pass |
| 47 | whisky | 브로콜리 버섯 크림딥 | broccoli, mushroom, milk, cheese | 딥 | 딥, 브로콜리, 버섯, 위스키 | pass |
| 48 | whisky | 파프리카 소시지 치즈그라탕 | sausage, pepper, cheese, milk | 그라탕 | 그라탕, 소시지, 파프리카, 위스키 | pass |
| 49 | whisky | 가지 돼지고기 간장말이 | eggplant, pork, green_onion, garlic | 말이구이 | 말이구이, 가지, 돼지고기, 위스키 | pass |
| 50 | whisky | 버터 생선살 감자해시 | fish, potato, butter, onion | 팬구이 | 팬구이, 해시, 생선살, 위스키 | pass |
| 51 | sparkling_wine | 오이 토마토 요거트핀초 | cucumber, tomato, yogurt, cheese | 샐러드 | 샐러드, 핀초, 오이, 스파클링와인 | pass |
| 52 | sparkling_wine | 상추 닭고기 레몬롤 | lettuce, chicken, cucumber, yogurt | 말이구이 | 말이구이, 상추, 닭고기, 스파클링와인 | pass |
| 53 | sparkling_wine | 당근 애호박 리본무침 | carrot, zucchini, cheese, garlic | 무침 | 무침, 당근, 애호박, 스파클링와인 | pass |
| 54 | sparkling_wine | 브로콜리 달걀 한입전 | broccoli, egg, cheese, green_onion | 전 | 전, 브로콜리, 달걀, 스파클링와인 | pass |
| 55 | sparkling_wine | 파프리카 생선살 양파찜 | fish, pepper, onion, garlic | 찜 | 찜, 생선살, 파프리카, 스파클링와인 | pass |
| 56 | sparkling_wine | 토마토 버섯 치즈보트 | tomato, mushroom, cheese, garlic | 에어프라이어 | 에어프라이어, 토마토, 버섯, 스파클링와인 | pass |
| 57 | sparkling_wine | 감자 오이 머스터드샐러드 | potato, cucumber, egg, yogurt | 샐러드 | 샐러드, 감자, 오이, 스파클링와인 | pass |
| 58 | sparkling_wine | 양배추 베이컨 식초샐러드 | cabbage, bacon, cucumber, onion | 샐러드 | 샐러드, 양배추, 베이컨, 스파클링와인 | pass |
| 59 | sparkling_wine | 시금치 치즈 오픈토스트 | bread, spinach, cheese, tomato | 오픈샌드 | 오픈샌드, 시금치, 치즈, 스파클링와인 | pass |
| 60 | sparkling_wine | 소시지 파프리카 미니꼬치 | sausage, pepper, tomato, cucumber | 꼬치구이 | 꼬치구이, 소시지, 파프리카, 스파클링와인 | pass |
| 61 | sake | 대파 닭고기 맑은찜 | chicken, green_onion, mushroom, garlic | 찜 | 찜, 닭고기, 대파, 사케 | pass |
| 62 | sake | 오이 달걀 겨자냉채 | egg, cucumber, onion, carrot | 냉채 | 냉채, 달걀, 오이, 사케 | pass |
| 63 | sake | 생선살 버섯 간장조림 | fish, mushroom, onion, garlic | 조림 | 조림, 생선살, 버섯, 사케 | pass |
| 64 | sake | 애호박 닭고기 소금구이 | chicken, zucchini, green_onion, garlic | 팬구이 | 팬구이, 닭고기, 애호박, 사케 | pass |
| 65 | sake | 시금치 버섯 달걀탕 | spinach, mushroom, egg, green_onion | 탕 | 탕, 시금치, 버섯, 사케 | pass |
| 66 | sake | 양배추 소고기 간장전골 | beef, cabbage, mushroom, garlic | 전골 | 전골, 소고기, 양배추, 사케 | pass |
| 67 | sake | 토마토 생선살 대파찜 | fish, tomato, green_onion, garlic | 찜 | 찜, 생선살, 토마토, 사케 | pass |
| 68 | sake | 브로콜리 닭고기 간장무침 | chicken, broccoli, green_onion, garlic | 무침 | 무침, 닭고기, 브로콜리, 사케 | pass |
| 69 | sake | 가지 버섯 소이볶음 | eggplant, mushroom, green_onion, garlic | 볶음 | 볶음, 가지, 버섯, 사케 | pass |
| 70 | sake | 감자 대파 달걀말이 | potato, egg, green_onion, milk | 달걀말이 | 달걀말이, 감자, 대파, 사케 | pass |
