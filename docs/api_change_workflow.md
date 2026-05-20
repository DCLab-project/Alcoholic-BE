# API Change Workflow

FE/AI가 새 기능을 요청하면 공유 API 시트에 먼저 계약을 적고, BE는 그 계약을 기준으로 이슈/브랜치/PR을 만듭니다.

## Rules

- main 직접 push/merge 금지
- 새 기능/수정은 GitHub issue 먼저 생성
- branch는 issue 번호를 포함
- Conventional Commits 사용
- 기존 FE 응답 필드는 깨지지 않게 additive change 우선
- breaking change가 필요하면 FE/AI 확인 후 별도 issue로 분리
- 작업 후 test, commit, push, PR

## Sheet Template

| Field | Example |
| --- | --- |
| 기능명 | 추천 카드 즐겨찾기 |
| 화면/플로우 | 추천 결과 카드에서 저장 버튼 클릭 |
| Method | `POST` |
| Path | `/api/v1/favorite-recipes` |
| Request | `{ "liquor": "소주", "name": "돼지고기 대파 소금구이", "reason": "소주와 잘 어울립니다.", "ingredient_yes": ["대파"], "ingredient_no": ["돼지고기"], "recipe": ["1. 대파를 썹니다."], "missing_ingredients": ["돼지고기"] }` |
| Response | `{ "status": "success", "favorite_id": 1 }` |
| FE 영향 | 추천 카드 버튼 상태 추가 |
| AI 영향 | 없음 |
| 기존 호환성 | 기존 추천 응답 변경 없음 |
| BE 테스트 | service test, schema validation |
| Issue | `#00` |
| PR | `#00` |

## Request Checklist

- FE가 실제로 필요한 화면 상태를 적었는가?
- request/response 예시가 JSON으로 재현 가능한가?
- 기존 API를 확장하면 되는지, 새 API가 필요한지 확인했는가?
- 추천 응답이라면 `ingredient_yes`, `ingredient_no`, `missing_ingredients`, `ingredient_details[].status` 유지 여부를 확인했는가?
- AI 입력이라면 label key와 정규화 규칙을 확인했는가?

## BE Implementation Checklist

- issue 생성 또는 기존 issue 연결
- 최신 `origin/main` 기준 branch 생성
- schema/example/docs 업데이트
- service/repository 구현
- 테스트 추가 또는 보강
- `pytest -q -p no:cacheprovider` 통과
- PR 본문에 endpoint, 테스트 결과, 호환성 영향만 짧게 작성

