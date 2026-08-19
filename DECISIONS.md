# Architectural Decisions Record (ADR) — JobFlow

This document details the key technical, architectural, and design trade-off decisions for the **JobFlow** resilient job ingestion platform.

---

## ADR-001: Technology Stack & Core Framework

* **Status:** Accepted
* **Context:** Need a high-performance, type-safe, asynchronous web API engine with built-in documentation and validation.
* **Decision:** Selected **Python 3.11+**, **FastAPI**, **Pydantic v2**, and **SQLAlchemy 2.0**.
* **Consequences:** 
  * Auto-generated OpenAPI (Swagger) documentation at `/docs`.
  * Strong type safety and instant request schema validation.
  * Clean separation between internal dataclass models, Pydantic DTOs, and SQLAlchemy ORM models.

---

## ADR-002: Modular Source Adapter Contract (`JobSource`)

* **Status:** Accepted
* **Context:** Ingestion targets change, update markup, or introduce rate-limiting. Hardcoding ingestion logic inside API endpoints creates tight coupling.
* **Decision:** Defined an abstract base interface `JobSource` (`app.sources.base.JobSource`) with `fetch_jobs() -> list[dict[str, Any]]`.
* **Consequences:**
  * Interchangeable source adapters (`RSSJobSource`, `FallbackRSSJobSource`).
  * Switching upstream providers or adding scrapers/APIs requires zero code changes to the database or API routing layers.

---

## ADR-003: Data Normalization Strategy

* **Status:** Accepted
* **Context:** Unstructured feeds use disparate field names (`title`, `region`, `summary`, `link`, `published`).
* **Decision:** Implemented a dedicated normalization mapping inside `RSSJobSource`:
  * **Title Parsing:** `Company: Job Title` split into separate `company` and `title` fields.
  * **Location:** Mapping feed `region` to `location`.
  * **Description:** HTML tag cleaning and whitespace stripping via `re.sub(r"<[^>]+>", " ", value)`.
  * **Publication Date:** RFC 822 string parsing to naive UTC `datetime`.
  * **URL:** Normalizing direct job link.

---

## ADR-004: Deduplication & Transactional Isolation

* **Status:** Accepted
* **Context:** Repeated ingestion runs from RSS feeds return overlapping jobs, threatening database bloat and duplicate listings.
* **Decision:**
  * Enforced a `unique=True` database constraint on `JobDB.url`.
  * Implemented **SQLAlchemy SAVEPOINT isolation** (`db.begin_nested()`) inside `IngestionService`.
* **Consequences:**
  * When a duplicate URL is encountered, `savepoint.rollback()` isolates and rolls back ONLY the duplicate item, allowing valid unique listings in the same batch to be committed safely.

---

## ADR-005: Pacing, Timeout, and Exponential Backoff Retry Policy

* **Status:** Accepted
* **Context:** Unreliable networks or rate-limiting servers can cause hanging connections or transient HTTP 5xx/429 failures.
* **Decision:**
  * **Explicit Timeout:** `httpx.get(..., timeout=15.0)` prevents indefinite thread blocking.
  * **Pacing Interval:** Enforced a `5.0s` minimum request interval (`time.monotonic()`) between requests to prevent source hammering.
  * **Exponential Backoff:** Configured `tenacity.retry` with `stop_after_attempt(3)` and `wait_exponential(multiplier=1, min=1, max=8)` for `httpx.TimeoutException` and `httpx.HTTPError`.
  * **HTTP 429 Handling:** Inspects the `Retry-After` HTTP header and pauses execution before retrying.

---

## ADR-006: Primary Source Failure Detection & Automatic Failover

* **Status:** Accepted
* **Context:** Primary job sources can become unavailable, blocked, or offline. The system must remain resilient and operational.
* **Decision:** Designed `SourceManager` (`app.services.source_manager.SourceManager`) orchestrating a primary source (**We Work Remotely RSS**) and a controlled sandbox fallback feed (**JobFlow Sandbox XML**).
* **Consequences:**
  * If the primary source fails after all retries, `SourceManager` catches the exception, logs structured diagnostics, and seamlessly switches ingestion to the fallback feed.
  * Endpoints return metadata indicating `"source": "primary"` or `"source": "fallback"`.

---

## ADR-007: SQLite for Local Development vs PostgreSQL Trade-Offs

* **Status:** Accepted
* **Context:** Need zero-configuration, lightweight local persistence for evaluation while supporting production scale.
* **Decision:** Selected SQLite as the default database (`jobflow.db`) with `check_same_thread=False`.
* **Trade-Offs:**
  * **SQLite Advantages:** File-based, zero setup overhead, instant test execution.
  * **Production Path:** SQLAlchemy ORM abstraction allows switching to PostgreSQL by updating `DATABASE_URL` in `.env` without modifying business logic.
