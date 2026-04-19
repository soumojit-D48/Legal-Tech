# STEPS_BACKEND.md — LegalTech AI Contract Scanner
**Backend-Only Build Order & Execution Guide**
**Read PRD.md, TECH_STACK.md, and FOLDER_STRUCTURE.md before starting any step.**

---

## How to Use This Document

This file covers the complete backend build — every service, pipeline, endpoint, worker task, and data layer needed to power all features defined in the PRD. The frontend (`apps/web/`) is entirely out of scope here. Once the backend is complete, every feature can be verified via curl or a REST client.

Each step is self-contained. Complete it fully, run the verification checklist, and only move to the next step when every item passes. Never skip a step. If a verification fails, fix it before proceeding.

The backend is composed of four layers, built in this order:
1. Infrastructure and environment
2. Database and authentication
3. File handling and document parsing
4. AI pipelines and all feature endpoints

---

## PHASE 0 — Repository & Environment Setup

---

### STEP 0.1 — Initialize the Monorepo Root

Create the root directory `legaltech-ai/` and initialize a git repository. Create the top-level folder structure exactly as defined in FOLDER_STRUCTURE.md, but only the backend-relevant directories need to be wired up now: `services/api/`, `services/ai/`, `apps/worker/`, `packages/`, `infra/`, `scripts/`, `tests/`, and `.github/workflows/`. Create an empty `docker-compose.yml`, `docker-compose.test.yml`, `.gitignore`, and `README.md` at the root. The `.gitignore` must cover Python virtual environments, `__pycache__/`, `.env` files, compiled files, OS artifacts, and the Node-specific folders even if frontend is not yet built.

**Verification:**
- Root directory structure matches FOLDER_STRUCTURE.md at the top level for backend-relevant paths
- Git is initialized and first commit is made
- `.gitignore` blocks `__pycache__/`, `*.pyc`, `.env`, `.DS_Store`, `venv/`, `node_modules/`

---

### STEP 0.2 — Create the Root Environment Variable Template

Create `.env.example` at the monorepo root with every environment variable key listed in FOLDER_STRUCTURE.md's environment variables section. All values must be empty placeholders — no real secrets. Group them by section: Frontend (keep the keys, leave values blank), Backend API, AI Service, Shared. Create a copy as `.env` at the root (this is gitignored). Add an inline comment next to every key explaining what it is and where to get it.

**Verification:**
- `.env.example` exists at root with all variable keys present and grouped correctly
- `.env` exists at root and is confirmed to be gitignored
- Every variable from FOLDER_STRUCTURE.md's env section is present with a comment

---

### STEP 0.3 — Initialize the FastAPI Backend Service

Inside `services/api/`, create a Python virtual environment and install all backend packages from `requirements.txt` as listed in TECH_STACK.md. Create the FastAPI `app/main.py` with: app initialization, CORS middleware configured to allow all origins during development (tighten later), and a single `GET /health` endpoint returning `{"status": "ok", "service": "api"}`. Create `app/core/config.py` using Pydantic BaseSettings to load all backend environment variables from `.env`. Create a `run.py` file that starts uvicorn on port 8000. Create the `Dockerfile` for the API service. Create the folder structure inside `services/api/app/` exactly as defined in FOLDER_STRUCTURE.md: `api/`, `core/`, `models/`, `schemas/`, `services/`, `repositories/`, `db/`, `workers/`, `utils/`, and `templates/`. Add empty `__init__.py` files in each.

**Verification:**
- `uvicorn app.main:app --reload` starts without errors on port 8000
- `curl http://localhost:8000/health` returns `{"status": "ok", "service": "api"}`
- `curl -H "Origin: http://localhost:3000" http://localhost:8000/health` shows CORS headers in the response
- All environment variables load without errors via Pydantic Settings

---

### STEP 0.4 — Initialize the AI Service

Inside `services/ai/`, create a Python virtual environment and install all AI-specific packages: spaCy with `en_core_web_sm`, sentence-transformers (`all-MiniLM-L6-v2`), langdetect, langchain, langchain-openai, PyMuPDF, python-docx, unstructured (pdf and docx extras only), httpx, python-dotenv, and deepl. Create a minimal `main.py` that starts a lightweight FastAPI or plain HTTP service on port 8001 with a `GET /health` endpoint returning `{"status": "ok", "service": "ai"}`. Create all subdirectories defined in FOLDER_STRUCTURE.md under `services/ai/`: `pipelines/`, `prompts/`, `models/`, `rag/`, `rules/`, `parser/`, `translation/`, `cache/`, `data/`, `utils/`. Add `__init__.py` files in each. Create the `Dockerfile` for the AI service.

**Verification:**
- All imports succeed: `import fitz`, `import spacy`, `from sentence_transformers import SentenceTransformer`, `import langdetect`, `from langchain import ...`, `import docx`, `import httpx`
- `python -m spacy download en_core_web_sm` completes and `spacy.load("en_core_web_sm")` works
- `SentenceTransformer("all-MiniLM-L6-v2")` downloads and loads without error
- `curl http://localhost:8001/health` returns `{"status": "ok", "service": "ai"}`

---

### STEP 0.5 — Initialize the Celery Worker

Inside `apps/worker/`, create a Python virtual environment. Install Celery, the Redis client, and any shared dependencies needed for task processing (httpx, sqlalchemy, pydantic). Create `celery_app.py` with Celery initialization configured to use the Redis URL from environment variables as both the broker and result backend. Create the `tasks/` directory with placeholder files for each task defined in FOLDER_STRUCTURE.md: `process_contract.py`, `generate_summary.py`, `generate_counter_offer.py`, `generate_report.py`, `embed_contract.py`, `translate_results.py`, `cleanup_expired_reports.py`. Each placeholder file must define an empty Celery task function decorated with `@app.task` so Celery can discover it. Create the `Dockerfile` for the worker.

**Verification:**
- `celery -A celery_app worker --loglevel=info` starts without errors
- Celery connects to Redis and reports worker ready in the logs
- All task modules are auto-discovered by Celery (they appear in the worker log output)

---

### STEP 0.6 — Set Up Docker Compose for Local Development

Write the `docker-compose.yml` at the root to orchestrate all backend services: `api` (FastAPI on port 8000), `ai` (AI service on port 8001), `worker` (Celery, no exposed port), `redis` (Redis on port 6379), `db` (PostgreSQL 16 on port 5432). Configure environment variable injection from the root `.env` file into each service. Configure volume mounts for hot-reload during development on the API and AI services. Write `docker-compose.test.yml` for isolated test environments with a separate Postgres and Redis instance (different ports to avoid collision). Write `infra/nginx/nginx.conf` as a reverse proxy routing `/api` to FastAPI.

**Verification:**
- `docker-compose up` brings all backend services up without errors
- `curl http://localhost:8000/health` returns `{"status": "ok", "service": "api"}`
- `curl http://localhost:8001/health` returns `{"status": "ok", "service": "ai"}`
- Redis is reachable from the worker container (check worker logs for successful connection)
- PostgreSQL is reachable from the API container (check API logs)

---

## PHASE 1 — Database Foundation

---

### STEP 1.1 — Configure Database Connection

In `services/api/app/db/session.py`, set up the SQLAlchemy async engine using `asyncpg` as the driver, connected to the Neon PostgreSQL URL from environment variables. Configure the async session factory with a reasonable connection pool size. Create `app/db/base.py` that imports the declarative base and will serve as the discovery point for all models during Alembic migrations. Initialize Alembic in the `migrations/` directory. Configure `alembic.ini` and `migrations/env.py` to use the async engine and to auto-discover models from `app/db/base.py`.

**Verification:**
- The async engine connects to the database without raising a connection error on startup
- `alembic current` runs without errors (output shows "head" or no current revision yet — no crash)

---

### STEP 1.2 — Create All Database Models

In `services/api/app/models/`, create every ORM model defined in PRD.md Section 4.3. Create models for: `User`, `Contract`, `Clause`, `ScanJob`, `AnalysisResult`, `CounterOffer`, `PrecedentMatch`, `Report`, and `Embedding`. Each model must have: a UUID primary key, appropriate foreign key relationships, `created_at` and `updated_at` timestamps with auto-population, and all columns from the PRD schema. The `Embedding` model must use the `pgvector` `Vector` column type for the embedding field — import from the `pgvector.sqlalchemy` extension. Import all models in `app/db/base.py` so Alembic can detect them.

**Verification:**
- All model files import without errors: `python -c "from app.models import user, contract, clause, scan_job, analysis_result, counter_offer, precedent_match, report, embedding"`
- No circular import errors when all models are imported together
- The `Embedding` model's embedding column is of type `Vector`

---

### STEP 1.3 — Create and Run the Initial Migration

Generate the first Alembic migration using autogenerate. Before running autogenerate, ensure the migration also enables the `pgvector` extension by adding a manual `op.execute("CREATE EXTENSION IF NOT EXISTS vector")` at the top of the `upgrade()` function. Review the generated migration file to confirm all 9 tables are present with the correct columns, foreign keys, and indexes. Run the migration against the development database. Create a second targeted migration that adds any missing indexes important for performance: an index on `clauses.contract_id`, `scan_jobs.contract_id`, `scan_jobs.status`, `embeddings.contract_id`, and `embeddings.embedding_type`.

**Verification:**
- `alembic upgrade head` runs without errors
- All 9 tables exist in the database: `users`, `contracts`, `clauses`, `scan_jobs`, `analysis_results`, `counter_offers`, `precedent_matches`, `reports`, `embeddings`
- The `pgvector` extension is active: run `SELECT * FROM pg_extension WHERE extname = 'vector'` against the database — it should return one row
- `alembic current` confirms the migration is applied

---

### STEP 1.4 — Create the Repository Layer

In `services/api/app/repositories/`, create a repository file for each entity: `user_repo.py`, `contract_repo.py`, `clause_repo.py`, `scan_job_repo.py`, `precedent_repo.py`, and `report_repo.py`. Each repository contains only async database query functions — no business logic. Standard functions for each: `create`, `get_by_id`, `get_all_by_user_id`, `update`, `delete`. Additional functions: `scan_job_repo` needs `update_status(job_id, status)` and `update_progress(job_id, pct)`. `report_repo` needs `get_by_share_uuid(uuid)` and `delete_expired()`. `clause_repo` needs `get_all_by_contract_id(contract_id)` and `bulk_create(clauses)`. All functions must use the async SQLAlchemy session and return `None` gracefully when a record is not found.

**Verification:**
- All repository files import without errors
- Each repository function can be called with a mock async session without errors (write a quick standalone test script if needed)
- No business logic appears in any repository — only query construction and execution

---

## PHASE 2 — Authentication

---

### STEP 2.1 — Configure Clerk JWT Verification in the Backend

In `services/api/app/core/security.py`, implement Clerk JWT verification. The function must: extract the Bearer token from the `Authorization` header, fetch Clerk's JWKS endpoint to get the public key (cache this — do not refetch on every request), verify the token signature and expiry, extract the `sub` claim as the user ID, and return it. Create a FastAPI dependency function wrapping this so any endpoint can inject it with a single parameter. Any verification failure must raise `HTTPException(status_code=401)`.

In `services/api/app/api/v1/endpoints/auth.py`, create the Clerk webhook endpoint `POST /webhooks/clerk`. This endpoint receives `user.created` and `user.updated` events from Clerk and upserts the user record in the `users` table. Verify the webhook signature using the `CLERK_WEBHOOK_SECRET` from environment variables. Register this endpoint on the router in `app/api/v1/router.py` — create `router.py` now if it does not exist.

**Verification:**
- `curl -H "Authorization: Bearer invalidtoken" http://localhost:8000/api/v1/contracts` returns `401`
- `curl -H "Authorization: Bearer <valid_clerk_jwt>" http://localhost:8000/api/v1/contracts` returns `200` (or `404` if no contracts) — not `401`
- Sending a simulated `user.created` webhook payload to `POST /webhooks/clerk` creates a user row in the `users` table

---

### STEP 2.2 — Mount the API Router and Protect All Routes

Create `services/api/app/api/v1/router.py` that aggregates all v1 endpoint routers (auth, upload, analysis, streaming, counter_offer, summary, power, precedent, report, chat, translate, health). Mount this under the `/api/v1` prefix in `app/main.py`. Create placeholder router files for all endpoints listed in FOLDER_STRUCTURE.md under `app/api/v1/endpoints/` — each must define the router with `APIRouter()` and at minimum a stub endpoint returning `{"status": "not_implemented"}` so the router mounts without errors. Apply the Clerk JWT dependency to all routers except `health` and `webhooks/clerk`.

**Verification:**
- `curl http://localhost:8000/api/v1/health` returns `{"status": "ok"}` without authentication
- `curl http://localhost:8000/api/v1/upload` returns `401` (no token)
- `curl http://localhost:8000/api/v1/scan/test-job-id` returns `401` (no token)
- All expected route paths exist: verify with `curl http://localhost:8000/openapi.json` and inspect the `paths` object

---

## PHASE 3 — File Upload Pipeline

---

### STEP 3.1 — Implement the Upload Endpoint

In `services/api/app/api/v1/endpoints/upload.py`, implement the `POST /api/v1/upload` endpoint. It must: require a valid Clerk JWT, accept a JSON request body containing: `file_url` (Uploadthing URL of the encrypted uploaded file), `original_filename`, `file_type` (pdf or docx), and `file_size_bytes`. Create a `Contract` record in the database with the authenticated user's ID, file reference, and detected language as "unknown" (to be updated after detection). Create a `ScanJob` record with status "queued" and progress 0. Queue the main Celery scan task by calling it with the `contract_id` and `file_url`. Return a JSON response containing `job_id`, `contract_id`, and `status: "queued"`.

In `services/api/app/services/contract_service.py`, implement the business logic called by the upload endpoint: `create_contract()` and `create_scan_job()`.

**Verification:**
- `curl -X POST http://localhost:8000/api/v1/upload -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"file_url":"https://example.com/test.pdf","original_filename":"test.pdf","file_type":"pdf","file_size_bytes":50000}'` returns a JSON object with `job_id`, `contract_id`, and `status: "queued"`
- A `Contract` row is created in the database with the correct `user_id`
- A `ScanJob` row is created with `status = "queued"`
- The Celery task appears in the worker logs as received

---

### STEP 3.2 — Implement File Retrieval and Decryption Utility

In `services/api/app/utils/file_handler.py`, implement the file retrieval and temporary storage utility. It must: accept an Uploadthing file URL, download the file bytes using httpx, save the bytes to a secure temporary file path in `/tmp/` with a UUID filename, and return the temp file path. Also implement a cleanup function that deletes the temp file after processing. Note on encryption: the frontend sends the encryption key in the session via the `Authorization` header alongside the Clerk JWT. The file handler must be designed to accept an optional decryption key and decrypt the file bytes using AES-256-GCM before writing to disk. If no key is provided (for testing), write the raw bytes. Document clearly that in production the key comes from the session header.

**Verification:**
- Calling the download function with a publicly accessible PDF URL downloads the file and returns a valid file path
- The temp file exists on disk after the call
- The cleanup function removes the temp file
- Calling with a non-existent URL raises a clear error — not a silent failure

---

## PHASE 4 — Document Parsing Pipeline

---

### STEP 4.1 — Implement the PDF Parser

In `services/ai/parser/pdf_parser.py`, implement PDF text extraction using PyMuPDF (fitz). The parser must: open the file from a file path, extract text page by page, preserve paragraph structure, strip repeated headers and footers (detect text appearing on 3+ consecutive pages and exclude it), and return a single cleaned text string. Handle password-protected PDFs by returning a dict with `error: "password_protected"`. Handle scanned PDFs (no extractable text) by returning the text as an empty string along with a `requires_ocr: True` flag.

**Verification:**
- Run the parser against a real multi-page PDF contract and confirm readable text is returned
- Run against a scanned PDF — confirm an empty text string is returned with `requires_ocr: True`, no crash
- Run against a password-protected PDF — confirm a graceful error dict is returned, no crash

---

### STEP 4.2 — Implement the DOCX Parser

In `services/ai/parser/docx_parser.py`, implement DOCX text extraction using python-docx. The parser must: open the DOCX from a file path, extract text from all paragraphs in document order, preserve section headings as delimiter markers in the output text, extract text from all tables in the document, and return a single cleaned text string. Handle empty or malformed DOCX files without crashing.

**Verification:**
- Run the parser against a real DOCX contract and confirm readable text including headings is returned
- Run against an empty DOCX — confirm an empty string is returned without crash
- Tables in the DOCX appear as text in the output

---

### STEP 4.3 — Implement the Fallback Parser and Dispatcher

In `services/ai/parser/fallback_parser.py`, implement the unstructured.io fallback parser using only the `pdf` and `docx` extras. Accept a file path and file type, run unstructured on it, and return the extracted text as a string.

In `services/ai/parser/__init__.py` (or a `dispatcher.py`), implement the `parse_document(file_path, file_type)` function: call the appropriate primary parser based on file type, check if the output text is meaningful (more than 100 characters), and call the fallback if the primary returns insufficient content. Return a `ParseResult` object containing `text`, `file_type`, `page_count`, and `requires_ocr` flag.

**Verification:**
- `parse_document("path/to/contract.pdf", "pdf")` returns a `ParseResult` with `text` longer than 100 characters for a normal PDF
- `parse_document("path/to/scanned.pdf", "pdf")` triggers the fallback parser and still returns text if unstructured can extract it
- `parse_document("path/to/contract.docx", "docx")` returns correct text

---

### STEP 4.4 — Implement Clause Segmentation

In `services/ai/pipelines/clause_extraction.py`, implement clause segmentation using spaCy's `en_core_web_sm` model. The segmenter must: load the spaCy model once (use a module-level singleton to avoid reloading), split the contract text into sentence units, group adjacent sentences into logical clauses using heuristics (numbered sections like "1.1", lettered sub-clauses, continuation sentences that don't start with a capital letter or clause number), assign each clause a sequential `position_index`, merge any clause under 10 words into the adjacent clause, split any clause over 500 words at sentence boundaries, and return a list of clause objects each containing: `clause_id` (UUID), `position_index`, `text`, and `word_count`.

**Verification:**
- A 10-page contract text produces between 20 and 100 clause objects
- No clause in the output is under 10 words
- No clause in the output is over 500 words
- `position_index` values are sequential integers starting at 0 with no gaps
- Each `clause_id` is a unique UUID

---

## PHASE 5 — LLM Integration Foundation

---

### STEP 5.1 — Implement the OpenRouter Client

In `services/ai/models/openrouter_client.py`, implement the async OpenRouter API client using httpx. It must: read the API key, primary model name, and fast model name from environment variables, support both standard (non-streaming) and streaming request modes via a parameter, enforce `response_format: {"type": "json_object"}` for all structured output calls, implement retry logic with up to 3 retries and exponential backoff on 429 and 5xx responses, log all requests and responses at DEBUG level, and return the response content as a string.

In `services/ai/models/model_config.py`, define model name constants: `PRIMARY_MODEL` (Llama 3.3 70B) and `FAST_MODEL` (Gemini Flash), along with default temperature settings for each use case (risk analysis, creative counter-offer generation, etc.).

In `services/ai/models/streaming.py`, implement the streaming handler that consumes a streaming httpx response from OpenRouter and yields complete JSON strings one at a time as they arrive (accumulate tokens until a valid JSON object is complete, then yield it).

**Verification:**
- `python -c "from services.ai.models.openrouter_client import call_llm; import asyncio; print(asyncio.run(call_llm('Return JSON: {\"test\": true}', 'fast')))"` returns a JSON string without error
- A simulated 429 response (mock the httpx call) triggers a retry — verify via log output
- The streaming handler yields tokens progressively when `stream=True`

---

### STEP 5.2 — Create All Prompt Template Files

In `services/ai/prompts/`, create all 7 prompt template files as plain text: `risk_analysis.txt`, `type_detection.txt`, `consequence.txt`, `summary.txt`, `power_asymmetry.txt`, `counter_offer.txt`, `precedent.txt`. Each file must contain a clearly structured system prompt and user prompt template, using `{{placeholder}}` syntax for all dynamic values. Refer to PRD.md Section 3 for what each prompt must accomplish and what output fields it must return. Every prompt must instruct the model to return only valid JSON with no preamble, no markdown formatting, and no explanation outside the JSON object.

In `services/ai/utils/` create a `prompt_loader.py` utility that: reads a prompt file by name from the `prompts/` directory, substitutes all `{{placeholder}}` tokens with values from a provided dictionary, raises a clear `ValueError` if a required placeholder is missing or if the prompt file does not exist, and returns the final prompt string.

**Verification:**
- Each of the 7 prompt files exists and contains valid text with at least one `{{placeholder}}`
- `prompt_loader.py` correctly substitutes all placeholders given a matching dictionary
- `prompt_loader.py` raises `ValueError` if a required placeholder is missing
- `prompt_loader.py` raises `ValueError` if the requested prompt file does not exist

---

### STEP 5.3 — Implement All Pydantic Response Schemas

In `services/api/app/schemas/`, create all Pydantic v2 schema files:

`response.py` — define all shared enums: `RiskLevel` (HIGH, MEDIUM, LOW, SAFE), `ContractType` (Employment, NDA, Freelance/SOW, SaaS Subscription, Lease/Rental, Partnership, IP License, Loan, M&A, Other), `ScanStatus` (queued, processing, complete, failed), `SignVerdict` (Yes as-is, Yes with changes, No), `PowerLabel`, `EnforcementLikelihood`.

`clause.py` — `ClauseResult` containing all fields from PRD.md Feature 1: clause_id, position_index, text, risk_level, risk_category, plain_english, worst_case_scenario, negotiable (bool), confidence (float), financial_exposure (optional), headline (optional), scenario (optional), probability (optional).

`scan_job.py` — `ScanJobStatus` (job_id, contract_id, status, progress_pct, error_message optional), `ScanResponse`.

`contract.py` — `ContractCreate`, `ContractRead` (includes contract_type, detected_language, party_roles, created_at, overall_risk_score if available).

`power.py` — `PowerAnalysisResult` (power_score int, power_label, key_imbalances array, leverage_points array).

`precedent.py` — `CaseReference` (name, year, jurisdiction, outcome), `PrecedentMatch` (precedent_summary, enforcement_likelihood, confidence_score, cited_cases array).

`counter_offer.py` — `CounterOfferVersion` (clause_text, explanation), `CounterOfferResult` (aggressive, balanced, conservative, negotiation_email).

`summary.py` — `SummaryCard` (one_liner, should_you_sign, top_3_concerns, top_2_positives, overall_risk_score, negotiating_power), `ProsConsItem` (dimension, point), `ProsConsResult` (pros, cons, verdict).

`chat.py` — `ChatRequest` (question, conversation_history optional array), `ChatResponse` (answer, clause_citation optional, sources array).

`report.py` — `ReportCreate`, `ReportRead` (report_id, share_uuid, share_url, expires_at, language, pdf_path).

`translation.py` — `TranslationRequest` (target_language), `TranslationResponse` (contract_id, target_language, status).

In `services/ai/`, create a matching set of Pydantic models for validating raw LLM JSON responses (these may differ slightly — they represent what the LLM actually returns before being mapped to the API schemas). Create a `validate_llm_response(raw_json_string, pydantic_model)` utility in `services/ai/utils/` that: parses the JSON, validates against the Pydantic model, catches `ValidationError` and logs the raw string on failure, and returns `None` on failure so callers can retry.

**Verification:**
- All schema files import without errors
- `ClauseResult(clause_id="...", position_index=0, text="...", risk_level="HIGH", risk_category="indemnity", plain_english="...", worst_case_scenario="...", negotiable=True, confidence=0.85)` parses without error
- `ClauseResult(risk_level="INVALID")` raises a `ValidationError`
- `validate_llm_response('{"bad": "json"', ClauseResult)` returns `None` without raising

---

## PHASE 6 — Core Scan Pipeline

---

### STEP 6.1 — Implement Contract Type Detection Pipeline

In `services/ai/pipelines/type_detection.py`, implement the contract type auto-detection pipeline. It takes the first 1000 tokens of the contract text, calls the FAST_MODEL using the `type_detection.txt` prompt, parses the response with Pydantic validation, and returns a `TypeDetectionResult` object containing: `contract_type` (one of the 10 defined types), `confidence` (float 0–1), `party_roles` (array of strings), and `requires_manual_selection` (True if confidence < 0.8).

**Verification:**
- Run the function against a real employment contract text — it should return `contract_type = "Employment"` with `confidence > 0.8`
- Run against an NDA — it should return `contract_type = "NDA"`
- Run against ambiguous text — it should return `requires_manual_selection = True` if confidence is low
- The function returns a valid Pydantic model, not a raw dict

---

### STEP 6.2 — Implement the Rule Engine

In `services/ai/rules/regex_rules.py`, define the rule set as a list of rule objects. Each rule object has: `name`, `pattern` (compiled regex), `risk_category`, and `risk_level` (HIGH or MEDIUM). Implement at minimum 40 patterns covering all risk categories from PRD.md Feature 1: indemnity, IP assignment, non-compete, non-solicitation, auto-renewal, limitation of liability, termination for convenience, unilateral modification rights, liquidated damages, arbitration-only, payment clawback, and governing law. Include multiple patterns per category to catch varied phrasing.

In `services/ai/rules/risk_mapper.py`, implement the `triage_clause(clause_text)` function: run all patterns against the text, collect matches, and return the triage result — `GREEN` if zero matches, `YELLOW` if 1–2 matches (none HIGH-level), `RED` if 3+ matches or any single HIGH-level pattern matches. Also return the list of matched rule names for downstream use.

**Verification:**
- `triage_clause("shall indemnify, defend, and hold harmless")` returns `RED` or `YELLOW` with category `indemnity`
- `triage_clause("all intellectual property, inventions, and work product created")` returns `RED` with category `ip_assignment`
- `triage_clause("This agreement will automatically renew")` returns `YELLOW` or `RED` with category `auto_renewal`
- `triage_clause("The parties agree to the following payment terms.")` returns `GREEN`
- A clause with a HIGH-level pattern (e.g., a non-compete) returns `RED` regardless of total match count

---

### STEP 6.3 — Implement the Risk Classification Pipeline

In `services/ai/pipelines/risk_classification.py`, implement the full two-pass risk classification pipeline from PRD.md Feature 1.

Pass 1: run `triage_clause` from the rule engine on every clause. Separate results into GREEN, YELLOW, and RED buckets. GREEN clauses receive a default `ClauseResult` with `risk_level = SAFE` and `confidence = 1.0` — no LLM call needed.

Pass 2: take all YELLOW and RED clauses and batch them into groups of maximum 20. For each batch, call the PRIMARY_MODEL with the `risk_analysis.txt` prompt, injecting the contract type, user role, and the batch of clause texts. Parse and validate each clause result in the response array with Pydantic. If validation fails for any clause in a batch, retry that batch once with a correction prompt before defaulting to a safe fallback result.

Implement a streaming variant of this function that yields each validated `ClauseResult` object one at a time as responses arrive, rather than accumulating all results and returning at the end.

**Verification:**
- Run the pipeline on a 30-clause contract where 10 clauses are GREEN, 15 YELLOW, 5 RED
- Confirm exactly 0 LLM calls are made for GREEN clauses (check call count)
- Confirm YELLOW and RED clauses are batched: 15+5 = 20 in one batch = 1 LLM call
- Confirm all 30 clauses are present in the output with valid `ClauseResult` objects
- The streaming variant yields results progressively — not all at once

---

### STEP 6.4 — Implement the SSE Streaming Endpoint

In `services/api/app/api/v1/endpoints/streaming.py`, implement `GET /api/v1/scan/{jobId}/stream`. This is the most critical endpoint. It must: verify the Clerk JWT, confirm the scan job belongs to the requesting user, subscribe to the Redis pub/sub channel named `scan:{jobId}`, yield each message received from the channel as an SSE event with format `data: {json}\n\n`, send a heartbeat event every 15 seconds to keep the connection alive (format: `event: heartbeat\ndata: {}\n\n`), send a final `event: complete\ndata: {}\n\n` event when the scan job status becomes "complete", and close the StreamingResponse cleanly.

In `services/api/app/services/streaming_service.py`, implement the `publish_clause_result(job_id, clause_result_json)` function that publishes a message to the `scan:{jobId}` Redis pub/sub channel. The Celery worker will call this after each clause is processed.

**Verification:**
- `curl -N -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/scan/<jobId>/stream` keeps the connection open and shows `event: heartbeat` every 15 seconds
- `curl -N -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/scan/<invalid-jobId>/stream` returns `404`
- Manually publishing a message to the Redis channel (using `redis-cli PUBLISH scan:<jobId> '{"test":true}'`) causes it to appear in the curl output
- Calling with another user's job ID returns `403`

---

### STEP 6.5 — Implement the Main Celery Scan Task

In `apps/worker/tasks/process_contract.py`, implement the main scan pipeline Celery task. This task orchestrates all pipeline steps in the exact order from PRD.md Section 4.1. The task receives `contract_id` and `file_url` as arguments and must:

1. Update `ScanJob` status to "processing", progress to 0
2. Download and (if applicable) decrypt the contract file via `file_handler.py`
3. Parse the document with the dispatcher — update progress to 10%
4. Detect language with `langdetect` — if non-English, translate to English via DeepL — update progress to 15%
5. Segment into clauses — update progress to 20%
6. Run the rule engine triage on all clauses — update progress to 25%
7. Detect contract type — update progress to 30%
8. Run risk classification (LLM calls on flagged clauses) — publish each completed clause result to Redis as it arrives — update progress to 60%
9. Run consequence generation on HIGH and MEDIUM clauses — update progress to 70%
10. Run power asymmetry analysis — update progress to 75%
11. Run legal precedent retrieval for each HIGH-risk clause — update progress to 80%
12. Run summary card generation — update progress to 85%
13. Run pros/cons generation — update progress to 88%
14. Store all results in the database (clauses, analysis_result, precedent_matches) — update progress to 95%
15. Run embedding pipeline for Q&A RAG — update progress to 98%
16. If original contract was non-English, translate all result text fields back to the user's preferred language — update progress to 99%
17. Update `ScanJob` status to "complete", progress to 100%
18. Publish a "complete" signal to the Redis pub/sub channel

On any unhandled exception: set `ScanJob` status to "failed" and store the error message. Configure the task to retry up to 3 times on transient failures with exponential backoff.

**Verification:**
- Queue the task manually via `celery -A celery_app call process_contract --args='["<contract_id>", "<file_url>"]'`
- Watch the `scan_jobs` table — `progress_pct` should increase through the steps
- Watch the Redis pub/sub channel for clause results being published
- After completion, `ScanJob` status = "complete" in the database
- After completion, all clause rows exist in the `clauses` table
- `analysis_results` row exists with `overall_risk_score` populated
- If the task is given a bad file URL, status becomes "failed" with an error message

---

### STEP 6.6 — Wire Upload to Scan — End-to-End Integration Check

No new code is written in this step. Test the full loop from upload endpoint to scan completion.

**Verification:**
- `POST /api/v1/upload` with a real PDF URL returns `job_id` and `contract_id`
- Open the SSE stream: `curl -N -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/scan/<jobId>/stream`
- Clause results arrive in the stream as the worker processes them
- The stream receives `event: complete` when the scan finishes
- All clause rows exist in the `clauses` table after completion
- `GET /api/v1/scan/<jobId>` (implement a basic status endpoint if not yet done) returns `status: complete`

---

## PHASE 7 — Remaining AI Feature Pipelines

---

### STEP 7.1 — Implement the Consequence Generation Pipeline

In `services/ai/pipelines/consequence_generation.py`, implement the real-world consequence translator from PRD.md Feature 3. The function accepts an array of HIGH and MEDIUM risk clause results (with their risk categories already assigned), iterates over them, and for each clause calls the PRIMARY_MODEL with the `consequence.txt` prompt injecting: `clause_type`, `user_role`, `contract_type`, and `clause_text`. Parse each response into a Pydantic model containing: `headline`, `scenario`, `financial_exposure`, `probability`, and `similar_case` (optional). Return the input clause results enriched with the consequence fields. Only process HIGH and MEDIUM clauses — skip LOW and SAFE. Batch where possible to reduce LLM calls.

Update the main Celery task to call this pipeline after risk classification and to publish updated clause results (with consequence fields added) back to the Redis channel.

**Verification:**
- Run the pipeline directly on a list of mock HIGH-risk clause objects
- An indemnity clause returns a `financial_exposure` field that is a dollar amount or the string "unlimited" — not empty
- An IP assignment clause returns a `headline` that references IP, portfolio, or ownership
- `probability` is always one of "Low", "Medium", or "High"
- LOW and SAFE clauses are passed through unchanged — no LLM calls for them

---

### STEP 7.2 — Implement the Power Asymmetry Pipeline and Endpoint

In `services/ai/pipelines/power_analysis.py`, implement the power asymmetry scorer from PRD.md Feature 5. The function accepts the full array of clause results (with risk assessments) and the user role. It calls the PRIMARY_MODEL with the `power_asymmetry.txt` prompt, parses the response into a `PowerAnalysisResult` Pydantic model containing: `power_score` (integer -100 to +100), `power_label`, `key_imbalances` (array of objects with `clause`, `why`, `score`), and `leverage_points` (array of strings).

In `services/api/app/api/v1/endpoints/power.py`, implement `GET /api/v1/power/{contractId}`. Verify JWT and ownership, fetch the power analysis result from `analysis_results` table, and return the `PowerAnalysisResult`. If the scan is not yet complete, return `202 Accepted` with a retry message.

**Verification:**
- Run the pipeline on a mock contract with all HIGH-risk clauses — confirm `power_score` is below -30
- `power_score` is always an integer between -100 and +100 — never a float, never out of range
- `key_imbalances` contains at least 1 item when HIGH-risk clauses are present
- `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/power/<contractId>` returns the power analysis JSON for a completed scan

---

### STEP 7.3 — Implement the Summary Card Pipeline and Endpoint

In `services/ai/pipelines/summary.py`, implement the plain-language summary card generator from PRD.md Feature 4. The function accepts: contract type, all HIGH-risk clause summaries, all MEDIUM-risk clause summaries, and risk distribution statistics (counts per level). It calls the FAST_MODEL with `summary.txt`, parses the response into a `SummaryCard` Pydantic model. In the same pipeline file or as a second function, implement the pros/cons generator: accepts the full clause analysis, calls FAST_MODEL with a pros/cons prompt, returns a `ProsConsResult`.

In `services/api/app/api/v1/endpoints/summary.py`, implement `GET /api/v1/summary/{contractId}`. Verify JWT and ownership, fetch summary and pros/cons from `analysis_results`, and return both as a combined response object.

**Verification:**
- `should_you_sign` is always one of "Yes as-is", "Yes with changes", "No" — never any other value
- `overall_risk_score` is always an integer between 0 and 100
- `top_3_concerns` always has exactly 3 items
- `top_2_positives` always has exactly 2 items
- `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/summary/<contractId>` returns the full summary JSON

---

### STEP 7.4 — Seed the Legal Precedent Corpus

Before implementing the precedent retrieval pipeline, the corpus must exist. In `services/ai/data/precedents/`, create subdirectories for `employment/`, `ip/`, `nda/`, and `vendor/`. Populate each directory with at minimum 15 real or well-researched fictional court case summary files (at least 60 total across all domains). Each file should contain: case name, year, jurisdiction, outcome, a 2–3 sentence summary of the clause at issue and the court's ruling, and the clause type tag. These do not need to be exact legal documents — they are summaries used for embedding similarity.

In `scripts/seed_precedents.py`, implement the seeding script: read all case summary files from the `data/precedents/` subdirectories, embed each using sentence-transformers `all-MiniLM-L6-v2`, store each embedding in the `embeddings` table with `embedding_type = "precedent"` and metadata (jurisdiction, year, outcome, clause_type) in a JSONB column, and print the total number of records indexed.

Run the script to populate the database.

**Verification:**
- `python scripts/seed_precedents.py` runs without errors and reports at least 60 records indexed
- Query the `embeddings` table: `SELECT COUNT(*) FROM embeddings WHERE embedding_type = 'precedent'` returns at least 60
- A manual pgvector similarity search for a non-compete clause text against the `precedent` embeddings returns at least 3 results with similarity score > 0.4

---

### STEP 7.5 — Implement the Legal Precedent Retrieval Pipeline and Endpoint

In `services/ai/rag/retriever.py`, implement the pgvector similarity search function. It accepts: a query embedding (vector), `embedding_type` filter, optional `clause_type` filter, and `top_k` integer. It runs a pgvector cosine similarity query against the `embeddings` table and returns the top-k results with their metadata and similarity scores.

In `services/ai/rag/vector_store.py`, implement `store_embeddings(contract_id, chunks, embedding_type)` for bulk insert of embedding records.

In `services/ai/pipelines/precedent_retrieval.py`, implement the legal precedent retrieval pipeline from PRD.md Feature 9. For each HIGH-risk clause: embed the clause text, run a similarity search filtered to `embedding_type = "precedent"` and the clause's risk category, retrieve the top 3 matches, call the PRIMARY_MODEL with `precedent.txt` injecting the clause text and the 3 retrieved case summaries, parse the response into a `PrecedentMatch` Pydantic model, calculate the confidence score as the product of average retrieval similarity and the LLM's self-rated confidence (implement this in `services/ai/utils/confidence_scorer.py`), store the result in `precedent_matches`.

In `services/api/app/api/v1/endpoints/precedent.py`, implement `GET /api/v1/precedent/{clauseId}`. Verify JWT, confirm the clause belongs to a contract owned by the user, fetch the `PrecedentMatch` record, and return it.

**Verification:**
- Run the pipeline for a non-compete clause — confirm 3 case cards are returned with `enforcement_likelihood` set
- `confidence_score` is between 0 and 100 — never outside this range
- `cited_cases` has between 1 and 3 items
- `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/precedent/<clauseId>` returns the precedent JSON for a HIGH-risk clause
- The same call for a LOW-risk clause returns `404` or an empty precedent result (precedent is only generated for HIGH-risk)

---

### STEP 7.6 — Seed the Favorable Clause Corpus and Implement Counter-Offer Pipeline

In `services/ai/data/favorable_clauses/`, create subdirectories for each clause type: `indemnity/`, `ip_assignment/`, `non_compete/`, `auto_renewal/`, `limitation_of_liability/`. Populate each with at minimum 5 example favorable clause variants (25+ total). These are rewritten versions of risky clauses that favor the signing party — they serve as RAG references for counter-offer generation.

In `scripts/index_favorable_clauses.py`, implement the seeding script: read all favorable clause files, embed each, store in the `embeddings` table with `embedding_type = "favorable_clause"` and the clause type as metadata, and print the total indexed.

In `services/ai/pipelines/counter_offer.py`, implement the counter-offer generator from PRD.md Feature 6. The function accepts a HIGH-risk clause with its risk category, embeds it, retrieves the top similar favorable clause variant from pgvector filtered by `embedding_type = "favorable_clause"` and clause type, calls PRIMARY_MODEL with `counter_offer.txt` injecting the original clause, retrieved reference, contract type, and user role, parses the response into a `CounterOfferResult` Pydantic model containing aggressive, balanced, conservative versions plus the negotiation email, and stores in `counter_offers`.

In `apps/worker/tasks/generate_counter_offer.py`, implement the Celery task that calls this pipeline. This task is triggered on-demand (not part of the main scan task).

In `services/api/app/api/v1/endpoints/counter_offer.py`, implement `POST /api/v1/counter-offer/{clauseId}`. Verify JWT and ownership, check if a counter-offer already exists (return it immediately if so), otherwise queue the `generate_counter_offer` task, and return `202 Accepted` with the task status. Implement `GET /api/v1/counter-offer/{clauseId}` to poll for the result.

**Verification:**
- `python scripts/index_favorable_clauses.py` indexes at least 25 records
- Run the counter-offer pipeline directly for an IP assignment clause — confirm three versions are generated and are all different from each other
- The `negotiation_email` is 2 sentences in a professional tone
- `curl -X POST -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/counter-offer/<clauseId>` triggers the task and returns `202`
- Polling `GET /api/v1/counter-offer/<clauseId>` eventually returns the three counter-offer versions

---

## PHASE 8 — RAG Chat Pipeline

---

### STEP 8.1 — Implement the Contract Embedding Pipeline

In `services/ai/utils/chunk_splitter.py`, implement the overlapping chunk splitter: accept a text string, split into chunks of approximately 500 tokens (estimate ~4 chars per token), with a 50-token overlap between adjacent chunks, and return an array of chunk strings.

In `services/ai/rag/embedder.py`, implement the contract embedding function: accept a text string, split into chunks using `chunk_splitter`, embed each chunk using sentence-transformers `all-MiniLM-L6-v2` (load the model once as a singleton), and return an array of `{chunk_text, chunk_index, embedding_vector}` objects.

In `apps/worker/tasks/embed_contract.py`, implement the Celery task that: accepts `contract_id` and `contract_text`, runs the embedding pipeline, and stores all chunk embeddings in the `embeddings` table with `embedding_type = "contract_qa"` and the `contract_id`. This task is called at the end of the main scan task.

**Verification:**
- A 5-page contract text (approximately 2000 words) is split into between 8 and 40 chunks
- Adjacent chunks share content at the boundary (the last 50 tokens of chunk N appear at the start of chunk N+1)
- All embeddings are stored in the `embeddings` table with the correct `contract_id` and `embedding_type = "contract_qa"`
- A similarity search for "non-compete" against a contract's embeddings returns chunks containing non-compete language
- Similarity search results are scoped to a single contract — chunks from other contracts are not returned

---

### STEP 8.2 — Implement the Q&A Chat Pipeline and Endpoint

In `services/ai/rag/chat_chain.py`, implement the LangChain Q&A retrieval chain. Configure it with: the pgvector retriever scoped to a specific `contract_id` fetching the top 5 most similar chunks for the query, a system prompt instructing the model to always cite the clause or section it references and to say explicitly if the answer is not in the contract, and streaming enabled. The function accepts `question`, `contract_id`, and optional `conversation_history` (array of prior Q&A pairs), and returns a streaming generator that yields answer tokens.

In `services/api/app/api/v1/endpoints/chat.py`, implement `POST /api/v1/chat/{contractId}`. Verify JWT and ownership. Confirm the contract's embedding task is complete (check that `embeddings` rows exist for this contract). Accept a `ChatRequest` body. Call the chat chain and return a `StreamingResponse` with `text/event-stream` content type. Include the clause citation as a final event after streaming completes.

In `services/api/app/services/chat_service.py`, implement the orchestration logic that formats the conversation history and calls the chat chain.

**Verification:**
- `curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"question":"What are the notice periods?"}' http://localhost:8000/api/v1/chat/<contractId>` streams an answer for a contract that contains notice period language
- The answer contains a clause reference (e.g., "Section 4.2 states...")
- Asking about something not in the contract returns a response explicitly stating it is not addressed — not a hallucinated answer
- Sending a follow-up question with conversation history in the request body uses the prior context in the answer
- Calling the endpoint on a contract that hasn't been embedded yet returns `400` with a clear message

---

## PHASE 9 — Multilingual Support

---

### STEP 9.1 — Implement Language Detection and the DeepL Translation Wrapper

In `services/ai/translation/detector.py`, implement language detection using `langdetect`. Accept a text string (use only the first 500 characters for speed), return the detected language code as a string (e.g., "es", "fr", "de", "en"), and default to "en" on detection failure. Never raise an unhandled exception from this function.

In `services/ai/translation/translator.py`, implement the DeepL API wrapper. Functions needed: `translate_text(text, source_lang, target_lang)` for a single string, and `translate_batch(texts_array, source_lang, target_lang)` for a list of strings in one API call. Use the DeepL API key from environment variables. Handle rate limits and API errors gracefully by returning the original text if translation fails (with a warning log). Implement a bilingual legal glossary loaded from a JSON file at startup that maps jurisdiction-specific legal terms to their correct equivalents in each target language — apply glossary replacements after DeepL translation.

Create the glossary JSON file at `services/ai/translation/legal_glossary.json` with at minimum 20 legal terms mapped across all 6 supported languages (English, Spanish, French, German, Portuguese, Hindi).

**Verification:**
- `detector.detect_language("Este contrato establece los términos")` returns "es"
- `detector.detect_language("This agreement establishes the terms")` returns "en"
- `translator.translate_text("This agreement establishes the terms", "en", "es")` returns a Spanish translation
- `translator.translate_batch(["clause 1 text", "clause 2 text"], "en", "es")` makes exactly 1 DeepL API call (not 2)
- A key legal term like "indemnity" is correctly translated using the glossary, not just raw DeepL output

---

### STEP 9.2 — Integrate the Multilingual Pipeline and Post-Scan Translation

In `services/ai/pipelines/multilingual_pipeline.py`, implement the full multilingual orchestration pipeline from PRD.md Feature 11. Implement two functions:

`preprocess_contract(text)`: detect language, if non-English translate the full text to English, return `{english_text, original_language, was_translated}`.

`postprocess_results(clause_results, analysis_result, target_language)`: after all analysis is complete, translate all human-readable text fields back to `target_language` using batch translation. Fields to translate: `plain_english`, `worst_case_scenario`, `headline`, `scenario`, `one_liner`, all items in `top_3_concerns`, `top_2_positives`, `leverage_points`, and `negotiation_email`. Store both English and translated versions in the database.

The main Celery task already calls preprocess at step 4 and postprocess at step 16 — ensure both are fully wired.

In `apps/worker/tasks/translate_results.py`, implement the on-demand Celery task for post-scan language switching. It accepts `contract_id` and `target_language`, fetches all stored English results from the database, calls the postprocess function, and updates the stored records with the translated versions.

In `services/api/app/api/v1/endpoints/translate.py`, implement `POST /api/v1/translate/{contractId}`. Verify JWT and ownership. Accept a `TranslationRequest` body with `target_language`. Queue the `translate_results` Celery task. Return `202 Accepted` with the task ID.

**Verification:**
- Upload a Spanish-language PDF contract — after the scan, all `plain_english` fields in the `clauses` table should contain Spanish text (translated back)
- `curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"target_language":"fr"}' http://localhost:8000/api/v1/translate/<contractId>` queues the translation task and returns `202`
- After the task completes, re-fetching clause data shows `plain_english` in French
- An English contract is not translated (no DeepL call is made — verify via logs)
- Legal terms in translated results match the glossary mappings, not raw DeepL output

---

## PHASE 10 — Scan Status and History Endpoints

---

### STEP 10.1 — Implement Scan Status and Contract History Endpoints

In `services/api/app/api/v1/endpoints/analysis.py`, implement all contract and scan status endpoints:

`POST /api/v1/scan/{contractId}` — manually trigger or retrigger a scan for a contract the user owns. Verify JWT and ownership. If a scan is already complete, return the existing results. If failed, reset and requeue.

`GET /api/v1/scan/{jobId}` — return the current `ScanJobStatus` (status, progress_pct, error_message if any). No auth bypass — verify JWT and ownership.

`GET /api/v1/contracts` — return a list of all contracts for the authenticated user, with each contract's: `contract_id`, `original_filename`, `contract_type`, `detected_language`, `created_at`, and `overall_risk_score` (from `analysis_results` if complete, null otherwise).

`GET /api/v1/contracts/{contractId}` — return the full contract detail including all clause results, analysis result, and scan job status.

`DELETE /api/v1/contracts/{contractId}` — soft-delete or hard-delete the contract and all associated data for the authenticated user.

**Verification:**
- `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/scan/<jobId>` returns `{"status": "complete", "progress_pct": 100}` for a finished scan
- `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/contracts` returns an array of the user's contracts
- `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/contracts/<contractId>` returns full contract detail including all clause objects
- Accessing another user's contract returns `403`
- Deleting a contract removes its data and subsequent `GET` returns `404`

---

## PHASE 11 — Report Generation

---

### STEP 11.1 — Build the Jinja2 PDF Report Templates

In `services/api/templates/`, create the Jinja2 HTML templates for the PDF report from PRD.md Feature 12. Create `base.html` with: overall layout, Jinja2 block definitions for each section, color variables for risk levels (HIGH=red, MEDIUM=amber, LOW=green, SAFE=grey), embedded professional-looking CSS for print layout, and a logo placeholder. Create section templates: `cover.html`, `summary.html`, `clauses.html`, `power.html`, `precedent.html`, `counter_offers.html`. The CSS in `static/report.css` must include proper page-break rules to prevent clauses or case citations from being cut mid-page.

Create all 6 i18n language string files in `templates/i18n/`: `en.json`, `es.json`, `fr.json`, `de.json`, `pt.json`, `hi.json`. Each file must contain translated labels for all static report text: section headings, risk level labels, verdict labels, footer disclaimer, etc.

**Verification:**
- Render `base.html` with dummy Jinja2 context data — confirm it produces valid HTML with no template errors
- `weasyprint` can convert the rendered HTML to a PDF without raising errors: `python -c "from weasyprint import HTML; HTML(string='<h1>Test</h1>').write_pdf('/tmp/test.pdf')"`
- The generated test PDF is a valid PDF file (non-zero bytes, opens correctly)
- All 6 i18n JSON files exist and contain at minimum 10 label keys each

---

### STEP 11.2 — Implement the PDF Generation Service and Report Endpoints

In `services/api/app/utils/pdf_generator.py`, implement the PDF generation function. It must: accept a `contract_id` and `language`, fetch all associated data from the database (contract metadata, all clauses sorted by position, analysis result, counter-offers, precedent matches), select the correct i18n JSON file based on language, render each template section with the data using Jinja2, concatenate sections into a complete HTML document, convert to PDF using WeasyPrint, save to a path under a `reports/` directory, and return the file path.

In `services/api/app/services/report_service.py`, implement: `create_report_record(contract_id, language)` — generates a UUID for the share link, calculates the 48-hour expiry timestamp, creates a `Report` record in the database. `get_report(report_id, user_id)` — fetches and returns the report if owned by the user. `get_report_by_share_uuid(share_uuid)` — fetches the report without authentication check, but verifies it has not expired.

In `apps/worker/tasks/generate_report.py`, implement the Celery task that calls `pdf_generator.py` and updates the report record with the PDF path.

In `services/api/app/api/v1/endpoints/report.py`, implement:
`POST /api/v1/report/generate/{contractId}` — verify JWT and ownership, create the report record, queue the `generate_report` Celery task, return `202 Accepted` with the report ID.
`GET /api/v1/report/{reportId}` — verify JWT and ownership, return the PDF as a file download response or a JSON record with the PDF path and share URL.
`GET /api/v1/report/share/{shareUuid}` — public endpoint (no JWT required), fetch report by share UUID, verify it has not expired, return the PDF as a file download or the report data as JSON. Return `410 Gone` if expired.

**Verification:**
- `curl -X POST -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/report/generate/<contractId>` triggers report generation and returns a report ID
- After the Celery task runs, `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/report/<reportId>` returns the report data including a `share_url`
- `curl http://localhost:8000/api/v1/report/share/<shareUuid>` works without authentication and returns the report data
- Manually set a report's `expires_at` to a time in the past — the same share UUID call should return `410 Gone`
- The generated PDF file is non-zero bytes and opens correctly as a PDF

---

### STEP 11.3 — Implement the Report Cleanup Celery Beat Task

In `apps/worker/tasks/cleanup_expired_reports.py`, implement the Celery Beat periodic task. It must: query the database for all `Report` records where `expires_at < NOW()`, for each expired report attempt to delete the PDF file from the filesystem (log a warning if the file is missing but do not crash), delete the report record from the database, and log the total number of reports cleaned up in this run.

In `apps/worker/celery_app.py`, configure Celery Beat to schedule `cleanup_expired_reports` on an hourly interval.

**Verification:**
- Manually create a report record with `expires_at` set 1 hour in the past and the PDF file on disk
- Call the task directly: `celery -A celery_app call cleanup_expired_reports`
- Confirm the report record no longer exists in the database
- Confirm the PDF file has been deleted from disk
- A report with `expires_at` in the future is NOT deleted
- Confirm the task appears in the Celery Beat schedule: `celery -A celery_app beat --loglevel=debug`

---

## PHASE 12 — Caching Layer

---

### STEP 12.1 — Implement the Redis Result Cache

In `services/ai/cache/result_cache.py`, implement the result caching utility. Functions needed:

`get_cache_key(contract_text)`: generate a SHA-256 hash of the contract text content (stripped of whitespace) — this is the cache key. Never use the filename as part of the key.

`get_cached_results(contract_text)`: check Redis for a cached scan result using the content hash as the key. If found, return the deserialized results. If not found, return `None`.

`store_results(contract_text, results, ttl_days=7)`: serialize the full results dict and store in Redis with a TTL of 7 days.

`invalidate_cache(contract_text)`: delete the cached result for the given content hash.

In `services/ai/cache/cache_config.py`, define constants: default TTL, key prefix convention (e.g., `scan_result:`), and any Redis connection settings.

Integrate the cache check as the very first step in the main Celery scan task (`process_contract.py`): if a cache hit is found, publish the cached clause results to the SSE channel directly and mark the scan job as complete without any LLM or parsing calls. Store results in the cache at the end of every new scan.

**Verification:**
- Run a full scan on a contract — confirm a cache key is stored in Redis after completion (`redis-cli KEYS "scan_result:*"`)
- Upload the exact same contract a second time — confirm the second scan completes in under 2 seconds and no LLM calls appear in the AI service logs
- Rename the file and upload again — confirm the cache is still hit (content hash, not filename)
- Call `invalidate_cache` manually — confirm the key is removed from Redis and the next scan does a full LLM run

---

### STEP 12.2 — Pre-Compute Demo Contract Results

In `services/ai/data/synthetic_contracts/`, create 3 demo contract files: a freelance agreement (containing at least one IP assignment clause and one non-compete clause), an employment contract (containing at least one non-compete and one automatic renewal clause), and an NDA (containing indemnity and governing law clauses). These should be realistic plain-text contracts of at least 5 pages each.

In `scripts/seed_demo_contracts.py`, implement the pre-computation script: for each of the 3 demo contracts, run the full scan pipeline, and store the results in Redis with no TTL (TTL = 0 means permanent). Log the cache key for each contract so it can be referenced in documentation.

**Verification:**
- `python scripts/seed_demo_contracts.py` runs without errors and logs 3 cache keys
- Uploading the demo freelance agreement contract triggers a cache hit and completes in under 3 seconds
- The cached freelance agreement result contains at least one HIGH-risk IP assignment clause
- The cached NDA result contains at least one HIGH-risk indemnity clause

---

## PHASE 13 — Rate Limiting

---

### STEP 13.1 — Implement API Rate Limiting

Configure rate limiting using Upstash Redis (the same Redis instance used for Celery). Implement a rate limiter middleware or per-endpoint dependency in `services/api/app/core/` using a sliding window algorithm backed by Redis atomic operations. Apply rate limits exactly as defined in PRD.md Section 7.4:

- Upload endpoint: 10 uploads per user per hour
- Scan endpoint: 10 scans per user per hour
- Chat endpoint: 100 messages per user per day
- Counter-offer endpoint: 50 requests per user per day

All rate limit keys must be scoped to the authenticated user ID so limits are per-user, not global. On limit exceeded, return `429 Too Many Requests` with a `Retry-After` header indicating when the limit resets.

**Verification:**
- Make 11 rapid upload requests with the same user token — the 11th returns `429`
- The `429` response includes a `Retry-After` header with a valid timestamp
- Rate limits are per-user: two different users can each make 10 uploads without blocking each other
- After the window resets (simulate by moving the Redis key TTL to 0), requests succeed again

---

## PHASE 14 — Testing

---

### STEP 14.1 — Backend Unit Tests

In `services/api/tests/unit/`, write unit tests for all service layer functions using pytest and pytest-asyncio. Mock all external dependencies (LLM calls, Redis, database) — no real network calls. Cover: `contract_service`, `analysis_service`, `report_service`, `chat_service`, `translation_service`, `streaming_service`. In `services/ai/tests/test_pipelines.py`, write unit tests for all pipeline functions with mocked LLM responses — confirm Pydantic validation is applied correctly and that mock responses in the right shape parse without error. In `services/ai/tests/test_rules.py`, write unit tests for the rule engine — test every regex pattern with at least one matching clause and one non-matching clause.

**Verification:**
- `pytest services/api/tests/unit/ -v` passes with all tests green
- `pytest services/ai/tests/ -v` passes with all tests green
- No test makes a real LLM call or database call (verified by checking that tests complete even with invalid API keys)
- Rule engine tests achieve coverage of all 40+ regex patterns
- Service layer test coverage is above 80%: `pytest --cov=app/services services/api/tests/unit/`

---

### STEP 14.2 — Backend Integration Tests

In `tests/` (root) and `services/api/tests/integration/`, write integration tests using the `docker-compose.test.yml` environment. Use `httpx.AsyncClient` with the FastAPI app in test mode. Use a real test database (not mocked). Seed the test database with known contract and user data before each test class.

Write tests for: the full upload-to-scan pipeline end-to-end (upload endpoint → Celery task → database results), SSE streaming delivering at least one clause event for a known contract, the chat endpoint returning a non-hallucinated answer for a seeded contract, the translation endpoint switching a contract's language and updating stored results, report generation producing a non-empty PDF, the share link endpoint working without authentication, and the cleanup task correctly deleting an expired report.

**Verification:**
- `pytest tests/ -v` passes with all tests green (requires `docker-compose.test.yml` running)
- The full scan pipeline integration test completes in under 60 seconds
- The SSE test receives at least one `data:` event line
- The chat test asserts the response does NOT contain fabricated contract terms

---

### STEP 14.3 — API Pipeline Smoke Test Script

Create `scripts/test_full_pipeline.py` — a standalone script (not a pytest test) that exercises the full backend API flow end to end using a hardcoded demo contract file. The script should: call the upload endpoint, open the SSE stream and read until complete, call the summary endpoint, call the power endpoint, call the counter-offer endpoint for the first HIGH-risk clause, call the chat endpoint with a question, generate a report and verify the share link works. Print a pass/fail result for each step. This script is useful for manual verification after deployments.

**Verification:**
- `python scripts/test_full_pipeline.py` runs against the local backend and prints "PASS" for every step
- Any network error or unexpected status code prints "FAIL" for that step and continues to the next
- The script completes within 120 seconds for a normal scan

---

## PHASE 15 — CI/CD and Deployment

---

### STEP 15.1 — Set Up GitHub Actions CI for the Backend

In `.github/workflows/ci.yml`, create the CI pipeline that runs on every pull request and push to main. It must run: backend linting with ruff or flake8 across all Python services, backend type checking (if using mypy), unit tests for the API service, unit tests for the AI service, and integration tests using `docker-compose.test.yml`. The pipeline must fail fast. Use GitHub Actions service containers for Postgres and Redis instead of full docker-compose where possible for speed.

**Verification:**
- Opening a pull request triggers the CI pipeline automatically
- A failing unit test causes the pipeline to fail and the PR shows a red status
- All existing tests pass on the `main` branch (green status)

---

### STEP 15.2 — Deploy the Backend to Railway

Deploy the FastAPI API service, the AI service, and the Celery worker to Railway as three separate services. Configure: the `services/api/Dockerfile` for the API service on Railway, the `services/ai/Dockerfile` for the AI service, the `apps/worker/Dockerfile` for the Celery worker, all backend environment variables in Railway's dashboard using the `.env.example` as the reference, the Neon database URL as `DATABASE_URL`, and the Upstash Redis URL as `REDIS_URL`. Configure Railway to run database migrations automatically as a deploy step: add `alembic upgrade head` to the API service's start command or as a pre-deploy hook. Run the seeding scripts (`seed_precedents.py`, `index_favorable_clauses.py`, `seed_demo_contracts.py`) once against the production database after first deployment.

**Verification:**
- All three services are running on Railway with a green status
- `curl https://<railway-api-url>/health` returns `{"status": "ok", "service": "api"}`
- `curl https://<railway-api-url>/api/v1/scan/fake-id` returns `401` (auth is working in production)
- `alembic current` on the production database shows migrations are applied
- The Celery worker shows as connected in its Railway logs
- `python scripts/test_full_pipeline.py` pointed at the production URL passes all steps

---

### STEP 15.3 — Final Backend Production Verification

This is the final verification step for the complete backend. Test every feature via curl or a REST client against the production deployment.

**Verification:**
- Upload a real PDF contract — scan job is created and scan completes successfully
- SSE stream delivers clause-by-clause results
- At least one HIGH-risk clause is detected and stored
- Summary endpoint returns `should_you_sign` and `overall_risk_score`
- Power endpoint returns a `power_score` with `key_imbalances`
- Precedent endpoint for a HIGH-risk clause returns at least one case citation
- Counter-offer endpoint returns three versions for a HIGH-risk clause
- Chat endpoint answers a question about the contract with a clause citation and does not fabricate terms
- Report generation produces a downloadable PDF
- The share link for the report works without authentication
- Uploading a Spanish contract — after scan, clause `plain_english` fields contain Spanish text
- Switching language to French via the translate endpoint re-translates all fields to French
- Uploading the same contract twice — second scan returns from cache in under 3 seconds
- Uploading demo contract files — results return in under 3 seconds from pre-computed cache
- The rate limiter blocks the 11th upload attempt in under an hour

---

## Build Order Summary

```
PHASE 0  — Repository & Environment Setup     (Steps 0.1–0.6)
PHASE 1  — Database Foundation                (Steps 1.1–1.4)
PHASE 2  — Authentication                     (Steps 2.1–2.2)
PHASE 3  — File Upload Pipeline               (Steps 3.1–3.2)
PHASE 4  — Document Parsing Pipeline          (Steps 4.1–4.4)
PHASE 5  — LLM Integration Foundation        (Steps 5.1–5.3)
PHASE 6  — Core Scan Pipeline                 (Steps 6.1–6.6)
PHASE 7  — Remaining AI Feature Pipelines    (Steps 7.1–7.6)
PHASE 8  — RAG Chat Pipeline                  (Steps 8.1–8.2)
PHASE 9  — Multilingual Support               (Steps 9.1–9.2)
PHASE 10 — Scan Status and History Endpoints  (Step 10.1)
PHASE 11 — Report Generation                  (Steps 11.1–11.3)
PHASE 12 — Caching Layer                      (Steps 12.1–12.2)
PHASE 13 — Rate Limiting                      (Step 13.1)
PHASE 14 — Testing                            (Steps 14.1–14.3)
PHASE 15 — CI/CD and Deployment               (Steps 15.1–15.3)
```

**Total: 39 steps across 15 phases. Complete every verification before proceeding to the next step.**

---

## Appendix — API Endpoint Reference

All endpoints below are prefixed with `/api/v1`. All except `/health` and `/webhooks/clerk` and `/report/share/{shareUuid}` require a valid Clerk JWT in the `Authorization: Bearer` header.

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check — no auth |
| POST | /webhooks/clerk | Clerk user sync webhook — no auth, but webhook signature required |
| POST | /upload | Upload a contract file URL and start a scan job |
| GET | /scan/{jobId} | Get the status and progress of a scan job |
| GET | /scan/{jobId}/stream | SSE stream — delivers clause results in real time |
| GET | /contracts | List all contracts for the authenticated user |
| GET | /contracts/{contractId} | Get full contract detail including all clauses |
| DELETE | /contracts/{contractId} | Delete a contract and all associated data |
| GET | /summary/{contractId} | Get the summary card and pros/cons for a completed scan |
| GET | /power/{contractId} | Get the power asymmetry analysis |
| GET | /precedent/{clauseId} | Get the legal precedent match for a HIGH-risk clause |
| POST | /counter-offer/{clauseId} | Queue counter-offer generation for a HIGH-risk clause |
| GET | /counter-offer/{clauseId} | Get the generated counter-offer (poll after POST) |
| POST | /chat/{contractId} | Ask a question about the contract — streams the answer |
| POST | /translate/{contractId} | Queue a post-scan translation to a different language |
| POST | /report/generate/{contractId} | Queue PDF report generation |
| GET | /report/{reportId} | Get the report (authenticated) |
| GET | /report/share/{shareUuid} | Get the report via share link — no auth, checks expiry |

---

*This document covers the complete backend build. No frontend code is referenced. Every feature in PRD.md has a corresponding backend implementation step here. Use the frontend document separately when building the UI layer on top of these endpoints.*