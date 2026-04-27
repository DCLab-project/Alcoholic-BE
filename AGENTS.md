# Project Operating Rules

## Workspace
- Canonical workspace: `C:\kdh\vscode\ai-fridge-workspace`
- Main BE repo: `C:\kdh\vscode\ai-fridge-workspace\Alcoholic-BE`
- AI repo: `C:\kdh\vscode\ai-fridge-workspace\Alcoholic-AI`
- Legacy reference only: `C:\kdh\vscode\ai-fridge-workspace\ai-fridge-system-legacy`
- Default work target is the BE repo. Do not edit AI or legacy files unless explicitly requested.

## GitHub Repos
- BE: `DCLab-project/Alcoholic-BE`
- AI: `DCLab-project/Alcoholic-AI`
- Legacy personal repo `andantinow/ai-fridge-system` is reference only.
- Do not mix changes across repos.

## Branches
- Branch prefixes: `feature/...`, `fix/...`, `refactor/...`, `docs/...`
- Do not push directly to `main`.
- Start each new BE feature or fix from the latest `main` when possible.
- Create a short GitHub issue first, then create a focused branch for that issue.
- Recommended branch names:
  - `fix/be-recommendation-refresh-pagination`
  - `fix/be-recipe-seed-quality-gates`
  - `feature/be-cooking-tool-profile`
  - `feature/be-mysql-migration`
  - `feature/be-recommendation-history`
  - `docs/be-api-contract-cleanup`
- After merge, prefer deleting the branch and preserving history through the issue, PR, and commits.

## Commits
- Use Conventional Commits.
- Examples:
  - `feat(be): add manual liquor scan fallback flow`
  - `docs(be): add recipe catalog export for review`
  - `fix(be): normalize Korean ingredient names`
- Keep messages short and practical.

## Issues
- Keep GitHub issues short and practical.
- Title format: `[BE] 작업명` or `[AI] 작업명`
- Body format:
  - `## 배경`
  - `## 작업 내용`
  - `## 완료 조건`
- After finishing work, leave a short completion comment and close the issue.

## Language And Docs
- README and Swagger descriptions stay Korean.
- API paths, schema keys, and internal keys stay English.
- Structure in English, explanation in Korean.

## Local Run
- BE run command:
  - `.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000`
- Previous LAN test endpoints:
  - BE: `http://192.168.50.123:8000`
  - FE: `http://192.168.50.184:5174`

## Current BE Scope
- Main implemented APIs:
  - `GET /api/v1/inventory`
  - `POST /api/v1/inventory/bulk`
  - `PATCH /api/v1/inventory/quantity`
  - `GET /api/v1/stream/ingredients`
  - `GET /api/v1/stream/liquor`
  - `GET /api/v1/stream/recommendations`
  - `POST /api/v1/recognitions/ingredients`
  - `POST /api/v1/recognitions/liquor`
  - `POST /api/v1/scan/liquor/start`
  - `GET /api/v1/recommendations`
- Recommendation docs/data:
  - `docs/recommendation_knowledge.md`
  - `docs/recipe_catalog.md`
  - `seeds/recommendations.json`

## Product Direction
- Existing seed data is structure baseline, not final content quality.
- Recommendation content should be service-ready, user-friendly Korean.
- Do not expose undetected liquor substyles to users when the system only detects top-level liquor categories.
