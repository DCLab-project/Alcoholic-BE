# Database Setup

## Default SQLite

The backend uses SQLite by default for quick local development.

```env
DATABASE_URL=sqlite:///./alcoholic.db
```

## Local MySQL

Use the bundled Docker Compose file when testing the final demonstration-like
database flow.

```powershell
docker compose -f docker-compose.mysql.yml up -d
```

The compose file creates a MySQL 8.4 container named `alcoholic-mysql` and a
database named `alcoholic`.

Use this URL when running the backend against MySQL:

```powershell
$env:DATABASE_URL="mysql+pymysql://root:alcoholic@127.0.0.1:3306/alcoholic?charset=utf8mb4"
```

Create tables and load recommendation seed data:

```powershell
.\.venv\Scripts\python.exe scripts\initialize_database.py
```

The initializer creates the schema and syncs `seeds/recommendations.json` into
the recipe tables. The expected current seed size is 350 recipes: 50 recipes
for each of the 7 liquor categories.

Run the backend:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

Run the hardware-flow smoke test against the running backend:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_hardware_flow.py --base-url http://127.0.0.1:8000
```

Stop MySQL without deleting local data:

```powershell
docker compose -f docker-compose.mysql.yml stop
```

Delete the MySQL data only when you intentionally want a clean database:

```powershell
docker compose -f docker-compose.mysql.yml down -v
```

## Notes

- Keep SQLite as the fast fallback for routine backend unit tests.
- Use MySQL for final integration tests with FE and AI/Jetson/Arduino.
- Do not commit local `.env` files or database files.
- If the AI payload uses legacy ingredient keys such as `leek`, the backend
  should normalize them to the current canonical key `green_onion`.
