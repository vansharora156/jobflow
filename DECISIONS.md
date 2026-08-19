# Architectural Decisions (ADR)

This document logs key architectural and technical decisions made for the JobFlow project.

---

## Template

### ADR-XXX: Title of Decision

* **Status:** Draft | Accepted | Superseded | Deprecated
* **Date:** YYYY-MM-DD
* **Context:** What is the issue or requirement driving this decision?
* **Decision:** What is the proposed change or design decision?
* **Consequences:** What are the trade-offs, positive impacts, and negative impacts?

---

## ADR-001: Project Layout and Technology Stack

* **Status:** Accepted
* **Date:** 2026-08-19
* **Context:** Initial architecture design for JobFlow backend microservice/application.
* **Decision:**
  * Adopt FastAPI for high-performance async Web API capabilities and auto-generated OpenAPI documentation.
  * Use Pydantic v2 for data validation and schema definitions.
  * Structure code modularly into `api`, `models`, `schemas`, `services`, and `sources`.
* **Consequences:** Clean separation of concerns enabling scalable growth and straightforward testability.
