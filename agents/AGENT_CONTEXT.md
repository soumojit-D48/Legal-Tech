# AGENT_CONTEXT.md — Shared Context for All Agents
# LegalTech AI Contract Scanner

> Every agent reads this file first. It summarizes the critical facts every agent needs to operate.
> For full details, always defer to PRD.md, TECH_STACK.md, FOLDER_STRUCTURE.md, STEPS_BACKEND.md.

---

## What This Product Is

An AI-powered legal contract analysis platform. Users upload a contract (PDF or DOCX), the system analyzes every clause for risk, generates plain-English explanations, scores power imbalance, suggests counter-offers, retrieves legal precedents, and produces a shareable PDF report. Analysis completes in under 10 seconds for standard contracts.

**Target users:** Freelancers, employees, small business owners — non-lawyers who need to understand contracts they receive.

---

## Architecture in One Diagram

```
Browser (Next.js 15 — apps/web/)
  ↓ Clerk auth + WebCrypto encryption + Uploadthing
FastAPI (services/api/ — port 8000)
  ↓ Celery task queue via Upstash Redis
AI Service (services/ai/ — port 8001)
  ↓ OpenRouter (Llama 3.3 70B + Gemini Flash) + sentence-transformers
PostgreSQL on Neon + pgvector
Redis on Upstash (queue + cache + pub/sub)
```

---

## Agent Boundaries (Hard Lines)

| Agent | Owns | Never Touches |
|-------|------|---------------|
| Backend | services/api/, services/ai/, apps/worker/ | apps/web/ |
| Frontend | apps/web/ | services/, apps/worker/ |
| Database | models/, migrations/, repositories/, scripts/ | endpoints, pipelines, components |
| Reviewer | Reviews all of the above | Creates no code |
| Orchestrator | Coordinates all agents | Creates no code |

---

## The Two Free LLM Models (Never Use Anything Else)

- **PRIMARY:** `meta-llama/llama-3.3-70b-instruct:free` via OpenRouter — used for risk analysis, consequence generation, power asymmetry, counter-offers, precedent synthesis
- **FAST:** `google/gemini-2.0-flash-exp:free` via OpenRouter — used for contract type detection, summary card, pros/cons

Both accessed via `services/ai/models/openrouter_client.py`. Model names imported from `services/ai/models/model_config.py`. Never hardcoded anywhere else.

---

## The Three Vector Indexes in pgvector

All stored in the `embeddings` table, differentiated by `embedding_type`:

| Type | Used For | Scope | When Populated |
|------|----------|-------|----------------|
| `contract_qa` | Q&A chat retrieval | Per contract | After each scan |
| `favorable_clause` | Counter-offer RAG | Shared (all users) | Once via seeding script |
| `precedent` | Legal precedent retrieval | Shared (all users) | Once via seeding script |

Embedding model: `all-MiniLM-L6-v2` (384 dimensions). Runs locally on AI service. No API cost.

---

## SSE Event Format (Backend → Frontend)

The scan results page streams in real time via Server-Sent Events:

```
# Regular clause result
data: {"event_type": "clause_result", "data": {ClauseResult}}\n\n

# Power analysis (arrives after all clauses)
data: {"event_type": "power_result", "data": {PowerAnalysisResult}}\n\n

# Summary card (arrives last)
data: {"event_type": "summary_result", "data": {SummaryCard}}\n\n

# Keep-alive (every 15 seconds)
event: heartbeat\ndata: {}\n\n

# Scan finished
event: complete\ndata: {"job_id": "...", "contract_id": "..."}\n\n
```

Redis channel name: `scan:{jobId}`

---

## API Endpoint Summary

All endpoints under `/api/v1/`. All require Clerk JWT except: `/health`, `/webhooks/clerk`, `/report/share/{shareUuid}`.

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /upload | Start a scan job |
| GET | /scan/{jobId} | Poll scan status |
| GET | /scan/{jobId}/stream | SSE stream |
| GET | /contracts | List user's contracts |
| GET | /contracts/{id} | Full contract detail |
| DELETE | /contracts/{id} | Delete contract |
| GET | /summary/{contractId} | Summary card + pros/cons |
| GET | /power/{contractId} | Power asymmetry result |
| GET | /precedent/{clauseId} | Legal precedent for clause |
| POST | /counter-offer/{clauseId} | Trigger counter-offer generation |
| GET | /counter-offer/{clauseId} | Poll counter-offer result |
| POST | /chat/{contractId} | Q&A chat (streaming) |
| POST | /translate/{contractId} | Switch result language |
| POST | /report/generate/{contractId} | Trigger PDF generation |
| GET | /report/{reportId} | Get report (authenticated) |
| GET | /report/share/{shareUuid} | Get report (public, checks expiry) |

---

## Security Non-Negotiables

1. Every query that returns user data must filter by `user_id`
2. Encryption key never logged, never stored in DB
3. JWT verified on every protected endpoint via Clerk JWKS
4. Webhook signature verified before processing
5. Share links are UUID v4 (non-guessable) and expire in 48 hours
6. Rate limits per PRD Section 7.4: upload 10/hr, scan 10/hr, chat 100/day, counter-offer 50/day

---

## Environment Variables (Keys — Values in .env)

```bash
# API
DATABASE_URL          # Neon PostgreSQL connection string (asyncpg)
REDIS_URL             # Upstash Redis URL (rediss://)
CLERK_WEBHOOK_SECRET  # For verifying Clerk webhook payloads

# AI Service
OPENROUTER_API_KEY    # OpenRouter API key
PRIMARY_MODEL         # meta-llama/llama-3.3-70b-instruct:free
FAST_MODEL            # google/gemini-2.0-flash-exp:free
DEEPL_API_KEY         # DeepL API key for translation
EMBEDDING_MODEL       # all-MiniLM-L6-v2

# Frontend
NEXT_PUBLIC_API_URL         # FastAPI base URL
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY
UPLOADTHING_SECRET
UPLOADTHING_APP_ID

# Shared
AI_SERVICE_URL        # http://localhost:8001 (or Railway URL)
ENVIRONMENT           # development or production
```

---

## Supported Languages

English (en), Spanish (es), French (fr), German (de), Portuguese (pt), Hindi (hi).

Translation via DeepL API (free tier: 500k chars/month). Legal glossary at `services/ai/translation/legal_glossary.json` ensures terminology accuracy.

---

## Risk Levels and Categories

**Levels:** HIGH, MEDIUM, LOW, SAFE
**Categories:** indemnity, ip_assignment, non_compete, auto_renewal, limitation_of_liability, termination, payment, governing_law, other

HIGH and MEDIUM → get consequence generation, power scoring, LLM analysis
HIGH only → get legal precedent retrieval, counter-offer generation
GREEN (no rule matches) → get SAFE result, no LLM calls

---

## The 9 Database Tables

`users`, `contracts`, `clauses`, `scan_jobs`, `analysis_results`, `counter_offers`, `precedent_matches`, `reports`, `embeddings`

Full column specs in Database Agent prompt and PRD.md Section 4.3.