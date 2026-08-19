# ⚡ JobFlow — Resilient Job Listing Ingestion Platform

JobFlow is a resilient, modular, and fault-tolerant job listing ingestion engine built with **Python**, **FastAPI**, **SQLAlchemy**, and **Pydantic**. 

It automatically fetches, normalizes, deduplicates, and persists job postings from external feeds with built-in pacing, exponential backoff retries, HTTP 429 rate limit handling, and automatic failover to a controlled sandbox source.

---

## 🌐 Live Production Deployment

* **Live Web Dashboard:** [https://jobflow-suia.onrender.com/dashboard](https://jobflow-suia.onrender.com/dashboard)
* **Live API Base URL:** [https://jobflow-suia.onrender.com](https://jobflow-suia.onrender.com)
* **Swagger API Documentation:** [https://jobflow-suia.onrender.com/docs](https://jobflow-suia.onrender.com/docs)
* **GitHub Repository:** [https://github.com/vansharora156/jobflow](https://github.com/vansharora156/jobflow)

---

## 🏛️ System Architecture & Data Flow

```text
                 🌐 User / Client
                        │
                        ▼
             ┌─────────────────────┐
             │  JobFlow Dashboard  │
             └──────────┬──────────┘
                        │ HTTPS
                        ▼
             ┌─────────────────────┐
             │  FastAPI API Engine │
             └──────────┬──────────┘
                        │
              SourceManager Router
                        │
          ┌─────────────┴─────────────┐
          │                           │
          v (Primary)                 v (Fallback)
+-------------------+       +-------------------+
|  WWR RSS Source   |       | JobFlow Sandbox   |
| (15s Timeout,     |       | XML Fallback Feed |
| Backoff & Pacing) |       +---------+---------+
+---------+---------+                 |
          |                           |
          └─────────────┬─────────────┘
                        │
                        v
          +---------------------------+
          |     Data Normalization    |
          |  (Company: Title Split,   |
          |   Clean HTML, Date Parsing|
          +-------------+-------------+
                        │
                        v
          +---------------------------+
          |     IngestionService      |
          |  (SAVEPOINT Deduplication)|
          +-------------+-------------+
                        │
                        v
          +---------------------------+
          |      SQLite Database      |
          |       (jobflow.db)        |
          +---------------------------+
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
│   ├── tests/
│   │   ├── test_api.py          # API route unit tests
│   │   ├── test_fallback.py     # Failover unit tests
│   │   ├── test_ingestion.py    # Deduplication & DB unit tests
│   │   ├── test_main.py         # Main app route tests
│   │   └── test_rss_source.py   # Title/Date parsing unit tests
│   ├── Procfile                 # Production deployment start command
│   ├── requirements.txt         # Python dependencies
│   └── jobflow.db               # SQLite database file
├── DECISIONS.md                 # Architecture Decision Records (ADR)
├── README.md                    # System documentation
└── .gitignore                   # Version control exclusion rules
```

---

## 🚀 Quick Start Guide

### Local Environment Setup

```bash
# Clone repository
git clone https://github.com/vansharora156/jobflow.git
cd jobflow/backend

# Create & activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload
```

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service root & system links |
| `GET` | `/health` | Application health check (`{"status": "healthy"}`) |
| `GET` | `/dashboard` | Interactive Web Dashboard UI |
| `GET` | `/jobs/` | List jobs with pagination (`limit`, `offset`) |
| `GET` | `/jobs/count` | Total count of persisted jobs in database |
| `GET` | `/jobs/{job_id}` | Fetch individual job details by ID |
| `POST` | `/jobs/ingest` | Trigger job ingestion pipeline (Primary → Fallback) |
| `GET` | `/sources/health` | Live source health status & ingestion telemetry |

---

## 🧪 Automated Test Execution

Run the complete 14-test suite using `pytest`:

```bash
cd backend
python -m pytest
```

```text
================ 14 passed in 0.92s ================
```

---

## 🛡️ Failure & Fallback Demonstration

1. Override primary URL in `backend/.env` with an invalid host:
   ```env
   JOB_FEED_URL=https://invalid-jobflow-test-source.example/rss
   ```
2. Trigger ingestion endpoint: `POST /jobs/ingest`
3. **Result:** Retries 3 times with exponential backoff, detects DNS failure, automatically failovers to `FallbackRSSJobSource` (`data/fallback_jobs.xml`), returning `"source": "fallback"` and 2 inserted sandbox listings.
