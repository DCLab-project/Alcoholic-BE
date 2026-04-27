# Seed expansion wave 1 plan

- Base branch: `feature/be-expand-recipe-seeds-70-20`
- Working branch: `feature/be-seed-expansion-wave-1-23`
- Issue: `#23`
- Goal: expand recommendation seeds from 280 to 350, adding 10 seeds per liquor.
- Index basis: existing `seeds/recommendations.json` names, liquor, core ingredient combinations, method tags, recipe step flow, pantry seasoning/sauce signatures, and cooking tool/heat patterns.
- Gate result: 70 passed candidates; 0 blocking name/core/method/tag/flow risks after replacements.
- Replacement handling: risky initial candidates were replaced before JSON application; no rejected candidate is applied to the seed file.

## 소주 (soju)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 양파 돼지고기 식초볶음 | `pork, onion, cabbage, garlic` | 볶음 / vinegar / pan / 중강불 | `볶음, 돼지고기, 양파, 소주` | 통과 |
| 2 | 대파 닭고기 간장찜 | `chicken, green_onion, potato, garlic` | 찜 / soy / pot / 중불 | `찜, 닭고기, 대파, 소주` | 통과 |
| 3 | 상추 소고기 초무침 | `beef, lettuce, cucumber, garlic` | 무침 / vinegar / pan_bowl / 중불 | `무침, 소고기, 상추, 소주` | 통과 |
| 4 | 감자 버섯 달걀탕 | `egg, potato, mushroom, green_onion` | 탕 / salt / pot / 중불 | `탕, 감자, 달걀, 소주` | 통과 |
| 5 | 파프리카 소시지 양배추볶음 | `sausage, pepper, cabbage, onion` | 볶음 / ketchup / pan / 중강불 | `볶음, 소시지, 파프리카, 소주` | 통과 |
| 6 | 가지 돼지고기 달걀전 | `eggplant, pork, egg, garlic` | 전 / pancake / pan / 중불 | `전, 가지, 돼지고기, 소주` | 통과 |
| 7 | 토마토 생선살 대파조림 | `fish, tomato, green_onion, onion` | 조림 / soy / pot / 약불 | `조림, 생선살, 토마토, 소주` | 통과 |
| 8 | 브로콜리 베이컨 달걀찜 | `broccoli, bacon, egg, milk` | 달걀찜 / salt / pot / 약불 | `달걀찜, 브로콜리, 베이컨, 소주` | 통과 |
| 9 | 애호박 소고기 구이 | `zucchini, beef, onion, garlic` | 구이 / herb / pan / 중불 | `구이, 애호박, 소고기, 소주` | 통과 |
| 10 | 양배추 치즈 달걀말이 | `cabbage, cheese, egg, milk` | 달걀말이 / salt / pan / 약불 | `달걀말이, 양배추, 치즈, 소주` | 통과 |

## 맥주 (beer)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 감자 닭고기 머스터드볶음 | `chicken, potato, onion, garlic` | 볶음 / mustard / pan / 중불 | `볶음, 감자, 닭고기, 맥주` | 통과 |
| 2 | 양배추 베이컨 감자전 | `cabbage, bacon, potato, egg` | 전 / pancake / pan / 중불 | `전, 양배추, 베이컨, 맥주` | 통과 |
| 3 | 브로콜리 소시지 우유수프 | `broccoli, sausage, milk, onion` | 수프 / cream / pot / 약불 | `수프, 브로콜리, 소시지, 맥주` | 통과 |
| 4 | 버섯 돼지고기 감자조림 | `mushroom, pork, potato, green_onion` | 조림 / soy / pot / 약불 | `조림, 버섯, 돼지고기, 맥주` | 통과 |
| 5 | 소시지 파프리카 치즈오픈샌드 | `bread, sausage, cheese, pepper` | 오픈샌드 / mustard / pan / 약불 | `오픈샌드, 소시지, 파프리카, 맥주` | 통과 |
| 6 | 오이 당근 머스터드샐러드 | `cucumber, carrot, lettuce, yogurt` | 샐러드 / mustard / bowl / 없음 | `샐러드, 오이, 당근, 맥주` | 통과 |
| 7 | 닭고기 파프리카 전분구이 | `chicken, pepper, egg, garlic` | 구이 / starch / pan / 중불 | `구이, 닭고기, 파프리카, 맥주` | 통과 |
| 8 | 가지 치즈그라탕 | `eggplant, cheese, milk, onion` | 그라탕 / cream / pan_lid / 약불 | `그라탕, 가지, 치즈, 맥주` | 통과 |
| 9 | 대파 소고기 버터볶음 | `beef, green_onion, butter, garlic` | 볶음 / butter_soy / pan / 중불 | `볶음, 소고기, 대파, 맥주` | 통과 |
| 10 | 상추 소고기 간장샐러드 | `beef, lettuce, tomato, garlic` | 샐러드 / soy_vinegar / pan_bowl / 중불 | `샐러드, 상추, 소고기, 맥주` | 통과 |

## 화이트와인 (white_wine)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 생선살 오이 요거트무침 | `fish, cucumber, yogurt, onion` | 무침 / yogurt / pan_bowl / 중불 | `무침, 생선살, 오이, 화이트와인` | 통과 |
| 2 | 브로콜리 감자 우유수프 | `broccoli, potato, milk, onion` | 수프 / cream / pot / 약불 | `수프, 브로콜리, 감자, 화이트와인` | 통과 |
| 3 | 닭고기 토마토 찜 | `chicken, tomato, onion, garlic` | 찜 / herb / pot / 중불 | `찜, 닭고기, 토마토, 화이트와인` | 통과 |
| 4 | 파프리카 치즈달걀찜 | `pepper, cheese, egg, milk` | 달걀찜 / salt / pot / 약불 | `달걀찜, 파프리카, 치즈, 화이트와인` | 통과 |
| 5 | 상추 버섯 식초샐러드 | `lettuce, mushroom, cucumber, onion` | 샐러드 / vinegar / pan_bowl / 중불 | `샐러드, 상추, 버섯, 화이트와인` | 통과 |
| 6 | 애호박 생선살 구이 | `zucchini, fish, butter, garlic` | 구이 / butter_salt / pan / 중불 | `구이, 애호박, 생선살, 화이트와인` | 통과 |
| 7 | 양배추 소고기 냉채 | `cabbage, beef, cucumber, onion` | 냉채 / vinegar / pan_bowl / 중불 | `냉채, 양배추, 소고기, 화이트와인` | 통과 |
| 8 | 감자 브로콜리 치즈그라탕 | `potato, broccoli, cheese, milk` | 그라탕 / cream / pan_lid / 약불 | `그라탕, 감자, 브로콜리, 화이트와인` | 통과 |
| 9 | 시금치 닭고기 달걀전 | `spinach, chicken, egg, green_onion` | 전 / pancake / pan / 중불 | `전, 시금치, 닭고기, 화이트와인` | 통과 |
| 10 | 토마토 버섯 스튜 | `tomato, mushroom, carrot, onion` | 스튜 / tomato_salt / pot / 약불 | `스튜, 토마토, 버섯, 화이트와인` | 통과 |

## 레드와인 (red_wine)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 소고기 버섯 토마토찜 | `beef, mushroom, tomato, butter` | 찜 / butter_soy / pot / 중불 | `찜, 소고기, 버섯, 레드와인` | 통과 |
| 2 | 돼지고기 감자 토마토조림 | `pork, potato, tomato, onion` | 조림 / tomato_soy / pot / 약불 | `조림, 돼지고기, 감자, 레드와인` | 통과 |
| 3 | 가지 치즈구이 | `eggplant, cheese, butter, garlic` | 구이 / herb / pan / 중불 | `구이, 가지, 치즈, 레드와인` | 통과 |
| 4 | 닭고기 파프리카 스튜 | `chicken, pepper, tomato, onion` | 스튜 / tomato_salt / pot / 약불 | `스튜, 닭고기, 파프리카, 레드와인` | 통과 |
| 5 | 베이컨 양배추 치즈말이 | `bacon, cabbage, cheese, garlic` | 말이구이 / herb / pan / 중불 | `말이구이, 베이컨, 양배추, 레드와인` | 통과 |
| 6 | 소시지 버섯 그라탕 | `sausage, mushroom, cheese, milk` | 그라탕 / cream / pan_lid / 약불 | `그라탕, 소시지, 버섯, 레드와인` | 통과 |
| 7 | 브로콜리 소고기 달걀전 | `beef, broccoli, egg, onion` | 전 / pancake / pan / 중불 | `전, 브로콜리, 소고기, 레드와인` | 통과 |
| 8 | 토마토 치즈 버터구이 | `tomato, cheese, butter, garlic` | 구이 / butter_salt / pan / 중불 | `구이, 토마토, 치즈, 레드와인` | 통과 |
| 9 | 감자 소고기 간장찜 | `beef, potato, carrot, onion` | 찜 / soy / pot / 중불 | `찜, 감자, 소고기, 레드와인` | 통과 |
| 10 | 감자 버섯 우유수프 | `potato, mushroom, milk, onion` | 수프 / cream / pot / 약불 | `수프, 감자, 버섯, 레드와인` | 통과 |

## 위스키 (whisky)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 돼지고기 감자 버터구이 | `pork, potato, butter, garlic` | 구이 / butter_salt / pan / 중불 | `구이, 돼지고기, 감자, 위스키` | 통과 |
| 2 | 소시지 양파 치즈볶음 | `sausage, onion, cheese, garlic` | 볶음 / ketchup / pan / 중불 | `볶음, 소시지, 양파, 위스키` | 통과 |
| 3 | 베이컨 버섯 달걀말이 | `bacon, mushroom, egg, milk` | 달걀말이 / salt / pan / 약불 | `달걀말이, 베이컨, 버섯, 위스키` | 통과 |
| 4 | 닭고기 양배추 조림 | `chicken, cabbage, onion, butter` | 조림 / butter_soy / pot / 약불 | `조림, 닭고기, 양배추, 위스키` | 통과 |
| 5 | 감자 소고기 미니볼 | `beef, potato, egg, onion` | 팬구이 / starch / pan / 중불 | `팬구이, 미니볼, 소고기, 위스키` | 통과 |
| 6 | 브로콜리 소시지 버터찜 | `broccoli, sausage, butter, garlic` | 찜 / butter_salt / pot / 중불 | `찜, 브로콜리, 소시지, 위스키` | 통과 |
| 7 | 토마토 치즈그라탕 | `tomato, cheese, milk, onion` | 그라탕 / cream / pan_lid / 약불 | `그라탕, 토마토, 치즈, 위스키` | 통과 |
| 8 | 양배추 베이컨 달걀전 | `bacon, cabbage, egg, garlic` | 전 / pancake / pan / 중불 | `전, 양배추, 베이컨, 위스키` | 통과 |
| 9 | 가지 돼지고기 볶음 | `eggplant, pork, onion, garlic` | 볶음 / soy / pan / 중강불 | `볶음, 가지, 돼지고기, 위스키` | 통과 |
| 10 | 버섯 생선살 간장조림 | `fish, mushroom, onion, green_onion` | 조림 / soy / pot / 약불 | `조림, 버섯, 생선살, 위스키` | 통과 |

## 스파클링와인 (sparkling_wine)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 오이 치즈샐러드 | `cucumber, cheese, lettuce, tomato` | 샐러드 / vinegar / bowl / 없음 | `샐러드, 오이, 치즈, 스파클링와인` | 통과 |
| 2 | 당근 달걀 미니전 | `carrot, egg, green_onion, milk` | 전 / pancake / pan / 중불 | `전, 당근, 달걀, 스파클링와인` | 통과 |
| 3 | 파프리카 생선살 보트 | `fish, pepper, cheese, onion` | 에어프라이어 / salt / air_fryer / 중불 | `에어프라이어, 파프리카, 생선살, 스파클링와인` | 통과 |
| 4 | 브로콜리 요거트무침 | `broccoli, yogurt, carrot, garlic` | 무침 / yogurt / pot_bowl / 중불 | `무침, 브로콜리, 요거트, 스파클링와인` | 통과 |
| 5 | 파프리카 양파 달걀찜 | `pepper, egg, cheese, onion` | 달걀찜 / salt / pot / 약불 | `달걀찜, 파프리카, 달걀, 스파클링와인` | 통과 |
| 6 | 감자 생선살 구이 | `fish, potato, butter, garlic` | 구이 / butter_salt / pan / 중불 | `구이, 감자, 생선살, 스파클링와인` | 통과 |
| 7 | 양배추 소시지 케첩볶음 | `sausage, cabbage, egg, green_onion` | 볶음 / ketchup / pan / 중강불 | `볶음, 양배추, 소시지, 스파클링와인` | 통과 |
| 8 | 토마토 버섯 오픈샌드 | `bread, tomato, mushroom, cheese` | 오픈샌드 / herb / pan / 약불 | `오픈샌드, 토마토, 버섯, 스파클링와인` | 통과 |
| 9 | 시금치 닭고기 오픈샌드 | `chicken, spinach, bread, cheese` | 오픈샌드 / mustard / pan / 약불 | `오픈샌드, 시금치, 닭고기, 스파클링와인` | 통과 |
| 10 | 애호박 베이컨 말이구이 | `zucchini, bacon, egg, garlic` | 말이구이 / soy / pan / 중불 | `말이구이, 애호박, 베이컨, 스파클링와인` | 통과 |

## 사케 (sake)

| # | name | core_keys | method | tags | duplicate risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | 애호박 생선살 대파찜 | `fish, green_onion, zucchini, garlic` | 찜 / salt / pot / 중불 | `찜, 생선살, 애호박, 사케` | 통과 |
| 2 | 닭고기 감자 전골 | `chicken, potato, mushroom, green_onion` | 전골 / soy / pot / 중불 | `전골, 닭고기, 감자, 사케` | 통과 |
| 3 | 오이 버섯 간장무침 | `cucumber, mushroom, green_onion, garlic` | 무침 / soy_vinegar / pan_bowl / 중불 | `무침, 오이, 버섯, 사케` | 통과 |
| 4 | 돼지고기 양파 달걀볶음 | `pork, onion, egg, green_onion` | 볶음 / soy / pan / 중불 | `볶음, 돼지고기, 달걀, 사케` | 통과 |
| 5 | 브로콜리 생선살 맑은탕 | `fish, broccoli, green_onion, garlic` | 탕 / salt / pot / 중불 | `탕, 브로콜리, 생선살, 사케` | 통과 |
| 6 | 가지 소고기 조림 | `beef, eggplant, green_onion, garlic` | 조림 / soy / pot / 약불 | `조림, 가지, 소고기, 사케` | 통과 |
| 7 | 시금치 우유 달걀찜 | `spinach, egg, milk, green_onion` | 달걀찜 / salt / pot / 약불 | `달걀찜, 시금치, 달걀, 사케` | 통과 |
| 8 | 양배추 버섯 소금구이 | `cabbage, mushroom, butter, garlic` | 구이 / butter_salt / pan / 중불 | `구이, 양배추, 버섯, 사케` | 통과 |
| 9 | 토마토 닭고기 간장찜 | `chicken, tomato, green_onion, onion` | 찜 / soy / pot / 중불 | `찜, 토마토, 닭고기, 사케` | 통과 |
| 10 | 감자 소시지 달걀전 | `potato, sausage, egg, green_onion` | 전 / pancake / pan / 중불 | `전, 감자, 소시지, 사케` | 통과 |
