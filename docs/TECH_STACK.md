# 🏛️ LegalTech Contract Scanner — Tech Stack

> Fully finalized tech stack. Everything is free tier compatible.

---

## 🎨 Frontend

| Tool | Version | Purpose |
|------|---------|---------|
| Next.js | **16** | App Router, SSE streaming, API routes |
| TailwindCSS | **v4** | Utility-first styling |
| Framer Motion | **11.x** | Animations — risk cards, power meter, stagger effects |
| Shadcn/ui | **latest** | Pre-built accessible UI components |
| Zustand | **5.x** | Lightweight client-side state management |
| React PDF | **latest** | PDF preview in browser |

---

## ⚙️ Backend

| Tool | Version | Purpose |
|------|---------|---------|
| Python | **3.12** | Runtime |
| FastAPI | **0.115.x** | Main async API server |
| Uvicorn | **0.32.x** | ASGI server |
| Pydantic | **v2** | Request/response validation + LLM JSON output parsing |
| python-multipart | **latest** | File upload handling |

---

## 🤖 AI / LLM

| Tool | Version | Purpose |
|------|---------|---------|
| OpenRouter API | free tier | LLM gateway — no cost |
| Llama 3.3 70B Instruct | free model | Main risk analysis, JSON structured output |
| Gemini 2.0 Flash (exp) | free model | Auto-detection, summary card (fast calls) |
| LangChain | **0.3.x** | Q&A chat RAG pipeline |
| spaCy | **3.8.x** | Clause segmentation + NER |
| spaCy model | `en_core_web_sm 3.8.x` | English language model |
| langdetect | **1.0.9** | Contract language auto-detection |

### 📡 LLM Streaming
| Tool | Purpose |
|------|---------|
| OpenRouter `stream=True` | Enables token-by-token streaming from LLM |
| FastAPI `StreamingResponse` | Streams response with `text/event-stream` content type |
| Next.js `EventSource` API | Consumes SSE stream on the frontend — no extra library needed |

---

## 🗄️ Database

| Tool | Version | Purpose |
|------|---------|---------|
| PostgreSQL | **16** | Main relational database |
| Neon | free tier | Serverless Postgres hosting |
| SQLAlchemy | **2.x** | Only ORM — used exclusively by FastAPI backend |
| Alembic | **1.14.x** | Database migrations |
| pgvector | **0.8.x** | Vector embeddings storage for RAG Q&A chat |

> **Note:** Next.js never touches the DB directly. All DB access goes through FastAPI → SQLAlchemy → Neon.

---

## 📁 File Storage

| Tool | Version | Purpose |
|------|---------|---------|
| Uploadthing | **7.x** | Free file uploads, native Next.js integration |
| WebCrypto API | browser native | AES-256-GCM client-side encryption before upload |

> **Note:** Files are encrypted in the browser before leaving the device. The server only ever receives encrypted blobs. No AWS KMS or key management service needed.

---

## 📄 Document Parsing

| Tool | Version | Purpose |
|------|---------|---------|
| PyMuPDF (fitz) | **1.25.x** | PDF text extraction |
| python-docx | **1.1.x** | DOCX file parsing |
| unstructured | **0.16.x** | Fallback parser for messy/scanned documents |

---

## 🔄 Async / Queue

| Tool | Version | Purpose |
|------|---------|---------|
| Celery | **5.4.x** | Background task processing for heavy contract scans |
| Upstash Redis | free tier | Hosted Redis — job queue + demo result caching |

---

## 📤 PDF Report Export

| Tool | Version | Purpose |
|------|---------|---------|
| WeasyPrint | **62.x** | Server-side branded PDF generation |
| Jinja2 | **3.1.x** | HTML templates for PDF report layout |

---

## 🌍 Translation (Multilingual)

| Tool | Version | Purpose |
|------|---------|---------|
| DeepL API | free tier (500k chars/month) | Legal text translation — superior to Google Translate for legal language |

---

## 🔐 Auth

| Tool | Version | Purpose |
|------|---------|---------|
| Clerk | free tier | Authentication, user sessions, Google/GitHub login |

---

## 🚀 Deployment (All Free)

| Service | Purpose |
|---------|---------|
| **Vercel** | Next.js 16 frontend hosting |
| **Railway** | FastAPI + Celery worker hosting |
| **Neon** | Serverless Postgres database |
| **Upstash** | Serverless Redis |

---

## 🏗️ Architecture Flow

```
Browser (Next.js 16)
  │
  ├── Clerk Auth (login / session)
  │
  ├── WebCrypto API (AES-256-GCM encrypt file in browser)
  │
  ├── Uploadthing (upload encrypted blob)
  │
  └── POST /api/scan → FastAPI (0.115.x)
          │
          ├── Celery + Upstash Redis (async background job)
          │
          ├── PyMuPDF / python-docx (parse document)
          │
          ├── spaCy en_core_web_sm (segment into clauses)
          │
          ├── OpenRouter → Llama 3.3 70B (risk analysis)
          │       └── stream=True → FastAPI StreamingResponse
          │               └── text/event-stream → Next.js EventSource
          │
          ├── Pydantic v2 (validate structured JSON output)
          │
          ├── SQLAlchemy 2.x → Neon Postgres (store results)
          │
          └── pgvector (store embeddings for Q&A chat RAG)
                  │
                  └── LangChain 0.3.x (Q&A retrieval chain)

  Frontend renders:
  ├── Framer Motion (animated risk cards, power meter needle)
  ├── Shadcn/ui (components)
  ├── Zustand (client state)
  └── WeasyPrint → Jinja2 (branded PDF report download)
```

---

## 📦 Full Dependency Summary

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "tailwindcss": "^4.0.0",
    "framer-motion": "^11.0.0",
    "shadcn-ui": "latest",
    "zustand": "^5.0.0",
    "react-pdf": "latest",
    "@uploadthing/react": "^7.0.0"
  }
}
```

### Backend (`requirements.txt`)
```
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.9.0
python-multipart==0.0.12
sqlalchemy==2.0.36
alembic==1.14.0
pgvector==0.3.6
celery==5.4.0
redis==5.2.0
pymupdf==1.25.0
python-docx==1.1.2
unstructured==0.16.0
spacy==3.8.0
langdetect==1.0.9
langchain==0.3.0
langchain-openai==0.2.0
weasyprint==62.0
jinja2==3.1.4
httpx==0.28.0
python-dotenv==1.0.1
```

---