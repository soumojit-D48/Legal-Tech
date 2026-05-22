# STEPS.md — LegalTech AI Contract Scanner
**Build Order & Execution Guide**
**Read PRD.md, TECH_STACK.md, and FOLDER_STRUCTURE.md before starting any step.**

---

## How to Use This Document

Each step is self-contained. Complete it fully, run the verification checklist at the end of the step, and only move to the next step when every verification item passes. Never skip a step. Never partially complete a step and move on. If a verification fails, fix it before proceeding.

Steps are ordered so that every dependency is in place before it is needed. Infrastructure before services. Services before features. Features before UI. UI before integration.

---

## PHASE 0 — Repository & Environment Setup

---

### STEP 0.1 — Initialize the Monorepo Root

Create the root directory `legaltech-ai/`. Initialize a git repository. Create the top-level folder structure exactly as defined in FOLDER_STRUCTURE.md: the `apps/`, `services/`, `packages/`, `infra/`, `scripts/`, `tests/`, and `.github/workflows/` directories. Create an empty `docker-compose.yml`, `docker-compose.test.yml`, `.gitignore`, and `README.md` at the root. The `.gitignore` must cover Node modules, Python virtual environments, `.env` files, compiled files, and OS artifacts. The `README.md` should briefly describe the project and reference the three documentation files.

**Verification:**
- Root directory structure matches FOLDER_STRUCTURE.md exactly at the top level
- Git is initialized and first commit is made
- `.gitignore` prevents committing `node_modules/`, `__pycache__/`, `.env`, `*.pyc`, `.DS_Store`

---

### STEP 0.2 — Create the Root Environment Variable Template

Create `.env.example` at the monorepo root with every environment variable key listed in FOLDER_STRUCTURE.md's environment variables section. All values must be empty placeholders — no real secrets. Group them by section: Frontend, Backend API, AI Service, Shared. Create a copy of this file as `.env` at the root (this `.env` is gitignored). Document what each variable is and where to obtain it as an inline comment next to every key.

**Verification:**
- `.env.example` exists at root with all variable keys present and grouped
- `.env` exists at root and is gitignored
- Every variable from FOLDER_STRUCTURE.md's env section is present

---

### STEP 0.3 — Initialize the Frontend App

Inside `apps/web/`, initialize a Next.js 15 application using the App Router. Use TypeScript. Configure TailwindCSS v4 immediately after initialization. Install and configure Shadcn/ui — run its init command and accept all defaults. Install Framer Motion, Zustand, and React PDF. Install the Uploadthing Next.js package. Set up the `next.config.ts` with any necessary configuration for the project (image domains, environment variable exposure, etc.). Create the `components.json` for Shadcn/ui. Create the base `app/layout.tsx`, `app/page.tsx`, and `app/globals.css` with only minimal placeholder content — a heading that says "LegalTech AI" is sufficient for now.

**Verification:**
- `npm run dev` starts without errors on port 3000
- The landing page renders the placeholder heading
- TailwindCSS classes apply correctly (test with a utility class on the heading)
- No TypeScript errors on startup

---

### STEP 0.4 — Initialize the Backend API Service

Inside `services/api/`, create a Python virtual environment. Install all packages from the backend section of TECH_STACK.md into `requirements.txt`. Create the FastAPI `app/main.py` with only: app initialization, CORS middleware configured to allow the frontend origin, and a single `GET /health` endpoint that returns `{"status": "ok"}`. Create `app/core/config.py` using Pydantic BaseSettings to load all backend environment variables from `.env`. Create `uvicorn` startup in a `run.py` or equivalent. Create the `Dockerfile` for the API service.

**Verification:**
- `uvicorn app.main:app --reload` starts without errors on port 8000
- `GET /health` returns `{"status": "ok"}`
- CORS headers are present in the response when called from localhost:3000
- All environment variables load without errors via Pydantic Settings

---

### STEP 0.5 — Initialize the AI Service

Inside `services/ai/`, create a Python virtual environment. Install all AI-specific packages: spaCy with the `en_core_web_sm` model, sentence-transformers, langdetect, langchain, langchain-openai, PyMuPDF, python-docx, unstructured (pdf and docx extras only — not the full package), httpx, and python-dotenv. Create a minimal `main.py` or `__init__.py` that confirms all imports succeed. Create all subdirectories defined in FOLDER_STRUCTURE.md under `services/ai/`: `pipelines/`, `prompts/`, `models/`, `rag/`, `rules/`, `parser/`, `translation/`, `cache/`, `data/`, `utils/`. Create empty `__init__.py` files in each. Create the `Dockerfile` for the AI service.

**Verification:**
- All imports succeed without errors: spaCy, sentence_transformers, langdetect, langchain, fitz (PyMuPDF), docx, httpx
- `python -m spacy download en_core_web_sm` completes successfully
- `from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')` downloads and loads the model
- All subdirectories exist with `__init__.py` files

---

### STEP 0.6 — Initialize the Worker

Inside `apps/worker/`, create a Python virtual environment. Install Celery, Redis client, and any shared dependencies needed for task processing. Create `celery_app.py` with Celery initialization configured to use the Redis URL from environment variables. Create the `tasks/` directory with empty placeholder files for each task listed in FOLDER_STRUCTURE.md. Create the `Dockerfile` for the worker.

**Verification:**
- `celery -A celery_app worker --loglevel=info` starts without errors (even if no tasks are registered yet)
- Celery connects to Redis successfully (requires Redis running — use Docker for local Redis)

---

### STEP 0.7 — Set Up Docker Compose for Local Development

Write the `docker-compose.yml` at the root to orchestrate all services: `web` (Next.js on port 3000), `api` (FastAPI on port 8000), `ai` (AI service on port 8001), `worker` (Celery), `redis` (Redis on port 6379), `db` (PostgreSQL on port 5432). Configure environment variable injection from the root `.env` file into each service. Configure volume mounts for hot-reload during development. Write the `docker-compose.test.yml` for isolated test environments with a separate Postgres and Redis instance. Write `infra/nginx/nginx.conf` as a reverse proxy routing `/api` to FastAPI and `/` to Next.js. Add local SSL certificate placeholders in `infra/nginx/local-ssl/` — the WebCrypto API requires HTTPS even on localhost.

**Verification:**
- `docker-compose up` brings all services up without errors
- `GET http://localhost:8000/health` returns `{"status": "ok"}`
- `GET http://localhost:3000` renders the placeholder Next.js page
- Redis is reachable from the worker container
- PostgreSQL is reachable from the API container

---

## PHASE 1 — Database Foundation

---

### STEP 1.1 — Configure Database Connection

In `services/api/app/db/session.py`, set up the SQLAlchemy async engine using `asyncpg` as the driver, connected to the Neon PostgreSQL URL from environment variables. Configure the async session factory with appropriate connection pool settings. Create the `app/db/base.py` that imports the declarative base and will later import all models for Alembic discovery. Initialize Alembic in the `migrations/` directory with `alembic init`. Configure `alembic.ini` and `migrations/env.py` to use the async engine and to discover models from `app/db/base.py`.

**Verification:**
- SQLAlchemy async engine connects to the database without errors
- Alembic `alembic current` runs without errors (even if no migrations exist yet)

---

### STEP 1.2 — Create All Database Models

In `services/api/app/models/`, create every ORM model defined in FOLDER_STRUCTURE.md and specified in PRD.md Section 4.3. Create models for: `User`, `Contract`, `Clause`, `ScanJob`, `AnalysisResult`, `CounterOffer`, `PrecedentMatch`, `Report`, and `Embedding`. Each model must have: a UUID primary key, appropriate foreign keys and relationships, `created_at` and `updated_at` timestamp columns with auto-population, and all columns defined in PRD.md's database schema section. The `Embedding` model must use the `pgvector` Vector column type for the embedding field. Import all models in `app/db/base.py`.

**Verification:**
- All model files exist and import without errors
- All models are imported in `app/db/base.py`
- No circular import errors

---

### STEP 1.3 — Create and Run Initial Migration

Generate the first Alembic migration using autogenerate against the models created in Step 1.2. Review the generated migration file to ensure all tables, columns, foreign keys, indexes, and the pgvector extension are correctly represented. The migration must also enable the `pgvector` extension in Postgres (`CREATE EXTENSION IF NOT EXISTS vector`). Run the migration against the development database.

**Verification:**
- Migration file exists in `migrations/versions/`
- `alembic upgrade head` runs without errors
- All 9 tables exist in the database: `users`, `contracts`, `clauses`, `scan_jobs`, `analysis_results`, `counter_offers`, `precedent_matches`, `reports`, `embeddings`
- The `vector` column type is correctly created on the `embeddings` table
- `alembic current` shows the migration as applied

---

### STEP 1.4 — Create Repository Layer

In `services/api/app/repositories/`, create a repository file for each entity: `user_repo.py`, `contract_repo.py`, `clause_repo.py`, `scan_job_repo.py`, `precedent_repo.py`, and `report_repo.py`. Each repository must implement only async database query functions — no business logic. Standard functions per repository: `create`, `get_by_id`, `get_all_by_user`, `update`, `delete`. The `scan_job_repo` must also have `update_status` and `update_progress` functions. The `report_repo` must have `get_by_share_uuid` and `delete_expired` functions. All functions must use the async session and properly handle not-found cases.

**Verification:**
- All repository files exist and import without errors
- Each repository can be instantiated and called with a mock async session without errors
- No business logic in any repository — only raw queries

---

## PHASE 2 — Authentication

---

### STEP 2.1 — Configure Clerk in the Backend

In `services/api/app/core/security.py`, implement Clerk JWT verification. Every protected API endpoint will call this verification function. It must: extract the Bearer token from the Authorization header, verify it against Clerk's public key (fetched from Clerk's JWKS endpoint), extract the user ID (`sub` claim) from the verified token, and return the user ID. Create a FastAPI dependency function wrapping this verification so it can be injected into any endpoint with a single line. Create the `app/api/v1/endpoints/auth.py` endpoint that handles the Clerk webhook for user creation/update events — when Clerk fires a user.created webhook, create or upsert the user record in the `users` table.

**Verification:**
- A request to a protected endpoint with no token returns 401
- A request with an invalid token returns 401
- A request with a valid Clerk token returns the correct user ID
- The Clerk webhook endpoint accepts a user.created event and creates a user in the database

---

### STEP 2.2 — Configure Clerk in the Frontend

Install and configure Clerk in the Next.js frontend. Wrap the root `app/layout.tsx` with the Clerk provider. Create `middleware.ts` at the `apps/web/` root — this is the Clerk auth middleware that protects all routes under the `(app)/` route group. Any unauthenticated request to an `(app)/` route must redirect to `/sign-in`. Create the `(auth)/sign-in/page.tsx` and `(auth)/sign-up/page.tsx` pages using Clerk's pre-built components. Create the `api/webhooks/clerk/route.ts` Next.js API route to forward Clerk webhook events to the FastAPI backend.

**Verification:**
- Visiting any `(app)/` route while logged out redirects to `/sign-in`
- The sign-in page renders Clerk's sign-in component
- Signing in with Google or GitHub redirects to the dashboard
- After login, the Clerk JWT is available in the session and can be retrieved client-side
- The webhook route exists and returns 200

---

### STEP 2.3 — Set Up Authenticated API Client

In `apps/web/lib/api.ts`, create the typed API client that all frontend components will use to communicate with FastAPI. It must: automatically attach the Clerk JWT as a Bearer token on every request, handle 401 responses by redirecting to sign-in, handle network errors gracefully, and be fully typed with TypeScript generics so each call returns a typed response. Create the base TypeScript types in `apps/web/types/` that mirror the Pydantic schemas — `scan.ts`, `report.ts`, `chat.ts`, `api.ts`.

**Verification:**
- An authenticated API call to `GET /health` from the frontend returns `{"status": "ok"}`
- An unauthenticated call returns 401 and triggers redirect
- TypeScript types are correctly defined and match the API response shapes

---

## PHASE 3 — File Upload with Encryption

---

### STEP 3.1 — Implement Client-Side Encryption

In `apps/web/lib/crypto.ts`, implement the WebCrypto AES-256-GCM encryption utilities. This module must provide: a function to generate an AES-256-GCM key using `window.crypto.subtle.generateKey`, a function to encrypt an `ArrayBuffer` (the file bytes) using the generated key and return the encrypted buffer plus the IV, and a function to export the key as a hex string for display to the user. In `apps/web/hooks/useEncryption.ts`, wrap these utilities as a React hook that manages the key lifecycle: generates the key when a file is selected, encrypts the file, holds the key in component state (never in localStorage or sessionStorage), and clears the key on session end.

**Verification:**
- `generateKey()` produces a CryptoKey object
- Encrypting a test file produces a different byte sequence than the original
- The same key can decrypt the encrypted file back to the original bytes
- The key is not persisted anywhere — refreshing the page loses the key
- Runs only in a secure context (HTTPS or localhost)

---

### STEP 3.2 — Implement File Upload

Configure Uploadthing in the backend API: create the Uploadthing file router in `apps/web/app/api/uploadthing/route.ts`. Define allowed file types (PDF, DOCX) and maximum file size (25MB). In `apps/web/hooks/useUpload.ts`, implement the upload hook that: takes an encrypted file blob, uploads it via Uploadthing, and returns the file URL and reference key. In `apps/web/features/upload/UploadZone.tsx`, build the drag-and-drop upload area component. In `apps/web/features/upload/UploadProgress.tsx`, build the progress bar component. In `apps/web/features/upload/EncryptionBadge.tsx`, build the lock icon + "Encrypted before upload" text component that animates in during the upload process. In `apps/web/features/upload/EncryptionStatus.tsx`, build the post-session status component that shows the truncated key hash and deletion confirmation.

**Verification:**
- A PDF file can be drag-and-dropped onto the upload zone
- The encryption badge animates in during upload
- The file is encrypted before the upload starts (verify by checking the uploaded file is not readable as a PDF)
- The upload completes and returns a valid Uploadthing URL
- The upload zone rejects non-PDF/DOCX files with an error message
- Files over 25MB are rejected

---

### STEP 3.3 — Create the Upload API Endpoint and Contract Record

In `services/api/app/api/v1/endpoints/upload.py`, create the `POST /upload` endpoint. It must: verify the Clerk JWT (use the auth dependency), receive the Uploadthing file URL and file metadata (original filename, file type, file size) from the request body, create a new `Contract` record in the database with the user ID and file reference, create a new `ScanJob` record with status "queued", trigger the Celery scan task (passing the contract ID and file URL), and immediately return the `job_id` and `contract_id` to the frontend. In `services/api/app/services/contract_service.py`, implement the business logic for contract creation.

**Verification:**
- `POST /upload` with a valid JWT and file URL creates a Contract record in the database
- A ScanJob record is created with status "queued"
- The endpoint returns both `job_id` and `contract_id`
- The endpoint returns 401 without a valid JWT
- The Celery task is queued (visible in Celery logs)

---

## PHASE 4 — Document Parsing Pipeline

---

### STEP 4.1 — Implement PDF Parser

In `services/ai/parser/pdf_parser.py`, implement PDF text extraction using PyMuPDF (fitz). The parser must: open the uploaded PDF from a URL or file path, extract text page by page, preserve paragraph structure and line breaks, handle multi-column layouts by reading in reading order, strip headers and footers that repeat across pages, and return a single cleaned text string. It must handle password-protected PDFs gracefully (return an error, do not crash). It must handle scanned PDFs that have no extractable text (return an empty string and flag the document as requiring OCR).

**Verification:**
- A standard PDF contract is parsed and returns readable text
- A multi-page PDF returns text from all pages
- A password-protected PDF returns an appropriate error without crashing
- A scanned image PDF returns an empty string with a flag (does not crash)
- Repeated headers/footers are stripped or at least not duplicated excessively

---

### STEP 4.2 — Implement DOCX Parser

In `services/ai/parser/docx_parser.py`, implement DOCX text extraction using python-docx. The parser must: open the DOCX file, extract text from all paragraphs in document order, preserve section structure using heading styles as section delimiters, extract text from tables within the document, and return a single cleaned text string. Handle DOCX files with unusual or missing styles gracefully.

**Verification:**
- A standard DOCX contract is parsed and returns readable text
- Headings are preserved in the output
- Table content is included in the output
- An empty DOCX does not crash the parser

---

### STEP 4.3 — Implement Fallback Parser

In `services/ai/parser/fallback_parser.py`, implement the unstructured.io fallback parser. This is used when PyMuPDF fails to extract meaningful text (e.g., scanned documents, heavily formatted PDFs). Use only the `unstructured[pdf,docx]` extras — not the full package. The fallback parser should accept a file path and file type and return cleaned text. Create a unified `parse_document` dispatcher function in a `parser/__init__.py` or similar that: tries the appropriate primary parser (PDF or DOCX based on file type), checks if the output is meaningful (more than 100 characters of text), and falls back to the unstructured parser if the primary parser returns insufficient content.

**Verification:**
- The dispatcher correctly calls the PDF parser for `.pdf` files
- The dispatcher correctly calls the DOCX parser for `.docx` files
- If the PDF parser returns less than 100 characters, the fallback is called
- The fallback parser returns text from a scanned PDF

---

### STEP 4.4 — Implement Clause Segmentation

In `services/ai/pipelines/clause_extraction.py`, implement clause segmentation using spaCy's `en_core_web_sm` model. The segmenter must: load the spaCy model, split the contract text into sentence-level units, group adjacent sentences that belong to the same logical clause (using heuristics: numbered clauses, lettered sub-clauses, hanging sentences that are continuations), assign each clause a sequential `position_index`, and return an array of clause objects, each with: `clause_id` (UUID), `position_index`, `text`, and `word_count`. Clauses under 10 words should be merged with the adjacent clause. Clauses over 500 words should be split at sentence boundaries.

**Verification:**
- A 10-page contract produces between 20 and 100 clauses (reasonable range)
- Each clause has a unique `clause_id`
- No clause is under 10 words
- No clause is over 500 words
- Numbered sections (1.1, 1.2, etc.) are preserved as separate clauses
- The `position_index` is sequential with no gaps

---

## PHASE 5 — LLM Integration Foundation

---

### STEP 5.1 — Implement the OpenRouter Client

In `services/ai/models/openrouter_client.py`, implement the async OpenRouter API client using httpx. It must: read the API key and model names from environment variables, support both standard (non-streaming) and streaming (`stream=True`) request modes, accept a system prompt, a user prompt, and a model name as parameters, enforce `response_format: json_object` for structured output calls, implement retry logic — up to 3 retries with exponential backoff on rate limit (429) and server error (5xx) responses, and log all requests and responses at DEBUG level. In `services/ai/models/model_config.py`, define the model name constants: PRIMARY_MODEL for Llama 3.3 70B and FAST_MODEL for Gemini Flash. In `services/ai/models/streaming.py`, implement the SSE streaming handler that consumes a streaming response from OpenRouter and yields parsed JSON events.

**Verification:**
- A non-streaming call to the PRIMARY_MODEL returns a valid JSON response
- A non-streaming call to the FAST_MODEL returns a valid JSON response
- A streaming call yields tokens progressively
- A simulated 429 response triggers retry with backoff
- An invalid API key returns a clear error message

---

### STEP 5.2 — Load All Prompt Templates

In `services/ai/prompts/`, create all 7 prompt template files as plain text: `risk_analysis.txt`, `type_detection.txt`, `consequence.txt`, `summary.txt`, `power_asymmetry.txt`, `counter_offer.txt`, `precedent.txt`. Each file must contain the exact system and user prompt structure defined in PRD.md Section 3 for the corresponding feature, with `{{placeholder}}` tokens for all dynamic values. Create a prompt loader utility in `services/ai/utils/` that reads a prompt file by name and performs `{{placeholder}}` substitution given a dictionary of values. This utility will be used by all pipeline files.

**Verification:**
- All 7 prompt files exist in `services/ai/prompts/`
- The prompt loader correctly substitutes all placeholders
- The prompt loader raises a clear error if a required placeholder is missing
- The prompt loader raises a clear error if a prompt file does not exist

---

### STEP 5.3 — Implement Pydantic Response Schemas

In `services/api/app/schemas/`, create all Pydantic v2 schema files for every API input and output. Start with the core schemas used by the scan pipeline: `clause.py` (ClauseResult with all fields from PRD.md Feature 1), `scan_job.py` (ScanRequest, ScanJobStatus, ScanResponse), `contract.py` (ContractCreate, ContractRead), `response.py` (RiskLevel enum, ContractType enum, all shared enums). In `services/ai/`, create corresponding Pydantic models for validating LLM JSON responses. Every field in every LLM response must be validated before being stored. Create a `validate_llm_response` utility that: calls Pydantic validation, catches `ValidationError`, logs the raw LLM response on failure, and returns `None` on failure (so callers can retry).

**Verification:**
- A valid ClauseResult JSON parses without errors
- A ClauseResult with a missing required field raises a ValidationError
- A ClauseResult with an invalid RiskLevel enum value raises a ValidationError
- The `validate_llm_response` utility returns None (not raises) on invalid input
- All RiskLevel, ContractType, and other enum values from PRD.md are represented

---

## PHASE 6 — Core Scan Pipeline

---

### STEP 6.1 — Implement Contract Type Detection

In `services/ai/pipelines/type_detection.py`, implement the contract type auto-detection pipeline. It must: take the first 1000 tokens of the contract text, call the FAST_MODEL with the `type_detection.txt` prompt, parse the response into a structured object containing: `type` (one of the 10 contract types from PRD.md), `confidence` (float 0–1), `party_roles` (array of strings), and return this object. If confidence is below 0.8, the pipeline must flag the result so the frontend can show the manual correction selector.

**Verification:**
- An employment contract is classified as "Employment" with confidence > 0.8
- An NDA is classified as "NDA"
- Party roles are extracted correctly (e.g., ["employer", "employee"])
- A low-confidence detection sets the flag correctly
- The function returns a valid Pydantic model, not a raw dict

---

### STEP 6.2 — Implement the Rule Engine

In `services/ai/rules/regex_rules.py`, implement the 40+ regex patterns for risk signal detection. Cover all risk categories from PRD.md: indemnity language, IP assignment, non-compete, auto-renewal, limitation of liability, termination for convenience, unilateral modification, liquidated damages, arbitration-only, payment clawback, and more. Each pattern must have: a name, the regex pattern, the risk category it maps to, and a preliminary risk level (HIGH or MEDIUM). In `services/ai/rules/risk_mapper.py`, implement the mapping logic: given a clause text, run all patterns against it, count matches, and return the triage level — GREEN (0 matches), YELLOW (1–2 matches), RED (3+ matches or any HIGH-level pattern match).

**Verification:**
- A clause containing "shall indemnify and hold harmless" is flagged as indemnity risk
- A clause containing "all intellectual property created" is flagged as IP assignment
- A clause containing "automatically renew" is flagged as auto-renewal
- A clause with no risk signals is triaged as GREEN
- A clause with 1 signal is triaged as YELLOW
- A clause with a HIGH-level pattern (e.g., non-compete) is immediately triaged as RED regardless of count

---

### STEP 6.3 — Implement Risk Classification Pipeline

In `services/ai/pipelines/risk_classification.py`, implement the full two-pass risk classification pipeline as described in PRD.md Feature 1. Pass 1: run the rule engine on all clauses, separate into GREEN, YELLOW, RED buckets. Pass 2: send only YELLOW and RED clauses to the PRIMARY_MODEL in batches of maximum 20 clauses per call, using the `risk_analysis.txt` prompt with the contract type and user role injected. Parse and validate each response using Pydantic. Return the complete array of clause results — GREEN clauses get default LOW/SAFE results without an LLM call, flagged clauses get the full LLM analysis. Implement the streaming version of this pipeline that yields clause results one at a time as each LLM response arrives, so they can be pushed to the SSE stream.

**Verification:**
- GREEN clauses do not trigger any LLM calls
- YELLOW and RED clauses trigger LLM calls
- A 20-clause batch is sent as a single LLM call (not 20 separate calls)
- A 45-clause batch is sent as 3 LLM calls (batches of 20, 20, 5)
- Each returned clause result passes Pydantic validation
- The streaming version yields results progressively — not all at once at the end

---

### STEP 6.4 — Implement SSE Streaming Endpoint

In `services/api/app/api/v1/endpoints/streaming.py`, implement the `GET /scan/{jobId}/stream` endpoint. This is the most critical endpoint in the system. It must: verify the JWT and confirm the scan job belongs to the requesting user, subscribe to the Redis pub/sub channel for the job ID, yield each message from the channel as an SSE event with the format `data: {json}\n\n`, send a heartbeat event every 15 seconds to keep the connection alive, send a final `event: complete` event when the scan job status becomes "complete", and close the stream cleanly. In `services/api/app/services/streaming_service.py`, implement the Redis pub/sub publisher that the Celery worker calls to push clause results into the channel as they are processed. In `apps/web/hooks/useSSE.ts`, implement the frontend SSE consumer hook that: opens an EventSource connection, parses incoming JSON events, calls a callback for each clause result, handles reconnection on disconnect, and closes the connection on the "complete" event.

**Verification:**
- Opening the SSE endpoint with a valid JWT keeps the connection open
- Opening it with an invalid JWT returns 401 and closes
- Publishing a test message to the Redis channel causes it to appear in the SSE stream
- The heartbeat event is sent every 15 seconds
- The "complete" event closes the stream
- The frontend hook correctly parses each event and calls the callback
- On frontend page refresh, the hook reconnects and the stream resumes

---

### STEP 6.5 — Implement the Main Celery Task

In `apps/worker/tasks/process_contract.py`, implement the main scan pipeline Celery task. This task orchestrates all pipeline steps in the exact order defined in PRD.md Section 4.1 (steps 1 through 18, excluding translation which is conditional). The task must: accept a `contract_id` and `file_url` as arguments, update the `ScanJob` status to "processing" and `progress_pct` to 0, call each pipeline step in order, update `progress_pct` after each major step (parse: 10%, detect type: 15%, rule engine: 25%, LLM risk: 60%, consequence: 70%, power: 75%, precedent: 80%, summary: 85%, embed: 95%, store: 100%), publish each clause result to the Redis pub/sub channel as it completes (for SSE streaming), store all results in the database via the API's repository layer or directly via SQLAlchemy, and set the `ScanJob` status to "complete" when all steps finish. Handle errors by setting status to "failed" and storing the error message.

**Verification:**
- Queuing the task with a valid contract ID triggers all pipeline steps in order
- `progress_pct` updates are visible in the database during processing
- Each clause result is published to Redis as it completes (not all at once)
- ScanJob status changes to "complete" after all steps
- ScanJob status changes to "failed" if any step throws an unhandled error
- All clause results are stored in the `clauses` table after completion

---

### STEP 6.6 — Wire Upload to Scan — End-to-End Test

This step is a verification-only integration test. No new code is written. Connect the frontend upload flow to the backend scan pipeline and verify the full loop works end to end.

**Verification:**
- Upload a real PDF contract through the frontend UI
- The file is encrypted in the browser before upload
- The upload completes and returns a `job_id` and `contract_id`
- The frontend opens the SSE stream for the `job_id`
- The Celery worker processes the contract
- Clause results stream to the frontend via SSE
- All clause results are stored in the database
- The ScanJob reaches "complete" status
- The frontend receives the "complete" SSE event

---

## PHASE 7 — Remaining AI Pipelines

---

### STEP 7.1 — Implement Consequence Generation Pipeline

In `services/ai/pipelines/consequence_generation.py`, implement the real-world consequence translator as described in PRD.md Feature 3. It must: accept an array of HIGH and MEDIUM risk clauses with their risk categories, for each clause call the PRIMARY_MODEL with the `consequence.txt` prompt injecting: clause_type, user_role, contract_value (if known), and clause_text, parse the response into a Pydantic model containing: `headline`, `scenario`, `financial_exposure`, `probability`, and `similar_case`, and return the array of consequence objects. Integrate this pipeline call into the main Celery task after risk classification completes.

**Verification:**
- An indemnity clause returns a consequence with a financial_exposure field that is a dollar amount or "unlimited"
- An IP assignment clause returns a headline mentioning portfolio or IP rights
- The `probability` field is one of "Low", "Medium", "High"
- A LOW-risk clause is not passed to this pipeline (only HIGH and MEDIUM)
- All responses pass Pydantic validation

---

### STEP 7.2 — Implement Power Asymmetry Pipeline

In `services/ai/pipelines/power_analysis.py`, implement the power asymmetry scorer as described in PRD.md Feature 5. It must: accept the full array of clause results with their risk assessments and the user's role, call the PRIMARY_MODEL with the `power_asymmetry.txt` prompt, parse the response into a Pydantic model containing: `power_score` (integer -100 to +100), `power_label`, `key_imbalances` (array of objects), and `leverage_points` (array of strings), and return this object. Store the result in the `analysis_results` table. Integrate this pipeline call into the main Celery task after consequence generation.

**Verification:**
- A heavily one-sided contract (all clauses favor the other party) produces a power_score below -50
- A balanced contract produces a power_score between -20 and +20
- `power_score` is always an integer between -100 and +100
- `key_imbalances` contains at least 1 item for any contract with HIGH-risk clauses
- The result is stored correctly in `analysis_results`

---

### STEP 7.3 — Implement Summary Card Pipeline

In `services/ai/pipelines/summary.py`, implement the plain-language summary card generator as described in PRD.md Feature 4. It must: accept the contract type, all HIGH-risk clause summaries, all MEDIUM-risk clause summaries, and the overall risk statistics (counts per level), call the FAST_MODEL with the `summary.txt` prompt, parse the response into a Pydantic model containing: `one_liner`, `should_you_sign`, `top_3_concerns`, `top_2_positives`, `overall_risk_score`, and `negotiating_power`, and return this object. Also generate the Pros vs Cons snapshot in the same pipeline call or as a second call — accept the structured clause analysis and return `pros` (array), `cons` (array), and `verdict` string. Store both results in `analysis_results`. Integrate into the main Celery task after power analysis.

**Verification:**
- `should_you_sign` is always one of "Yes as-is", "Yes with changes", "No"
- `overall_risk_score` is always between 0 and 100
- `negotiating_power` is always "Strong", "Moderate", or "Weak"
- `top_3_concerns` always has exactly 3 items
- `top_2_positives` always has exactly 2 items
- Pros and cons are tagged with dimension labels (Financial, Liability, IP, etc.)

---

### STEP 7.4 — Implement Legal Precedent Retrieval Pipeline

In `services/ai/pipelines/precedent_retrieval.py`, implement the legal precedent retrieval and synthesis pipeline as described in PRD.md Feature 9. This requires the precedent corpus to be pre-indexed in pgvector (see STEP 7.5 for seeding). The pipeline must: accept a HIGH-risk clause with its risk category, embed the clause text using sentence-transformers `all-MiniLM-L6-v2`, perform a pgvector similarity search filtered by risk category to retrieve the top 3 most similar case summaries from the `embeddings` table (embedding_type = "precedent"), call the PRIMARY_MODEL with the `precedent.txt` prompt injecting the clause text and the 3 retrieved case summaries, parse the response into a Pydantic model containing: `precedent_summary`, `enforcement_likelihood`, `confidence_score` (0–100), and `cited_cases` (array of {name, year, outcome}), and store the result in `precedent_matches`. In `services/ai/utils/confidence_scorer.py`, implement the confidence score calculation: multiply the average RAG retrieval similarity score (from pgvector) by the LLM's self-rated confidence to produce the final score. Integrate this pipeline into the main Celery task, running it for each HIGH-risk clause after power analysis.

**Verification:**
- A non-compete clause retrieves precedent cases related to non-compete enforcement
- The retrieved cases have high similarity scores (above 0.6)
- `enforcement_likelihood` is one of the four defined values
- `confidence_score` is between 0 and 100
- `cited_cases` contains between 1 and 3 items
- The confidence score calculation correctly multiplies retrieval similarity by LLM confidence

---

### STEP 7.5 — Seed the Precedent Corpus

In `scripts/seed_precedents.py`, implement the script that populates the legal precedent vector index. The script must: read court case summary files from `services/ai/data/precedents/` (organized by subdirectory: employment, ip, nda, vendor), embed each case summary using sentence-transformers, store each embedding in the `embeddings` table with `embedding_type = "precedent"` and metadata (jurisdiction, year, outcome, clause_type) in a JSONB column, and report the total number of cases indexed. Populate `services/ai/data/precedents/` with at minimum 50 real case summaries sourced or summarized from CourtListener. Ensure coverage across all four domains and ensure the demo contract's HIGH-risk clauses will have at least 3 matching precedents.

**Verification:**
- The seed script runs without errors
- At least 50 precedent records exist in the `embeddings` table with `embedding_type = "precedent"`
- A similarity search for a non-compete clause returns at least 3 results with similarity > 0.5
- A similarity search for an IP assignment clause returns at least 3 results
- The precedent retrieval pipeline (STEP 7.4) works end-to-end with the seeded data

---

### STEP 7.6 — Implement Counter-Offer Pipeline and Seed Favorable Clause Corpus

In `scripts/index_favorable_clauses.py`, implement the script that populates the favorable clause corpus. Read clause variant files from `services/ai/data/favorable_clauses/` (organized by clause type subdirectory), embed each variant, and store in the `embeddings` table with `embedding_type = "favorable_clause"` and the clause type as metadata. Populate the data directory with at minimum 5 favorable variant examples per clause type covering: indemnity, ip_assignment, non_compete, auto_renewal, limitation_of_liability.

In `services/ai/pipelines/counter_offer.py`, implement the counter-offer generator as described in PRD.md Feature 6. It must: accept a HIGH-risk clause with its risk category, embed the clause, retrieve the top similar favorable clause variant from pgvector (embedding_type = "favorable_clause", filtered by clause type), call the PRIMARY_MODEL with the `counter_offer.txt` prompt injecting: original clause, retrieved favorable reference, contract type, and user role, parse the response into a Pydantic model containing: `aggressive` {clause, explanation}, `balanced` {clause, explanation}, `conservative` {clause, explanation}, and `negotiation_email`, and store in `counter_offers`. This pipeline is NOT part of the main scan task — it runs on-demand when the user clicks "Generate Counter-Offer" via the `generate_counter_offer` Celery task.

**Verification:**
- The favorable clause seed script indexes at least 25 records (5 types × 5 variants minimum)
- A counter-offer request for an IP assignment clause retrieves an IP-related favorable variant
- All three counter-offer versions (aggressive, balanced, conservative) are different from each other
- The negotiation_email is 2 sentences and professional in tone
- The counter-offer is stored in `counter_offers` linked to the correct clause

---

## PHASE 8 — RAG Chat Pipeline

---

### STEP 8.1 — Implement the Embedding Pipeline

In `services/ai/rag/embedder.py`, implement the contract embedding function using sentence-transformers `all-MiniLM-L6-v2`. It must: accept a contract text string, split it into overlapping chunks (chunk size 500 tokens, overlap 50 tokens) using the chunking utility in `services/ai/utils/chunk_splitter.py`, embed each chunk using the model, and return an array of {chunk_text, chunk_index, embedding_vector} objects. In `services/ai/rag/vector_store.py`, implement the pgvector storage functions: `store_embeddings` (bulk insert embedding records for a contract) and `search_similar` (given a query embedding and filters, return top-k similar records with similarity scores). In `apps/worker/tasks/embed_contract.py`, implement the Celery task that runs the embedding pipeline for a contract after scan completes and stores all chunk embeddings in the `embeddings` table with `embedding_type = "contract_qa"`.

**Verification:**
- A 5-page contract is split into between 10 and 50 chunks
- All chunks overlap correctly (last 50 tokens of chunk N appear at start of chunk N+1)
- All chunk embeddings are stored in the `embeddings` table
- A similarity search for "non-compete" returns chunks containing non-compete language
- Similarity search is scoped to a single contract (does not return chunks from other contracts)

---

### STEP 8.2 — Implement the Q&A Chat Pipeline

In `services/ai/rag/chat_chain.py`, implement the LangChain Q&A retrieval chain for contract chat. Configure it with: the pgvector retriever (fetching top 5 most similar chunks for the query), a system prompt instructing the model to always cite the clause or section it references and to explicitly say if the answer is not in the contract, and streaming output enabled. In `services/api/app/api/v1/endpoints/chat.py`, implement the `POST /chat/{contractId}` endpoint. It must: verify the JWT, confirm the contract belongs to the user, accept a `question` string and optional `conversation_history` array, call the chat chain, and return a streaming response via SSE. In `services/api/app/services/chat_service.py`, implement the chat service that orchestrates the retrieval chain call and formats the response.

**Verification:**
- Asking "What are the notice periods?" about a contract containing notice period language returns the correct answer with a clause citation
- Asking about something not in the contract returns "This is not addressed in the contract" (not a hallucinated answer)
- The answer streams token by token
- The conversation history is correctly passed for follow-up questions
- A follow-up question ("What if I give more notice?") uses context from the previous answer

---

## PHASE 9 — Multilingual Support

---

### STEP 9.1 — Implement Language Detection and Translation

In `services/ai/translation/detector.py`, implement language detection using langdetect. It must: accept a text string (use the first 500 characters for efficiency), return the detected language code (e.g., "es", "fr", "de"), and return "en" for English. Handle detection failures gracefully by defaulting to "en". In `services/ai/translation/translator.py`, implement the DeepL API wrapper. It must: accept a text string, source language, and target language, call the DeepL API, and return the translated text. Handle API errors and rate limits. Implement batch translation to minimize API calls — translate all clause results in a single batch call rather than one call per clause.

**Verification:**
- A Spanish text is detected as "es" with high confidence
- A French text is detected as "fr"
- An English text is detected as "en"
- A Spanish clause is correctly translated to English via DeepL
- An English clause is correctly translated to Spanish
- Batch translation of 20 clauses makes 1 API call, not 20

---

### STEP 9.2 — Implement the Multilingual Pipeline

In `services/ai/pipelines/multilingual_pipeline.py`, implement the full multilingual orchestration pipeline as described in PRD.md Feature 11. It must: detect the contract language, if non-English: translate the full contract text to English before passing to any other pipeline, after all analysis is complete: translate all result text fields back to the user's preferred language (plain_english, scenario, headline, worst_case, one_liner, top_concerns, top_positives, leverage_points, negotiation_email — all human-readable text fields), use the bilingual legal glossary JSON to ensure jurisdiction-specific terms are translated correctly, and store both the English and translated versions of results in the database. In `apps/worker/tasks/translate_results.py`, implement the on-demand Celery task for post-scan language switching — triggered when a user changes their language preference after a scan has already completed. In `services/api/app/api/v1/endpoints/translate.py`, implement the `POST /translate/{contractId}` endpoint that queues the translation task.

**Verification:**
- A Spanish PDF contract is detected as Spanish before parsing
- The translated-to-English text is used for all LLM analysis
- All result text fields are translated back to Spanish in the stored results
- The LanguageDetectionBanner shows correctly for a non-English contract
- Post-scan language switch from Spanish to English returns the English versions of all results
- Legal terms like "indemnización" correctly map to "indemnity" and back

---

## PHASE 10 — Report Generation

---

### STEP 10.1 — Build the PDF Report Templates

In `services/api/templates/`, build the Jinja2 HTML templates for the PDF report as described in PRD.md Feature 12. Create `base.html` with the overall layout, color scheme, typography (embed fonts inline for PDF), and the logo placeholder. Create section templates: `cover.html` (contract name, risk score, date, user role), `summary.html` (one-liner, verdict, concerns, positives, score meter), `clauses.html` (clause-by-clause table with risk color coding), `power.html` (power score and key imbalances), `precedent.html` (per-clause precedent summaries and case citations), `counter_offers.html` (side-by-side original vs rewritten clauses). Create the `static/report.css` with print-optimized CSS — proper page breaks, no orphaned headings, consistent color bands for HIGH/MEDIUM/LOW. Create all 6 language string files in `templates/i18n/` for report labels (English, Spanish, French, German, Portuguese, Hindi).

**Verification:**
- Rendering `base.html` with dummy data produces valid HTML
- WeasyPrint can convert the rendered HTML to a PDF without errors
- The PDF has correct page breaks (no clause cut off mid-page)
- Risk level colors are correct: HIGH = red, MEDIUM = yellow/amber, LOW = green
- The PDF is readable on mobile (test by opening on a phone)

---

### STEP 10.2 — Implement Report Generation Service

In `services/api/app/utils/pdf_generator.py`, implement the PDF generation function using WeasyPrint and Jinja2. It must: accept a contract ID, fetch all associated data (contract metadata, clauses, analysis results, counter-offers, precedent matches) from the database, select the correct i18n language file based on the user's preferred language, render each template section with the data, concatenate sections into a single HTML document, convert to PDF using WeasyPrint, save the PDF to a file path, and return the file path. In `services/api/app/services/report_service.py`, implement the report creation service: generate a UUID for the share link, set the 48-hour expiry timestamp, create the report record in the database, and trigger the `generate_report` Celery task. In `apps/worker/tasks/generate_report.py`, implement the Celery task that calls `pdf_generator.py`.

**Verification:**
- Triggering report generation for a completed scan produces a PDF file
- The PDF contains all sections: cover, summary, clauses, power, precedent, counter-offers
- The share UUID is stored in the report record
- The expiry timestamp is exactly 48 hours from creation
- The report endpoint (`GET /report/{reportId}`) returns the PDF for authenticated users
- The share endpoint (`GET /report/share/{shareUuid}`) returns the report without authentication

---

### STEP 10.3 — Implement Report Cleanup Task

In `apps/worker/tasks/cleanup_expired_reports.py`, implement the Celery Beat periodic task that runs every hour. It must: query the database for all reports where `expires_at` is in the past, delete the PDF file from the file system for each expired report, delete the report record from the database, and log the number of reports cleaned up. Configure Celery Beat in `apps/worker/celery_app.py` to schedule this task hourly.

**Verification:**
- Creating a report with an `expires_at` in the past and running the cleanup task deletes it
- The PDF file is deleted from the file system
- The database record is deleted
- The cleanup task runs on the hourly schedule (verify via Celery Beat logs)
- A report with `expires_at` in the future is NOT deleted

---

## PHASE 11 — Frontend Feature Implementation

---

### STEP 11.1 — Build the App Shell and Navigation

In `apps/web/app/(app)/layout.tsx`, build the app shell layout. It must include: a `Navbar.tsx` with the logo, user avatar (from Clerk), and navigation links (Dashboard, Upload), a `Sidebar.tsx` for contract history quick access, and a main content area. Build `components/layout/Navbar.tsx`, `Sidebar.tsx`, and `Footer.tsx`. Set up Zustand stores: create `scanStore.ts`, `clauseStore.ts`, `reportStore.ts`, `languageStore.ts`, and `uiStore.ts` with their initial state shapes and actions as defined by the features they support.

**Verification:**
- The app shell renders on all `(app)/` pages
- The Navbar shows the logged-in user's avatar
- The Sidebar renders without errors
- All Zustand stores initialize without errors
- Navigation between Dashboard, Upload, and other pages works

---

### STEP 11.2 — Build the Upload Page

In `apps/web/app/(app)/upload/page.tsx`, build the complete upload page. Compose: `UploadZone.tsx` (drag-and-drop area), `EncryptionBadge.tsx` (shows during upload), `EncryptionStatus.tsx` (shows post-upload), and `UploadProgress.tsx` (upload progress bar). The page flow must be: user drops file → encryption starts (badge animates) → encrypted file uploads (progress bar fills) → upload completes → `POST /upload` is called with the file URL → `job_id` is received → user is redirected to `/scan/{jobId}`. Handle errors: file type rejection, file size rejection, upload failure, API failure. All error states must show clear user-facing messages.

**Verification:**
- Dropping a PDF file triggers the encryption badge animation
- The progress bar fills during upload
- After upload, the user is redirected to the scan page with the correct job ID
- Dropping a non-PDF/DOCX file shows an error message
- Dropping a file over 25MB shows an error message
- Network failure shows a retry option

---

### STEP 11.3 — Build the Live Scan Results Page

In `apps/web/app/(app)/scan/[jobId]/page.tsx`, build the core scan results page. This is the most complex page in the application. Compose all analysis feature components in the correct layout described in PRD.md Section 8.1:

**Top section:** `SummaryCard.tsx` with `RiskScoreMeter.tsx` and `SignVerdict.tsx` — renders after scan completes, shows skeleton while loading.

**Left panel:** `ClauseList.tsx` containing `ClauseCard.tsx` components. Each `ClauseCard.tsx` contains: the clause text snippet, `RiskBadge.tsx`, and expands on click to show `ConsequencePanel.tsx`. Clauses animate in one by one using Framer Motion stagger as SSE events arrive. `RiskCounter.tsx` at the top of the list shows the live count.

**Right panel (detail):** Opens when a clause is selected. Shows the full consequence detail. Has tabs for: Consequence, Counter-Offer (`CounterOfferPanel.tsx`), Precedent (`PrecedentPanel.tsx`).

**Power section:** `PowerMeter.tsx` with `PowerScore.tsx` and `LeveragePoints.tsx` — renders after power analysis result arrives via SSE.

**Bottom section:** `ProsConsSnapshot.tsx` — renders after summary is complete.

Use `useScan.ts` hook to manage the SSE connection and populate the `scanStore` and `clauseStore`. Use Framer Motion for all animations: clause stagger, power meter needle, risk badge color transitions.

**Verification:**
- Opening `/scan/{jobId}` for a completed scan immediately shows all results
- Opening it for an in-progress scan shows real-time streaming
- Clauses animate in one by one, not all at once
- Clicking a clause card expands it and shows the consequence panel
- The power meter needle animates on first render
- The summary card only appears after the scan is fully complete
- Filtering clauses by risk level (HIGH / MEDIUM / LOW) works
- Page refresh restores all data from the database (not just SSE)

---

### STEP 11.4 — Build the Counter-Offer Panel

In `apps/web/features/counter-offer/CounterOfferPanel.tsx`, build the counter-offer panel. It must: show a "Generate Counter-Offer" button for HIGH-risk clauses, call the counter-offer endpoint when clicked, show a loading state while generation runs, render `ClauseDiff.tsx` with the original clause on the left (red background) and the rewritten clause on the right (green background) with word-level diff highlighting, render `VersionTabs.tsx` to switch between Aggressive / Balanced / Conservative versions, and render `NegotiationEmail.tsx` with the pre-written email and a copy-to-clipboard button that shows a success state animation.

**Verification:**
- The "Generate Counter-Offer" button only appears on HIGH-risk clauses
- Clicking it shows a loading spinner while the Celery task runs
- The diff view correctly highlights changed words (red removed, green added)
- Switching tabs between Aggressive / Balanced / Conservative shows different clause text
- The "Copy Email" button copies the negotiation email to clipboard
- A success checkmark animation plays after copying

---

### STEP 11.5 — Build the Legal Precedent Panel

In `apps/web/features/precedent/PrecedentPanel.tsx`, build the legal precedent panel. It must: show the precedent tab on HIGH-risk clause cards, display the `precedent_summary` text, render up to 3 `CaseCard.tsx` components each showing case name, year, jurisdiction, and outcome, render the `ConfidenceBadge.tsx` showing the confidence percentage with color coding (green for > 75%, yellow for 50–75%, red for < 50%), and display the `enforcement_likelihood` label.

**Verification:**
- The precedent tab is only visible on HIGH-risk clauses
- Up to 3 case cards render with correct data
- The confidence badge color changes based on the score
- The enforcement likelihood label displays correctly

---

### STEP 11.6 — Build the Q&A Chat Page

In `apps/web/app/(app)/chat/[contractId]/page.tsx` and the chat feature components, build the full Q&A chat interface. `ChatWindow.tsx` must: show the contract name at the top, render the conversation history with `ChatMessage.tsx` bubbles (user right, AI left), show the clause citation as a clickable pill under each AI response, stream AI responses token by token using SSE, and show a typing indicator while the response is being generated. `ChatInput.tsx` must: have a multi-line text input, send on Enter (Shift+Enter for newline), show a send button, and disable input while a response is streaming. Use `useChat.ts` hook for conversation state management.

**Verification:**
- Asking a question returns a streamed answer
- The answer contains a clause citation for questions about specific contract terms
- The clause citation pill is clickable (navigates to that clause on the scan results page)
- Follow-up questions correctly reference previous answers
- Asking about something not in the contract returns an explicit "not in contract" response
- Input is disabled while a response is streaming

---

### STEP 11.7 — Build the Multilingual UI Components

In `apps/web/features/multilingual/LanguageDetectionBanner.tsx`, build the banner that appears when a non-English contract is detected. It must show: the detected language name, the user's role assumption, and a manual language override option. In `apps/web/features/multilingual/BilingualToggle.tsx`, build the toggle that allows switching between the original language and English on the results page. In `apps/web/hooks/useLanguage.ts`, implement the language state hook that: reads the active language from `languageStore`, calls `POST /translate/{contractId}` when language is switched, shows a loading state while translation runs, and updates the store with the translated results.

**Verification:**
- Uploading a Spanish contract shows the language detection banner
- The banner correctly identifies the language
- The BilingualToggle appears on the results page for non-English contracts
- Switching language triggers the translation task
- After translation, all result text (clause explanations, consequences, etc.) displays in the selected language
- Switching back to English shows the English versions

---

### STEP 11.8 — Build the Report Page and Sharing

In `apps/web/app/(app)/report/[reportId]/page.tsx`, build the report viewer. Use `ReportViewer.tsx` to show the report in-browser (iframe or HTML render of the PDF content). In `apps/web/features/report/ShareButton.tsx`, implement the share button that: calls the report generation endpoint, waits for the PDF to be ready, generates the share link, copies it to clipboard, and shows a success animation. In `apps/web/features/report/DownloadButton.tsx`, implement direct PDF download. The share link (`/report/share/{shareUuid}`) must be publicly accessible without authentication — build this as a public route outside the `(app)/` route group.

**Verification:**
- The Download button triggers a PDF file download
- The Share button copies a valid URL to clipboard
- Opening the share URL in an incognito window (no login) shows the full report
- The report renders all sections correctly in-browser
- A share link that has expired shows an "expired" message

---

### STEP 11.9 — Build the Dashboard

In `apps/web/app/(app)/dashboard/page.tsx`, build the contract history dashboard. It must show: a list of all contracts the user has scanned, for each contract: filename, contract type, overall risk score, scan date, and a link to the scan results, a power asymmetry trend indicator if the user has 3 or more contracts ("Your last 3 contracts averaged -42"), and an empty state with a call-to-action to upload the first contract.

**Verification:**
- The dashboard shows all previously scanned contracts for the logged-in user
- Clicking a contract navigates to its scan results page
- The power trend shows if the user has 3+ contracts
- The empty state shows for new users
- Contracts from other users are never shown

---

## PHASE 12 — Caching and Performance

---

### STEP 12.1 — Implement the Redis Caching Layer

In `services/ai/cache/result_cache.py`, implement the result caching utility. It must: generate a cache key from the hash of the contract text content (not the file name), check the cache before running any LLM pipeline steps — if a cache hit is found, return the cached results immediately and skip all LLM calls, store completed scan results in Redis with a TTL of 7 days, and implement a cache invalidation function for when results need to be regenerated. In `services/ai/cache/cache_config.py`, define TTL constants and key naming conventions. Integrate the cache check as the first step in the main Celery scan task.

**Verification:**
- Uploading the same contract twice: the second scan returns results from cache without making any LLM calls (verify via LLM call logs showing 0 calls)
- Cache keys are based on content hash, not filename (renaming the file and re-uploading still hits cache)
- Cache TTL is 7 days (verify expiry timestamp in Redis)
- Cache invalidation removes the key from Redis

---

### STEP 12.2 — Pre-compute Demo Contract Results

In `scripts/seed_demo_contracts.py`, implement the demo pre-computation script. It must: define 3 specific demo contracts (a freelance agreement, an employment contract, an NDA) stored in `services/ai/data/synthetic_contracts/`, run the full scan pipeline on each contract, and store the results in Redis cache with no expiry (TTL = 0). This ensures that when these specific demo contracts are uploaded during a demonstration, results are returned instantly from cache with no LLM calls needed.

**Verification:**
- Running the seed script processes all 3 demo contracts
- The cache contains results for all 3 contracts
- Uploading a demo contract returns results in under 2 seconds (from cache)
- The demo freelance contract has at least one IP assignment clause flagged as HIGH risk

---

## PHASE 13 — Testing

---

### STEP 13.1 — Backend Unit Tests

In `services/api/tests/unit/`, write unit tests for all service layer functions. Test: `contract_service`, `analysis_service`, `counter_offer_service`, `summary_service`, `power_service`, `precedent_service`, `report_service`, `chat_service`, `translation_service`. Use pytest with pytest-asyncio for async functions. Mock all external dependencies (LLM calls, Redis, database) — unit tests must not make real network calls. In `services/ai/tests/test_pipelines.py`, write unit tests for all AI pipeline functions with mocked LLM responses. In `services/ai/tests/test_rules.py`, write unit tests for the rule engine — test every regex pattern against known positive and negative examples. Test every rule pattern with at least one match case and one non-match case.

**Verification:**
- All unit tests pass: `pytest services/api/tests/unit/ -v`
- All AI pipeline tests pass: `pytest services/ai/tests/ -v`
- No test makes a real LLM call or database call
- Rule engine tests cover all 40+ patterns
- Test coverage for service layer is above 80%

---

### STEP 13.2 — Backend Integration Tests

In `services/api/tests/integration/` and `tests/` (root), write integration tests using the `docker-compose.test.yml` environment. Test: the full upload-to-scan pipeline end to end, SSE streaming delivers correct events, the chat endpoint returns correct answers, the translation endpoint switches language correctly, report generation produces a valid PDF. Use `httpx.AsyncClient` with the FastAPI `TestClient` for API tests. Use a real test database (from docker-compose.test.yml) — not mocked. Seed the test database with known contract data before each test.

**Verification:**
- All integration tests pass: `pytest tests/ -v`
- The full scan pipeline test completes and produces results in the test database
- The SSE streaming test receives at least one clause event
- The report test produces a non-empty PDF file

---

### STEP 13.3 — Frontend Component Tests

In `apps/web/`, configure Vitest and React Testing Library. Write component tests for: `ClauseCard` (renders correct risk badge color), `PowerMeter` (renders with correct needle position for given score), `SummaryCard` (renders all fields), `UploadZone` (rejects invalid file types), `ChatInput` (disables on submit), `CounterOfferPanel` (shows three version tabs), `LanguageDetectionBanner` (shows for non-English, hidden for English).

**Verification:**
- All component tests pass: `npm run test` in `apps/web/`
- No test depends on external API calls
- ClauseCard renders red for HIGH, yellow for MEDIUM, green for LOW/SAFE

---

## PHASE 14 — CI/CD and Deployment

---

### STEP 14.1 — Set Up GitHub Actions CI Pipeline

In `.github/workflows/ci.yml`, create the CI pipeline that runs on every pull request and every push to main. It must: run frontend linting (ESLint), run frontend type checking (TypeScript), run frontend component tests (Vitest), run backend linting (ruff or flake8), run backend unit tests (pytest), run backend integration tests using docker-compose.test.yml, and report pass/fail status on the PR. The pipeline must fail fast — if any step fails, subsequent steps do not run.

**Verification:**
- Opening a pull request triggers the CI pipeline
- A failing test causes the pipeline to fail and blocks the PR
- All existing tests pass on the main branch

---

### STEP 14.2 — Deploy Frontend to Vercel

Connect the `apps/web/` directory to Vercel. Configure: the root directory as `apps/web/`, build command as `next build`, all frontend environment variables in Vercel's environment variable settings (using the `.env.example` as the reference), and automatic deployment on push to main. Set the production URL as the `NEXT_PUBLIC_API_URL` pointing to the Railway API deployment.

**Verification:**
- Pushing to main automatically triggers a Vercel deployment
- The production URL loads the application
- Clerk authentication works on the production URL
- The API client correctly calls the Railway backend URL

---

### STEP 14.3 — Deploy Backend to Railway

Deploy the FastAPI service and Celery worker to Railway. Configure: the `services/api/` Dockerfile for the API service, the `apps/worker/` Dockerfile for the worker service, all backend environment variables in Railway's environment settings, the Neon database URL as the `DATABASE_URL`, and the Upstash Redis URL as the `REDIS_URL`. Configure Railway to run database migrations automatically on deploy (`alembic upgrade head` as the deploy command or start script). Configure the AI service deployment separately pointing to the `services/ai/` Dockerfile.

**Verification:**
- All three services (API, AI, Worker) are running on Railway
- `GET /health` on the production Railway API URL returns `{"status": "ok"}`
- The Celery worker is connected to Upstash Redis (verify via Railway logs)
- Database migrations are applied on the production Neon database
- An end-to-end upload and scan works on the production environment

---

### STEP 14.4 — Final End-to-End Production Verification

This is the final verification step. Test the complete product on the production deployment.

**Verification:**
- Upload a real PDF contract from a fresh account on the production URL
- Contract is encrypted in the browser (verify by checking browser DevTools — the file bytes in the network request should not be readable as a PDF)
- Scan completes and all clauses stream to the results page
- At least one HIGH-risk clause is detected
- The Power Asymmetry Meter renders with an animated needle
- The Summary Card renders with a risk score
- Clicking a HIGH-risk clause shows the Consequence Panel with a financial exposure amount
- The Precedent Panel shows at least one case citation
- Generating a Counter-Offer produces three versions
- The Negotiation Email copy button works
- The Q&A Chat answers a question about the contract with a clause citation
- Downloading the PDF report produces a styled PDF with all sections
- The share link works in an incognito window without login
- Uploading a Spanish contract shows the language detection banner
- Switching language shows results in Spanish

---

## Build Order Summary

```
PHASE 0  — Repository & Environment        (Steps 0.1–0.7)
PHASE 1  — Database Foundation             (Steps 1.1–1.4)
PHASE 2  — Authentication                  (Steps 2.1–2.3)
PHASE 3  — File Upload with Encryption     (Steps 3.1–3.3)
PHASE 4  — Document Parsing Pipeline       (Steps 4.1–4.4)
PHASE 5  — LLM Integration Foundation      (Steps 5.1–5.3)
PHASE 6  — Core Scan Pipeline              (Steps 6.1–6.6)
PHASE 7  — Remaining AI Pipelines          (Steps 7.1–7.6)
PHASE 8  — RAG Chat Pipeline               (Steps 8.1–8.2)
PHASE 9  — Multilingual Support            (Steps 9.1–9.2)
PHASE 10 — Report Generation               (Steps 10.1–10.3)
PHASE 11 — Frontend Feature Implementation (Steps 11.1–11.9)
PHASE 12 — Caching and Performance         (Steps 12.1–12.2)
PHASE 13 — Testing                         (Steps 13.1–13.3)
PHASE 14 — CI/CD and Deployment            (Steps 14.1–14.4)
```

**Total: 47 steps across 14 phases. Complete every verification before proceeding.**

---

*Every step in this document assumes the agent has read PRD.md, TECH_STACK.md, and FOLDER_STRUCTURE.md in full before starting. All file paths reference FOLDER_STRUCTURE.md. All feature behaviors reference PRD.md. All tools reference TECH_STACK.md.*