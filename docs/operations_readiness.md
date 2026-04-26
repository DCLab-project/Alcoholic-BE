# 운영 준비 체크리스트

이 문서는 FE 연동 확인 이후 BE를 실제 서비스 형태로 올리기 전에 확인할 내용을 정리합니다.

## 현재 상태

- 기본 API 계약은 유지합니다: `inventory`, `stream`, `scan`, `recommendations`.
- 추천은 실시간 LLM 생성이 아니라 검수된 seed 레시피 DB에서 현재 재고와 주류를 기준으로 고릅니다.
- 현재 seed는 7개 주류 x 30개, 총 210개입니다.
- 현재 로컬 기본 DB는 SQLite `alcoholic.db`입니다.
- MySQL 전환을 위해 `DATABASE_URL`만 바꾸면 같은 모델과 seed 적재 흐름을 사용할 수 있게 준비합니다.
- 추천 응답 지연은 기본값 `RECOMMENDATION_RESPONSE_DELAY_SECONDS=0`으로 두고, FE 로딩 UI 테스트가 필요할 때만 조절합니다.

## 로컬 가상환경 정리

서버가 켜져 있으면 `.venv` 안의 `python.exe`나 `uvicorn.exe`가 잠겨서 삭제가 실패할 수 있습니다. 먼저 실행 중인 BE 서버를 끄고 진행하세요.

```powershell
cd C:\kdh\vscode\ai-fridge-workspace\Alcoholic-BE
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

서버 실행은 아래 명령을 기본으로 사용합니다.

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

로컬 FE와 같은 와이파이에서 테스트할 때는 `http://내PC_IP:8000/docs`로 Swagger를 확인합니다.

## DB 초기화

SQLite와 MySQL 모두 같은 초기화 스크립트를 사용합니다.

```powershell
.\.venv\Scripts\python.exe scripts\initialize_database.py
```

이 스크립트가 하는 일은 단순합니다.

- 현재 `DATABASE_URL`에 연결합니다.
- 필요한 테이블을 생성합니다.
- `seeds/recommendations.json`의 추천 레시피를 DB에 적재합니다.
- 적재된 recipe 수와 recipe ingredient 수를 출력합니다.

## MySQL 전환 순서

SQLite 기반 FE smoke test가 끝난 뒤 MySQL로 전환하는 것을 권장합니다. FE 연결이 불안정한 상태에서 DB까지 바꾸면 문제 원인을 찾기 어려워집니다.

1. MySQL 서버를 준비합니다.
2. `alcoholic` 데이터베이스를 생성합니다.
3. 문자셋은 `utf8mb4`를 사용합니다.
4. `.env`의 `DATABASE_URL`을 MySQL 주소로 바꿉니다.

예시:

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/alcoholic?charset=utf8mb4
```

5. DB 초기화 스크립트를 실행합니다.

```powershell
.\.venv\Scripts\python.exe scripts\initialize_database.py
```

6. 서버를 실행하고 아래를 확인합니다.

```text
GET /health
GET /api/v1/inventory
GET /api/v1/recommendations?liquor=소주&refresh=false
```

문제가 생기면 `.env`를 다시 아래처럼 돌리면 SQLite로 즉시 복귀할 수 있습니다.

```env
DATABASE_URL=sqlite:///./alcoholic.db
```

## Seed 확장 파이프라인

지금 seed는 데모와 구조 검증에는 충분하지만, 강한 서비스 DB로 가려면 주류별 후보를 더 늘리고 검수 상태를 남겨야 합니다.

권장 순서는 아래와 같습니다.

1. GPT Pro 또는 Gemini로 특정 주류 1개에 대해 후보를 생성합니다.
2. 기존 seed와 이름/핵심 조합 중복을 제거합니다.
3. 내부 key, 한글 display name, pantry item, step, pairing 문장을 검수합니다.
4. `seeds/recommendations.json`에 반영합니다.
5. 문장 톤과 사용자 노출 문구를 정리합니다.

```powershell
.\.venv\Scripts\python.exe scripts\polish_recommendation_seeds.py
.\.venv\Scripts\python.exe scripts\export_recipe_catalog.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\initialize_database.py
```

## Seed 선정 기준

추천 seed는 “새 레시피를 즉석 생성하기 위한 예시”가 아니라 “서비스가 직접 추천할 검수된 후보군”입니다.

- 술과 실제로 잘 맞는가
- 한국 1~2인 가구가 집에서 만들 수 있는가
- 내부 식재료 key로 매칭 가능한가
- 이름만 다른 중복 레시피가 아닌가
- 설명이 사용자에게 바로 노출되어도 어색하지 않은가
- recipe step이 초보자도 따라 할 만큼 구체적인가

추천 API는 이 seed 후보군 중에서 현재 냉장고 재고와 가장 잘 맞는 3개를 고릅니다.

## 다음 의사결정

- FE smoke test가 먼저입니다.
- 그 다음 MySQL 전환을 진행합니다.
- seed 확장은 한 번에 700개를 넣기보다, 주류별로 30개에서 50개, 80개, 100개 순서로 검수하며 늘리는 편이 안전합니다.
