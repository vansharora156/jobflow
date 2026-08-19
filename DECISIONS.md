# JobFlow – Engineering Decisions


## 1. Source Selection


We Work Remotely RSS was selected as the primary job source because it
provides structured public job data without requiring browser automation.


A controlled RSS XML sandbox is used as the fallback source so that
failover can be tested deterministically without attempting to bypass
source protections.


## 2. Source Architecture


JobFlow uses a source adapter interface:


JobSource
├── RSSJobSource
└── FallbackRSSJobSource


SourceManager is responsible for selecting the primary source and
automatically switching to the fallback when the primary fails or
returns no usable jobs.


This keeps source-specific logic separate from ingestion and database
logic.


## 3. Normalization


The source data is normalized into a common internal Job model.


The primary RSS feed uses:


- "Company: Job Title" → company + title
- region → location
- summary → description
- link → url
- published → published_at


This allows different sources to produce the same internal structure.


## 4. Deduplication


The job URL is used as the uniqueness key.


The database enforces a unique constraint on the URL. SQLAlchemy
SAVEPOINTs are used during batch ingestion so that a duplicate record
does not roll back the entire batch.


## 5. Reliability


The RSS client uses:


- 15-second HTTP timeout
- 3 retry attempts
- exponential backoff
- minimum request pacing interval
- HTTP 429 handling
- Retry-After support
- structured logging


This reduces unnecessary pressure on upstream sources and allows
temporary failures to recover automatically.


## 6. Fallback Strategy


If the primary source becomes unavailable, JobFlow automatically
switches to the controlled fallback source.
