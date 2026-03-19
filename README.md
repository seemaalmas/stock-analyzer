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

## Docker & Release

### Build and run locally

```bash
# Build the image
docker build -t stock-analyzer:dev .

# Run (Streamlit on port 8080)
docker run -p 8080:8080 stock-analyzer:dev

# With database env vars
docker run -p 8080:8080 \
  -e user=postgres.abc -e password=secret \
  -e host=db.example.com -e port=6543 -e dbname=postgres \
  stock-analyzer:dev

# Quick health check
curl -I http://localhost:8080
```

**Expected output** from `curl -I`:

```
HTTP/1.1 200 OK
```

### Automated smoke test

```bash
./scripts/smoke_local.sh
```

This builds the image, starts a container, waits for Streamlit to be ready,
curls the homepage, then tears down the container automatically.

**Windows alternative** (PowerShell):

```powershell
docker build -t stock-analyzer:dev .
docker run -d --name sa-test -p 8080:8080 stock-analyzer:dev
Start-Sleep 15
Invoke-WebRequest http://localhost:8080 -UseBasicParsing | Select-Object StatusCode
docker rm -f sa-test
```

### Creating a release

Tag a commit and push to trigger the release workflow:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This builds and pushes to GHCR:
- `ghcr.io/seemaalmas/stock-analyzer:0.1.0`
- `ghcr.io/seemaalmas/stock-analyzer:latest`

### Pull and run the GHCR image

```bash
docker pull ghcr.io/seemaalmas/stock-analyzer:latest
docker run -p 8080:8080 ghcr.io/seemaalmas/stock-analyzer:latest
```

> **Note on GHCR visibility:** After the first publish, the package defaults
> to *private*. Go to the package settings on GitHub and set visibility to
> *public* if you want unauthenticated pulls.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `port already in use` | Stop the process using port 8080: `lsof -ti:8080 \| xargs kill` or choose another port: `-p 9090:8080` |
| `ModuleNotFoundError` | Ensure `requirements.txt` lists the missing module; rebuild the image |
| Streamlit not reachable | Check container logs: `docker logs <container>`; verify `--server.address=0.0.0.0` is set |
| `docker: permission denied` | Add your user to the docker group: `sudo usermod -aG docker $USER` then re-login |
| GHCR push fails (403) | Ensure the workflow has `packages: write` permission and the package visibility is set correctly |

## How to Run

```bash
pip install -r requirements.txt
streamlit run main.py
```
