# JobFlow

JobFlow is a modular job automation and tracking platform built with FastAPI and Python.

## Project Structure

```text
jobflow/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application entrypoint
│   │   ├── config.py        # Environment & application settings
│   │   ├── database.py      # Database session and connection setup
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic schemas / DTOs
│   │   ├── api/             # API routes & endpoints
│   │   ├── services/        # Core business logic
│   │   └── sources/         # External integrations & data sources
│   ├── tests/               # Test suites (pytest)
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Docker container setup
├── README.md
├── DECISIONS.md             # Architecture Decision Records (ADRs)
└── .gitignore
```

## Quick Start

### Local Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be accessible at `http://127.0.0.1:8000` (Docs at `http://127.0.0.1:8000/docs`).

### Docker Setup

```bash
cd backend
docker build -t jobflow-backend .
docker run -p 8000:8000 jobflow-backend
```

## Running Tests

```bash
cd backend
pytest
```
