# ⚡ JobFlow — Resilient Job Listing Ingestion Platform

JobFlow is a resilient, modular, and fault-tolerant job listing ingestion engine built with **Python**, **FastAPI**, **SQLAlchemy**, and **Pydantic**. 

It automatically fetches, normalizes, deduplicates, and persists job postings from external feeds with built-in pacing, exponential backoff retries, HTTP 429 rate limit handling, and automatic failover to a controlled sandbox source.

---

## 🏛️ System Architecture

```text
               +-----------------------------------+
               |       JobFlow Web Dashboard       |
               |        (http://127.0.0.1:8000)    |
               +-----------------+-----------------+
                                 |
                                 v
               +-----------------+-----------------+
               |         FastAPI API Engine        |
               +-----------------+-----------------+
                                 |
                        SourceManager Router
                                 |
             +-------------------+-------------------+
             |                                       |
             v (Primary)                             v (Fallback)
+-------------------------+             +-------------------------+
|   We Work Remotely RSS  |             |  JobFlow Sandbox XML    |
| (15s Timeout, Pacing,   |             |  (Controlled Fallback   |
| Exponential Backoff)    |             |   Feed)                 |
+------------+------------+             +------------+------------+
             |                                       |
             +-------------------+-------------------+
                                 |
                                 v
                    +------------+------------+
                    |    Data Normalization   |
                    | (Title, Company, Date,  |
                    |  Clean HTML, Location)  |
                    +------------+------------+
                                 |
                                 v
                    +------------+------------+
                    | IngestionService        |
                    | (SAVEPOINT Isolation &  |
                    |  URL Deduplication)     |
                    +------------+------------+
                                 |
                                 v
                    +------------+------------+
                    |   SQLite Database DB    |
                    |     (jobflow.db)        |
                    +-------------------------+
```

---

## ✨ Key Features & Resilience Mechanisms

* **Modular Source Adapters:** Clean interface isolation via abstract `JobSource` contract.
* **Data Normalization:** Parses company names from `Company: Title` strings, strips HTML tags from descriptions, and converts RFC 822 timestamps to UTC `datetime`.
* **Database Deduplication:** Enforces unique URL constraints and uses SQLAlchemy `SAVEPOINT` (`db.begin_nested()`) isolation so duplicate listings do not cancel batch operations.
* **Request Pacing:** Enforces a 5.0-second minimum request interval (`time.monotonic()`) to respect upstream rate limits.
* **Exponential Backoff & Retries:** Powered by `tenacity` (`3 attempts`, `1s -> 2s -> 4s`, max 8s wait) for transient network timeouts and HTTP 5xx/429 errors.
* **HTTP 429 & Retry-After Handling:** Reads server `Retry-After` headers and pauses before retrying.
* **Automatic Failover:** Automatically routes ingestion to a controlled XML sandbox fallback feed if the primary RSS feed fails or returns empty data.
* **Interactive Live Dashboard:** Modern dark-mode web dashboard with real-time stats, one-click manual ingestion trigger, and health monitoring.

---

## 📁 Project Directory Structure

```text
jobflow/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── jobs.py          # Job list, count, detail & ingest endpoints
│   │   │   └── health.py        # Live source health & telemetry endpoint
│   │   ├── models/
│   │   │   ├── job.py           # Dataclass internal representation
│   │   │   └── job_db.py        # SQLAlchemy JobDB table definition
│   │   ├── schemas/
│   │   │   └── job.py           # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── ingestion.py     # Ingestion & SAVEPOINT deduplication service
│   │   │   ├── source_manager.py# Primary/fallback failover orchestrator
│   │   │   └── logger.py        # Structured logging configuration
│   │   ├── sources/
│   │   │   ├── base.py          # Abstract JobSource base class
│   │   │   ├── rss_source.py    # Primary WWR RSS feed adapter
│   │   │   └── fallback_source.py # Controlled XML sandbox fallback adapter
│   │   ├── static/
│   │   │   └── dashboard.html   # Web dashboard UI
│   │   ├── config.py            # Environment & app settings
│   │   ├── database.py          # SQLAlchemy engine & session maker
│   │   └── main.py              # FastAPI application entrypoint
│   ├── data/
│   │   └── fallback_jobs.xml    # Sandbox XML fallback feed
│   ├── scripts/
│   │   ├── inspect_feed.py      # RSS feed inspection tool
│   │   └── test_fallback.py     # Fallback source test script
│   ├── tests/
│   │   ├── test_api.py          # API route unit tests
│   │   ├── test_fallback.py     # Failover unit tests
│   │   ├── test_ingestion.py    # Deduplication & DB unit tests
│   │   ├── test_main.py         # Main app route tests
│   │   └── test_rss_source.py   # Title/Date parsing unit tests
│   ├── Dockerfile               # Container build file
│   ├── requirements.txt         # Python dependencies
│   └── jobflow.db               # SQLite database file
├── DECISIONS.md                 # Architecture Decision Records (ADR)
├── README.md                    # System documentation
└── .gitignore                   # Version control exclusion rules
```

---

## 🚀 Quick Start Guide

### 1. Local Environment Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/jobflow.git
cd jobflow/backend

# Create and activate virtual environment
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn app.main:app --reload
```

* **Interactive Web Dashboard:** `http://127.0.0.1:8000/dashboard`
* **Swagger API Documentation:** `http://127.0.0.1:8000/docs`
* **Root API:** `http://127.0.0.1:8000/`

---

### 2. Docker Container Setup

```bash
cd backend
docker build -t jobflow-backend .
docker run -p 8000:8000 jobflow-backend
```

---

## ⚙️ Environment Variables (`backend/.env`)

```env
JOB_FEED_URL=https://weworkremotely.com/remote-jobs.rss
```

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service root & system links |
| `GET` | `/health` | Application health check |
| `GET` | `/dashboard` | Interactive Web Dashboard UI |
| `GET` | `/jobs/` | List jobs with pagination (`limit`, `offset`) |
| `GET` | `/jobs/count` | Total count of persisted jobs in database |
| `GET` | `/jobs/{job_id}` | Fetch individual job details by ID |
| `POST` | `/jobs/ingest` | Trigger job ingestion pipeline (Primary → Fallback) |
| `GET` | `/sources/health` | Live source health status & ingestion telemetry |

---

## 🧪 Running Automated Unit Tests

Execute the complete 14-test suite using `pytest`:

```bash
cd backend
python -m pytest
```

```text
================ 14 passed in 0.89s ================
```

---

## 🛡️ Controlled Failure & Failover Demo

You can test automatic failover in a controlled demo environment:

1. Edit `backend/.env` to point to an invalid domain:
   ```env
   JOB_FEED_URL=https://invalid-jobflow-test-source.example/rss
   ```
2. Trigger ingestion:
   ```bash
   curl -X POST http://127.0.0.1:8000/jobs/ingest
   ```
3. **Observed Behavior:**
   - Primary RSS fails 3 times after exponential backoff retries.
   - `SourceManager` catches the exception and logs diagnostic error.
   - Ingestion seamlessly switches to `FallbackRSSJobSource`.
   - Response payload:
     ```json
     {
       "fetched": 2,
       "inserted": 2,
       "duplicates": 0,
       "failed": 0,
       "source": "fallback"
     }
     ```
4. Restore `backend/.env` back to `https://weworkremotely.com/remote-jobs.rss`.
