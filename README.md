# Stock Trend Analyzer

A Streamlit app to analyze NSE stock trends (Daily, Weekly, Monthly) based on Open/Close data and RSI indicators.

## Features
- Daily/Weekly/Monthly trend selector
- Date-based stock trend detection
- RSI and volume average
- FastAPI API layer (`/health`, `/health/db`, `POST /signals/score`)
- Built using yfinance, ta, pandas, FastAPI

## Local Setup

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd stock-analyzer

# 2. Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install runtime + dev dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 4. (Optional) Copy and fill in environment variables for DB access
cp .env.example .env   # then edit .env with your credentials

# 5. Run the Streamlit dashboard
streamlit run main.py

# 6. Run the API server
PYTHONPATH=. uvicorn api.app:app --reload --port 8000

# 7. Run linter + tests (same as CI)
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests_spcore/ -v
```

## Production Environment Variables

The following env vars are required for database connectivity in production:

| Variable | Description | Example |
|----------|-------------|---------|
| `user` | PostgreSQL username | `postgres.abcxyz` |
| `password` | PostgreSQL password | *(secret)* |
| `host` | Database host | `aws-1-ap-south-1.pooler.supabase.com` |
| `port` | Database port | `6543` |
| `dbname` | Database name | `postgres` |

> **Note:** Never commit `.env` or credentials to the repository.
> CI runs without any secrets — only the `tests_spcore/` suite is executed,
> which requires no database or external services.

## Migration Strategy

This project uses Supabase-hosted PostgreSQL. Schema changes follow this process:

1. **Define** the migration as a SQL file in `migrations/` (create the directory when first needed).
2. **Review** the SQL in a PR — the CI pipeline validates code quality but does not run migrations.
3. **Apply** manually via `psql` or the Supabase SQL editor against the staging/production database:
   ```bash
   psql "$DATABASE_URL" -f migrations/001_add_new_table.sql
   ```
4. **Verify** by running the integration tests in `tests/` against the updated database.

> Future improvement: adopt a migration tool (e.g., Alembic) for automated, versioned migrations.

## How to Run

```bash
pip install -r requirements.txt
streamlit run main.py
```
