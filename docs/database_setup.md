# Database Setup

## Default Local Database

The default database is SQLite:

```env
DATABASE_URL=sqlite:///./alcoholic.db
```

This keeps local FE smoke tests simple.

## MySQL

Use PyMySQL through SQLAlchemy:

```env
DATABASE_URL=mysql+pymysql://root:alcoholic@127.0.0.1:3306/alcoholic?charset=utf8mb4
DATABASE_POOL_RECYCLE_SECONDS=1800
```

Short `mysql://` URLs are accepted and normalized to `mysql+pymysql://`.
If a MySQL URL omits `charset`, the app appends `charset=utf8mb4`.

Start the local MySQL container:

```powershell
docker compose -f docker-compose.mysql.yml up -d
```

If `alcoholic-mysql` was already created manually with `docker run`, either keep
using that container or remove it before switching to compose:

```powershell
docker stop alcoholic-mysql
docker rm alcoholic-mysql
docker compose -f docker-compose.mysql.yml up -d
```

Stop it without deleting data:

```powershell
docker compose -f docker-compose.mysql.yml stop
```

Create the schema and load recommendation seeds:

```powershell
.\.venv\Scripts\python.exe scripts\initialize_database.py
```

The initializer runs `Base.metadata.create_all` and then syncs
`seeds/recommendations.json` into the recipe tables.

Run the app against MySQL:

```powershell
$env:DATABASE_URL="mysql+pymysql://root:alcoholic@127.0.0.1:3306/alcoholic?charset=utf8mb4"
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

Smoke-check the recommendation API:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/recommendations?liquor=beer&refresh=false"
```

The response should contain three recommendations and each item should include
`ingredient_yes`, `ingredient_no`, `missing_ingredients`, and
`ingredient_details[].status`.

Run the automated tests before pushing:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

## Notes

- Keep SQLite for automated tests unless a test explicitly needs MySQL.
- Do not commit local `.env` files or database files.
- The compose file creates the `alcoholic` database automatically.
- Removing the `alcoholic_mysql_data` Docker volume deletes local MySQL data.
