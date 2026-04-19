# 🏛️ LegalTech Contract Scanner — Production Folder Structure

> Monorepo architecture.
> Clean separation: Frontend · API · AI Service · Worker

---

## 📁 Root

```
legaltech-ai/
│
├── apps/
│   ├── web/                           # Next.js 15 frontend
│   └── worker/                        # Celery background worker
│
├── services/
│   ├── api/                           # FastAPI backend
│   └── ai/                            # AI + NLP pipelines
│
├── packages/                          # Shared code (TS + Python)
│   ├── types/                         # Shared TypeScript types
│   ├── utils/                         # Shared helpers
│   └── config/                        # Env + constants
│
├── infra/
│   ├── docker/                        # All Dockerfiles
│   ├── nginx/                         # Reverse proxy config
│   └── terraform/                     # Optional infra as code
│
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Lint + test on every PR
│       ├── deploy-web.yml             # Auto deploy frontend to Vercel
│       └── deploy-api.yml             # Auto deploy backend to Railway
│
├── scripts/                           # Dev + seed scripts
├── tests/                             # Global integration tests
├── .env.example                       # All env variable keys
├── .gitignore
├── docker-compose.yml                 # Local dev: all services
├── docker-compose.test.yml            # CI testing: isolated test DB + Redis
└── README.md
```

---

## 🎨 Frontend — `apps/web/`

```
apps/web/
│
├── public/
│   ├── fonts/                         # Self-hosted fonts
│   ├── icons/                         # SVG icons
│   └── logo.svg
│
├── app/                               # Next.js 15 App Router
│   ├── layout.tsx                     # Root layout (Clerk, fonts, providers)
│   ├── page.tsx                       # Landing page
│   ├── globals.css                    # Tailwind v4 base styles
│   │
│   ├── (auth)/                        # Auth route group
│   │   ├── sign-in/
│   │   │   └── page.tsx
│   │   └── sign-up/
│   │       └── page.tsx
│   │
│   ├── (app)/                         # Protected route group (guarded by middleware.ts)
│   │   ├── layout.tsx                 # App shell (sidebar, navbar)
│   │   ├── dashboard/
│   │   │   └── page.tsx               # Contract history dashboard
│   │   ├── upload/
│   │   │   └── page.tsx               # Upload + scan trigger
│   │   ├── scan/
│   │   │   └── [jobId]/
│   │   │       └── page.tsx           # Live scan results (SSE consumer)
│   │   ├── report/
│   │   │   └── [reportId]/
│   │   │       └── page.tsx           # Shareable report view
│   │   └── chat/
│   │       └── [contractId]/
│   │           └── page.tsx           # Q&A chat page
│   │
│   └── api/                           # Next.js edge API routes
│       ├── uploadthing/
│       │   └── route.ts               # Uploadthing file router
│       └── webhooks/
│           └── clerk/
│               └── route.ts           # Clerk webhook handler
│
├── middleware.ts                      # Clerk auth middleware — protects all (app)/ routes
│
├── components/
│   ├── ui/                            # Shadcn/ui base components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── dialog.tsx
│   │   ├── progress.tsx
│   │   ├── tabs.tsx
│   │   ├── tooltip.tsx
│   │   ├── separator.tsx
│   │   └── skeleton.tsx
│   │
│   ├── layout/                        # App layout components
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   │
│   └── common/                        # Shared utility components
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       ├── EmptyState.tsx
│       └── LanguageSwitcher.tsx
│
├── features/                          # Feature-based components (main UI)
│   │
│   ├── upload/                        # Upload flow
│   │   ├── UploadZone.tsx             # Drag & drop upload area
│   │   ├── EncryptionBadge.tsx        # "Encrypted before upload" indicator
│   │   ├── EncryptionStatus.tsx       # Post-session: key hash display + deletion confirmation
│   │   └── UploadProgress.tsx         # Upload progress bar
│   │
│   ├── analysis/                      # Scan results + risk analysis
│   │   ├── ScanProgress.tsx           # Live scan progress bar
│   │   ├── ClauseCard.tsx             # Individual clause risk card
│   │   ├── ClauseList.tsx             # Animated list of clause cards
│   │   ├── RiskBadge.tsx              # HIGH / MEDIUM / LOW badge
│   │   ├── RiskCounter.tsx            # "3 HIGH · 7 MEDIUM · 12 SAFE"
│   │   └── ConsequencePanel.tsx       # Slide-open consequence detail
│   │
│   ├── summary/                       # Summary card
│   │   ├── SummaryCard.tsx            # Hero summary (score + verdict)
│   │   ├── RiskScoreMeter.tsx         # 0–100 animated score
│   │   ├── ProsConsSnapshot.tsx       # Two-column pros vs cons
│   │   └── SignVerdict.tsx            # Yes / No / Yes with changes
│   │
│   ├── power/                         # Power asymmetry meter
│   │   ├── PowerMeter.tsx             # Animated gauge needle
│   │   ├── PowerScore.tsx             # Score label + description
│   │   └── LeveragePoints.tsx         # User leverage point list
│   │
│   ├── counter-offer/                 # Counter offer generator
│   │   ├── CounterOfferPanel.tsx      # Slide-open panel
│   │   ├── ClauseDiff.tsx             # Side-by-side diff (red vs green)
│   │   ├── VersionTabs.tsx            # Aggressive / Balanced / Conservative
│   │   └── NegotiationEmail.tsx       # Copy email snippet button
│   │
│   ├── precedent/                     # Legal precedent + confidence score
│   │   ├── PrecedentPanel.tsx         # Expandable panel on clause card
│   │   ├── CaseCard.tsx               # Individual case: name, year, outcome
│   │   └── ConfidenceBadge.tsx        # "87% confidence" visual badge
│   │
│   ├── multilingual/                  # Multilingual support UI
│   │   ├── LanguageDetectionBanner.tsx  # "Spanish contract detected" auto-detect banner
│   │   └── BilingualToggle.tsx        # Side-by-side English / original language toggle
│   │
│   ├── chat/                          # Q&A chat
│   │   ├── ChatWindow.tsx             # Full chat interface
│   │   ├── ChatMessage.tsx            # Message bubble
│   │   ├── ChatInput.tsx              # Input + send button
│   │   └── ClauseCitation.tsx         # Highlighted clause reference
│   │
│   └── report/                        # Shareable report
│       ├── ReportViewer.tsx           # In-browser report preview
│       ├── ShareButton.tsx            # Copy shareable link
│       └── DownloadButton.tsx         # PDF download trigger
│
├── animations/                        # Framer Motion configs
│   ├── variants.ts                    # Shared animation variants
│   ├── transitions.ts                 # Transition presets
│   └── PowerMeterAnim.ts              # Needle animation logic
│
├── hooks/                             # Custom React hooks
│   ├── useSSE.ts                      # SSE stream consumer
│   ├── useScan.ts                     # Scan job state + progress
│   ├── useEncryption.ts               # WebCrypto AES-256-GCM
│   ├── useUpload.ts                   # Uploadthing handler
│   ├── useChat.ts                     # Chat state + history
│   └── useLanguage.ts                 # Active language state + switch handler
│
├── store/                             # Zustand state stores
│   ├── scanStore.ts                   # Live scan job state
│   ├── clauseStore.ts                 # Clause results + selected clause
│   ├── reportStore.ts                 # Report state
│   ├── languageStore.ts               # Active language + translation state
│   └── uiStore.ts                     # UI state (panels, modals)
│
├── lib/                               # Frontend utilities
│   ├── api.ts                         # Typed API client (fetch → FastAPI)
│   ├── uploadthing.ts                 # Uploadthing client config
│   ├── crypto.ts                      # WebCrypto API helpers
│   ├── sse.ts                         # SSE connection utility
│   └── utils.ts                       # General helpers (cn, formatters)
│
├── types/                             # TypeScript types (local)
│   ├── scan.ts
│   ├── report.ts
│   ├── chat.ts
│   └── api.ts
│
├── styles/
│   └── globals.css
│
├── .env.local
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── components.json                    # Shadcn/ui config
└── package.json
```

---

## ⚙️ Backend API — `services/api/`

```
services/api/
│
├── app/
│   │
│   ├── main.py                        # FastAPI app init, CORS, middleware
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── router.py              # Mounts all v1 endpoints
│   │       └── endpoints/
│   │           ├── upload.py          # POST /upload
│   │           ├── analysis.py        # POST /scan, GET /scan/{jobId}
│   │           ├── streaming.py       # GET /scan/{jobId}/stream (SSE)
│   │           ├── counter_offer.py   # POST /counter-offer
│   │           ├── summary.py         # GET /summary/{contractId}
│   │           ├── power.py           # GET /power/{contractId}
│   │           ├── precedent.py       # GET /precedent/{clauseId}
│   │           ├── report.py          # POST /report/generate, GET /report/{id}
│   │           ├── chat.py            # POST /chat/{contractId}
│   │           ├── translate.py       # POST /translate/{contractId} — switch language post-scan
│   │           ├── auth.py            # Clerk webhook + JWT verify
│   │           └── health.py          # GET /health
│   │
│   ├── core/
│   │   ├── config.py                  # Pydantic settings (loads .env)
│   │   ├── security.py                # Clerk JWT verification
│   │   └── logging.py                 # Structured logging config
│   │
│   ├── models/                        # SQLAlchemy ORM models
│   │   ├── base.py                    # Declarative base
│   │   ├── user.py                    # User (synced from Clerk webhook)
│   │   ├── contract.py                # Contract (metadata, file ref, detected language)
│   │   ├── clause.py                  # Clause (text, risk, analysis)
│   │   ├── scan_job.py                # Scan job (status, progress)
│   │   ├── analysis_result.py         # Full analysis result per contract
│   │   ├── counter_offer.py           # Generated counter offers
│   │   ├── precedent_match.py         # Matched case law per clause
│   │   ├── report.py                  # Report (UUID, expiry, PDF path)
│   │   └── embedding.py               # pgvector embedding store
│   │
│   ├── schemas/                       # Pydantic schemas (API I/O)
│   │   ├── contract.py                # ContractCreate, ContractRead
│   │   ├── clause.py                  # ClauseResult, ClauseRead
│   │   ├── scan_job.py                # ScanRequest, ScanResponse
│   │   ├── counter_offer.py           # CounterOfferRequest, Response
│   │   ├── power.py                   # PowerAnalysisResult, LeveragePoint
│   │   ├── precedent.py               # PrecedentMatch, CaseReference, ConfidenceScore
│   │   ├── report.py                  # ReportCreate, ReportRead
│   │   ├── chat.py                    # ChatRequest, ChatResponse
│   │   ├── translation.py             # TranslationRequest, TranslationResponse
│   │   └── response.py                # Shared enums (RiskLevel, ContractType)
│   │
│   ├── services/                      # Business logic layer
│   │   ├── contract_service.py        # Contract create/read/delete
│   │   ├── analysis_service.py        # Orchestrates full scan pipeline
│   │   ├── counter_offer_service.py   # Counter offer orchestration
│   │   ├── summary_service.py         # Summary card generation
│   │   ├── power_service.py           # Power asymmetry orchestration
│   │   ├── precedent_service.py       # Legal precedent retrieval + confidence
│   │   ├── report_service.py          # PDF generation + share link
│   │   ├── chat_service.py            # Q&A chat orchestration
│   │   ├── translation_service.py     # Post-scan language switching orchestration
│   │   └── streaming_service.py       # SSE stream management
│   │
│   ├── repositories/                  # DB query layer (no logic here)
│   │   ├── user_repo.py
│   │   ├── contract_repo.py
│   │   ├── clause_repo.py
│   │   ├── scan_job_repo.py
│   │   ├── precedent_repo.py
│   │   └── report_repo.py
│   │
│   ├── db/
│   │   ├── session.py                 # SQLAlchemy async engine + session
│   │   └── base.py                    # Import all models for Alembic
│   │
│   ├── workers/
│   │   └── tasks.py                   # Celery task triggers (calls ai service)
│   │
│   └── utils/
│       ├── file_handler.py            # Uploadthing download + temp storage
│       ├── pdf_generator.py           # WeasyPrint + Jinja2 PDF builder
│       └── validators.py              # Input validation helpers
│
├── templates/                         # Jinja2 HTML → PDF report templates
│   ├── base.html                      # Base layout (fonts, colors, logo)
│   ├── cover.html                     # Cover page
│   ├── summary.html                   # Summary card section
│   ├── clauses.html                   # Clause-by-clause breakdown
│   ├── power.html                     # Power asymmetry section
│   ├── precedent.html                 # Legal precedent section
│   ├── counter_offers.html            # Counter-offer section
│   └── i18n/                          # Translated report template strings
│       ├── en.json
│       ├── es.json
│       ├── fr.json
│       ├── de.json
│       ├── pt.json
│       └── hi.json
│
├── static/                            # Static assets for PDF
│   ├── logo.png
│   └── report.css
│
├── migrations/                        # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_validators.py
│   └── integration/
│       ├── test_scan_api.py
│       ├── test_chat_api.py
│       ├── test_precedent_api.py
│       ├── test_translate_api.py
│       └── test_report_api.py
│
├── .env
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
├── Dockerfile
└── pyproject.toml
```

---

## 🧠 AI Service — `services/ai/`

```
services/ai/
│
├── pipelines/                         # One file per feature pipeline
│   ├── clause_extraction.py           # spaCy segmentation + clause splitting
│   ├── risk_classification.py         # Rule engine + LLM risk scoring
│   ├── consequence_generation.py      # Real-world consequence translator
│   ├── type_detection.py              # Contract type auto-detection
│   ├── power_analysis.py              # Power asymmetry scoring
│   ├── counter_offer.py               # Counter-offer RAG + generation
│   ├── summary.py                     # Plain-language summary card
│   ├── precedent_retrieval.py         # Legal precedent case matching
│   └── multilingual_pipeline.py       # Orchestrates: detect → translate → analyze → translate back
│
├── prompts/                           # All LLM prompts as .txt files
│   ├── risk_analysis.txt
│   ├── type_detection.txt
│   ├── consequence.txt
│   ├── summary.txt
│   ├── power_asymmetry.txt
│   ├── counter_offer.txt
│   └── precedent.txt
│
├── models/                            # LLM client + config
│   ├── openrouter_client.py           # OpenRouter async httpx client
│   ├── streaming.py                   # stream=True → SSE handler
│   └── model_config.py                # Model names, fallbacks, temperature
│
├── rag/                               # RAG pipeline
│   ├── embedder.py                    # Text → vectors via sentence-transformers
│   ├── retriever.py                   # pgvector similarity search
│   ├── vector_store.py                # pgvector connection + indexing
│   └── chat_chain.py                  # LangChain Q&A retrieval chain
│
├── rules/                             # Rule-based pre-processing
│   ├── regex_rules.py                 # 40+ regex patterns for risk signals
│   └── risk_mapper.py                 # Maps rule hits → risk categories
│
├── parser/                            # Document parsing
│   ├── pdf_parser.py                  # PyMuPDF text extraction
│   ├── docx_parser.py                 # python-docx extraction
│   └── fallback_parser.py             # unstructured.io fallback
│
├── translation/                       # Multilingual support
│   ├── detector.py                    # langdetect language detection
│   └── translator.py                  # DeepL API wrapper
│
├── cache/                             # Redis caching layer
│   ├── result_cache.py                # Cache scan results by contract hash
│   └── cache_config.py                # TTL settings, key naming conventions
│
├── data/                              # Source data for RAG corpora (pre-indexing)
│   ├── precedents/                    # Court case summaries from CourtListener
│   │   ├── employment/
│   │   ├── ip/
│   │   ├── nda/
│   │   └── vendor/
│   ├── favorable_clauses/             # Industry-standard favorable clause variants
│   │   ├── indemnity/
│   │   ├── ip_assignment/
│   │   ├── non_compete/
│   │   ├── auto_renewal/
│   │   └── limitation_of_liability/
│   └── synthetic_contracts/           # GPT-4o generated edge case contracts
│
├── utils/
│   ├── text_cleaner.py                # Text normalization helpers
│   ├── chunk_splitter.py              # Long contract chunking strategy
│   └── confidence_scorer.py           # RAG similarity × LLM confidence
│
├── tests/
│   ├── test_pipelines.py
│   ├── test_rules.py
│   ├── test_multilingual.py
│   └── test_rag.py
│
├── requirements.txt
└── Dockerfile
```

---

## ⚡ Worker — `apps/worker/`

```
apps/worker/
│
├── celery_app.py                      # Celery init + Upstash Redis config
│
├── tasks/
│   ├── process_contract.py            # Main scan pipeline task
│   ├── generate_summary.py            # Summary card task
│   ├── generate_counter_offer.py      # Counter-offer task
│   ├── generate_report.py             # PDF report task
│   ├── embed_contract.py              # pgvector embedding + indexing task
│   ├── translate_results.py           # Re-translate stored results to new language
│   └── cleanup_expired_reports.py     # Periodic task: delete reports past 48hr expiry
│
├── utils/
│   └── task_helpers.py                # Task status updates, error handling
│
├── requirements.txt
└── Dockerfile
```

---

## 📦 Shared Packages — `packages/`

```
packages/
│
├── types/                             # Shared TypeScript types
│   ├── contract.ts                    # Contract, ContractType enum
│   ├── clause.ts                      # Clause, RiskLevel enum
│   ├── scan.ts                        # ScanJob, ScanStatus
│   ├── power.ts                       # PowerAnalysisResult, LeveragePoint
│   ├── precedent.ts                   # PrecedentMatch, CaseReference, ConfidenceScore
│   ├── consequence.ts                 # ClauseConsequence, FinancialExposure
│   ├── report.ts                      # Report, ShareLink
│   └── api.ts                         # API request/response base types
│
├── utils/
│   ├── formatters.ts                  # Date, currency, score formatters
│   └── helpers.ts                     # General utility functions
│
└── config/
    ├── env.ts                         # Env variable validation
    ├── constants.ts                   # Risk colors, labels, contract types
    └── risk_taxonomy.ts               # 41 CUAD clause types + 40+ risk signal labels (shared frontend + backend)
```

---

## 🏗️ Infra — `infra/`

```
infra/
│
├── docker/
│   ├── Dockerfile.web                 # Next.js production image
│   ├── Dockerfile.api                 # FastAPI production image
│   ├── Dockerfile.ai                  # AI service image
│   └── Dockerfile.worker              # Celery worker image
│
├── nginx/
│   ├── nginx.conf                     # Reverse proxy config
│   └── local-ssl/                     # Self-signed cert for local HTTPS (required for WebCrypto API)
│       ├── localhost.crt
│       └── localhost.key
│
└── terraform/
    ├── main.tf
    └── variables.tf
```

---

## 🔧 Scripts — `scripts/`

```
scripts/
├── seed_precedents.py                 # Fetch case summaries from CourtListener → index to pgvector
├── index_favorable_clauses.py         # Load favorable_clauses/ data → embed + index to pgvector
├── generate_synthetic_contracts.py    # Generate edge case contracts via LLM → save to data/synthetic_contracts/
├── seed_demo_contracts.py             # Pre-cache demo contract scan results in Redis
├── test_openrouter.py                 # Verify OpenRouter connection + models
└── setup_dev.sh                       # One-command local dev setup
```

---

## 🧪 Integration Tests — `tests/`

```
tests/
├── conftest.py
├── test_full_scan_pipeline.py         # End-to-end: upload → scan → results
├── test_streaming.py                  # SSE stream integration test
├── test_multilingual_pipeline.py      # Detect → translate → analyze → translate back
├── test_precedent_retrieval.py        # RAG retrieval + confidence scoring
└── test_report_generation.py          # PDF generation test
```

---

## 🐳 Docker Compose

```yaml
# docker-compose.yml — services:
#
# web      → Next.js 15       → localhost:3000
# api      → FastAPI          → localhost:8000
# ai       → AI Service       → localhost:8001
# worker   → Celery worker
# redis    → Redis            → localhost:6379
# db       → Postgres         → localhost:5432

# docker-compose.test.yml — services:
#
# api-test → FastAPI (test mode)
# db-test  → Isolated Postgres (wiped after each run)
# redis-test → Isolated Redis
```

---

## 🗂️ Database Tables

```
users
contracts
clauses
scan_jobs
analysis_results
counter_offers
precedent_matches
reports
embeddings
```

---

## 🔑 Environment Variables — `.env.example`

```bash
# ── Frontend ─────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
UPLOADTHING_SECRET=
UPLOADTHING_APP_ID=

# ── Backend API ───────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname
REDIS_URL=rediss://upstash-url:6379
CLERK_WEBHOOK_SECRET=

# ── AI Service ────────────────────────────────────────────
OPENROUTER_API_KEY=
PRIMARY_MODEL=meta-llama/llama-3.3-70b-instruct:free
FAST_MODEL=google/gemini-2.0-flash-exp:free
DEEPL_API_KEY=
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ── Shared ────────────────────────────────────────────────
AI_SERVICE_URL=http://localhost:8001
ENVIRONMENT=development
```

---

## 🔄 Full Data Flow

```
Browser (Next.js 15)
  → Clerk Auth (middleware.ts enforces on all (app)/ routes)
  → WebCrypto AES-256-GCM encrypts file in browser
  → EncryptionBadge shows lock icon during upload
  → Uploadthing stores encrypted blob
  │
  └── POST /upload → FastAPI (services/api)
        → services/contract_service.py creates DB record
        → workers/tasks.py queues Celery job
              │
              └── apps/worker/tasks/process_contract.py
                    → services/ai: multilingual_pipeline.py (detect language)
                    →   LanguageDetectionBanner renders if non-English
                    → services/ai: parser/ extracts text
                    → services/ai: rules/ flags clauses
                    → services/ai: pipelines/risk_classification.py
                    → services/ai: pipelines/consequence_generation.py
                    → services/ai: pipelines/power_analysis.py
                    → services/ai: pipelines/precedent_retrieval.py
                    → services/ai: pipelines/summary.py
                    → services/ai: cache/result_cache.py → Upstash Redis
                    → services/ai: rag/embedder.py → pgvector
                    → services/api: repositories/ → Neon Postgres
              │
              └── GET /scan/{jobId}/stream (SSE)
                    → FastAPI StreamingResponse
                    → Next.js EventSource
                    → Zustand store updates
                    → Framer Motion renders UI
                    │
                    ├── ClauseList (risk cards animate in)
                    ├── PrecedentPanel (per HIGH-risk clause)
                    ├── PowerMeter (needle animates)
                    ├── SummaryCard (hero score)
                    └── EncryptionStatus (post-session key hash + deletion notice)

  POST /translate/{contractId}
    → apps/worker/tasks/translate_results.py
    → services/ai: multilingual_pipeline.py (translate stored results)
    → BilingualToggle re-renders analysis in selected language

  Periodic (Celery Beat)
    → apps/worker/tasks/cleanup_expired_reports.py
    → Deletes reports past 48hr expiry from storage + DB
```

---

*Production-grade monorepo. Every feature accounted for. Clean architecture.*