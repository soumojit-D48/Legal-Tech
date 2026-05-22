# PRD — LegalTech AI Contract Scanner
**Product Requirements Document**
**Version:** 1.0
**Status:** Active Development

---

## 1. Product Overview

### 1.1 What Is This Product

LegalTech AI Contract Scanner is a full-stack web application that uses artificial intelligence to analyze legal contracts. A user uploads any contract — employment agreement, NDA, freelance/SOW, SaaS subscription, lease, partnership, IP license, loan, M&A, or other — and the system automatically reads every clause, identifies risks, explains consequences in plain English, scores power imbalances, generates negotiation counter-offers, retrieves relevant legal precedents, and produces a shareable branded PDF report. The entire analysis completes in under 10 seconds for a standard contract.

The product is built for non-lawyers: freelancers, employees, small business owners, and anyone who needs to sign a contract but cannot afford or does not have time to consult a lawyer for every document they receive.

### 1.2 Core Problem Being Solved

Most people sign contracts without fully understanding what they are agreeing to. Legal language is deliberately complex. Hiring a lawyer for contract review costs $300–$500/hr. Free online tools either give generic summaries or just restate the clause in slightly simpler language. No existing tool combines clause-level risk detection, real-world consequence translation, power asymmetry visualization, counter-offer generation, legal precedent grounding, and multilingual support in a single workflow.

### 1.3 Who This Is For

**Primary users:**
- Freelancers and independent contractors reviewing client SOW/freelance agreements
- Employees reviewing employment contracts and non-competes
- Small business owners reviewing vendor contracts and SaaS subscriptions
- Startup founders reviewing partnership and investor agreements

**Secondary users:**
- Legal ops teams doing high-volume contract triage
- HR teams standardizing offer letter reviews
- Anyone in a non-English-speaking market who receives contracts in a foreign language

### 1.4 Product Goals

- Reduce time to understand a contract from hours to under 60 seconds
- Make professional-grade contract risk analysis accessible to anyone without legal training
- Give users actionable outputs they can immediately use: counter-offer language, negotiation emails, shareable reports
- Support contracts in any language, analyze in English, return results in the user's language
- Be the most visually clear and memorable contract analysis tool available

---

## 2. User Flows

### 2.1 Primary Flow — Upload to Full Analysis

1. User lands on the product, signs up or logs in via Clerk (Google or GitHub OAuth supported)
2. User navigates to the Upload page
3. User drags and drops or selects a PDF or DOCX contract file
4. The file is encrypted in the browser using AES-256-GCM (WebCrypto API) before it leaves the device
5. The encrypted file is uploaded via Uploadthing
6. The system automatically detects the contract language
7. If non-English: a banner appears — "Spanish contract detected — analyzing as [user role] perspective"
8. A scan job is created and queued
9. The UI transitions to the live scan results page
10. Clauses animate in one by one via SSE streaming — each lights up RED, YELLOW, or GREEN
11. A counter ticks up in real time: "3 HIGH RISK · 7 MEDIUM · 12 SAFE"
12. As clauses render, the user can hover/click any clause to see its consequence panel
13. Once all clauses are processed, the Summary Card renders at the top
14. The Power Asymmetry Meter animates its needle
15. The full analysis is complete — user can explore all features from this single results page

### 2.2 Secondary Flows

**Counter-Offer:** User clicks any HIGH-risk clause → counter-offer panel slides open → three rewritten versions (Aggressive / Balanced / Conservative) appear side by side with the original → user copies their preferred version or the pre-written negotiation email

**Legal Precedent:** User clicks the precedent tab on any HIGH-risk clause → panel shows up to 3 real court cases with names, years, outcomes, and an overall enforcement likelihood score with confidence percentage

**Q&A Chat:** User navigates to the Chat page for a contract → types a natural language question about the contract → system retrieves relevant clauses via RAG and streams an answer with specific clause citations

**Report Export:** User clicks "Share Report" or "Download PDF" → branded PDF is generated server-side with all analysis sections → shareable UUID link is created with 48-hour expiry → user can send the link to a colleague or client who views the full report in-browser without an account

**Language Switch:** User with a non-English contract can toggle between the original language analysis and English at any point post-scan

**Contract History:** User visits the Dashboard to see all previously scanned contracts with their overall risk scores, contract types, and scan dates

---

## 3. Features — Full Specification

---

### FEATURE 1: Clause Risk Scanner

**What it does:**
Automatically segments the uploaded contract into individual clauses, runs each clause through a two-pass risk analysis system, and assigns every clause a risk level (HIGH / MEDIUM / LOW / SAFE) along with a risk category, plain-English explanation, worst-case scenario, negotiability flag, and confidence score.

**How it works:**

Pass 1 — Rule Engine (fast, deterministic):
The parsed contract text is segmented into clause units using spaCy sentence segmentation. A rule engine containing 40+ regex patterns scans each clause for known risk signals. Risk signals include: indemnity language, automatic renewal clauses, IP assignment language, non-compete and non-solicitation clauses, unilateral modification rights, limitation of liability caps, termination for convenience without cause, liquidated damages, arbitration-only dispute clauses, and more. Each matched signal maps to a preliminary risk category and triage level: GREEN (no signals), YELLOW (1–2 signals), RED (3+ signals or known high-risk patterns).

Pass 2 — LLM Analysis (smart, explainable):
Only YELLOW and RED clauses from Pass 1 are sent to the LLM. The LLM receives: the contract type, the user's role (e.g., "the employee", "the vendor"), and an array of flagged clauses. It returns structured JSON for each clause containing: clause_id, risk_level, risk_category, plain_english summary, worst_case_scenario, negotiable flag, and confidence score (0.0–1.0).

**Risk Categories:**
- `indemnity` — clause makes user financially responsible for third-party claims
- `ip_assignment` — clause transfers intellectual property rights to the other party
- `non_compete` — clause restricts user's ability to work elsewhere
- `auto_renewal` — clause automatically renews contract without explicit action
- `limitation_of_liability` — clause caps what user can recover in damages
- `termination` — clause gives other party broad termination rights
- `payment` — clause contains unfavorable payment or clawback terms
- `governing_law` — clause assigns unfavorable jurisdiction
- `other` — flagged by rule engine but not fitting a specific category

**Risk Levels:**
- `HIGH` — clause poses significant legal or financial risk, requires attention before signing
- `MEDIUM` — clause is one-sided or unusual, should be reviewed
- `LOW` — clause is standard but worth being aware of
- `SAFE` — clause poses no notable risk

**Confidence Scores:**
Any clause with a confidence score below 0.7 displays a "⚠️ Verify with attorney" indicator. This is a product-level commitment to honest output — the system does not overclaim certainty.

**UI behavior:**
Clauses stream into the results page one by one via SSE as they are processed. Each clause card pulses when it appears. The color (red/yellow/green) animates in. A counter in the top right ticks up in real time. Clicking a clause card expands it to show the full risk analysis.

---

### FEATURE 2: Contract Type Auto-Detection

**What it does:**
Before the main scan begins, the system automatically classifies what type of contract was uploaded and identifies the roles of each party. This classification feeds into every downstream prompt, making all risk assessments role-aware and contract-type-specific.

**How it works:**
A single LLM call is made using only the first 1000 tokens of the contract. The model classifies the contract into one of: Employment, NDA, Freelance/SOW, SaaS Subscription, Lease/Rental, Partnership, IP License, Loan, M&A, Other. It also extracts party roles (e.g., ["employer", "employee"] or ["client", "contractor"]). The user's role is inferred from the context or can be manually selected.

**UI behavior:**
Before clauses start streaming in, a banner displays: "Employment Agreement detected — analyzing as employee perspective." If the auto-detection confidence is below 0.8, a manual contract type selector is shown so the user can correct it.

---

### FEATURE 3: Real-World Consequence Translator

**What it does:**
For every HIGH and MEDIUM risk clause, translates the abstract legal risk into a specific, personalized, concrete scenario of what could actually happen to this user in their role if they sign without negotiation.

**How it works:**
Uses a template + LLM hybrid approach. Pre-built consequence templates exist for each risk category (e.g., indemnity → financial exposure scenario, IP assignment → portfolio rights scenario). The LLM personalizes the template based on the user's stated role, the contract type, and the contract value if known. The LLM is prompted to be specific — to use dollar amounts, timeframes, and concrete situations. It never uses vague language like "may result in." It states what WILL happen in the worst case.

**Output fields per clause:**
- `headline` — 8-word worst-case summary (e.g., "You lose all portfolio rights permanently")
- `scenario` — 2-sentence specific story of what goes wrong
- `financial_exposure` — dollar amount or "unlimited"
- `probability` — Low / Medium / High
- `similar_case` — optional real-world example headline

**UI behavior:**
The consequence is shown inside the expanded clause card. The `financial_exposure` field with a dollar sign is given prominent visual treatment — bold, large, colored red if the amount is significant. This is intentional: the visceral financial number drives user engagement and decision-making.

---

### FEATURE 4: Plain-Language Summary Card

**What it does:**
After all clauses are analyzed, generates a single hero card that gives the user a complete picture of the contract in under 10 seconds of reading.

**How it works:**
One LLM call after the full scan completes. Receives: contract type, all HIGH-risk clause summaries, all MEDIUM-risk clause summaries, and overall risk distribution statistics. Returns a structured summary.

**Output fields:**
- `one_liner` — single sentence describing the contract and its key implication
- `should_you_sign` — one of: "Yes as-is", "Yes with changes", "No"
- `top_3_concerns` — three most important things to address before signing
- `top_2_positives` — two favorable aspects of the contract
- `overall_risk_score` — 0 to 100 numeric score
- `negotiating_power` — "Strong", "Moderate", or "Weak"

**UI behavior:**
Rendered as the hero element at the top of the results page. The risk score number (e.g., "74/100") is displayed large and color-coded. The verdict ("Yes with changes") is shown prominently. The three concerns are bullet-listed below. This card is designed to be screenshot-worthy — users should want to share it.

---

### FEATURE 5: Power Asymmetry Meter

**What it does:**
Scores how much the contract structurally favors one party over the other and visualizes it as an animated gauge/meter — from -100 (heavily favors the counterparty) to +100 (heavily favors the user).

**How it works:**
The full clause list with risk assessments is sent to the LLM, which scores each clause from -100 to +100 based on who it favors. The average of all scores produces the overall power score. The LLM also identifies the top key imbalances and the user's leverage points (clauses where they have negotiating power).

**Output fields:**
- `power_score` — integer from -100 to +100
- `power_label` — human-readable label (e.g., "Strongly Favors Counterparty", "Slightly Favors You", "Balanced")
- `key_imbalances` — array of {clause, why, score} for the most one-sided clauses
- `leverage_points` — array of strings describing where the user has negotiating leverage

**UI behavior:**
An animated gauge component with a needle that swings from center to the calculated position. The animation plays on first render. Color gradient from green (balanced center) to red (extreme ends). Below the meter: "This contract gives the other party 3.2x more termination rights than you." Leverage points are listed below the meter as actionable items.

**Productization note:**
The system tracks power asymmetry across all contracts a user has scanned. The dashboard shows: "Your last 5 contracts averaged -42 (you're consistently signing unfavorable contracts)." This is a long-term retention feature.

---

### FEATURE 6: Counter-Offer Generator

**What it does:**
For every HIGH-risk clause, generates three ready-to-use rewritten versions of the clause (Aggressive, Balanced, Conservative) that are fairer to the user, along with a pre-written negotiation email the user can send to the other party.

**How it works:**
RAG + LLM hybrid. At query time, the HIGH-risk clause is embedded using sentence-transformers and a similarity search is run against the favorable clause corpus in pgvector. The top similar favorable clause variant is retrieved. The LLM then takes: the original clause, the retrieved favorable reference, the contract type, and the user's role, and generates three rewritten versions at different levels of aggressiveness. It also writes a 2-sentence negotiation email explaining the proposed change professionally.

**Output fields:**
- `aggressive` — {clause text, explanation of why this is better}
- `balanced` — {clause text, explanation}
- `conservative` — {clause text, explanation}
- `negotiation_email` — ready-to-send 2-sentence email

**UI behavior:**
Clicking any HIGH-risk clause reveals a "Generate Counter-Offer" button. Clicking it opens a side panel showing the original clause on the left in red and the rewritten clause on the right in green, with a diff-style highlight of what changed. Three tabs switch between Aggressive / Balanced / Conservative versions. A "Copy Negotiation Email" button is the hero CTA. The copy action triggers a success animation.

---

### FEATURE 7: Pros vs Cons Snapshot

**What it does:**
Generates a balanced two-column view of what is favorable and unfavorable in the contract across five dimensions: financial, liability, IP, exit rights, and obligations.

**How it works:**
Single LLM call post-scan. Receives the full clause analysis and returns structured pros and cons arrays tagged by dimension, plus a one-sentence overall verdict.

**Output fields:**
- `pros` — array of {dimension, point} for favorable aspects
- `cons` — array of {dimension, point} for unfavorable aspects
- `verdict` — one-sentence overall assessment

**UI behavior:**
Two-column card with green checkmarks on the left (pros) and red X marks on the right (cons). Items animate in with a stagger effect — one by one, alternating sides. Each item is tagged with its dimension (Financial, Liability, IP, etc.) as a small badge. Clean, scannable, screenshot-worthy.

---

### FEATURE 8: Clause Q&A Chat

**What it does:**
After a contract is scanned, the user can ask any natural language question about the contract and receive a streaming answer that cites the specific clause it is drawing from.

**How it works:**
At scan time, the contract is chunked and embedded using sentence-transformers and stored in pgvector. The Q&A chat uses a LangChain ConversationalRetrievalChain: the user's question is embedded, the top relevant contract chunks are retrieved via similarity search, and these chunks plus the question are sent to the LLM which generates a grounded answer. The system prompt instructs the model to always cite the specific clause or section it is referencing and to say explicitly if the answer is not in the contract.

**Key behaviors:**
- Answers are streamed token-by-token via SSE
- Every answer includes a clause citation (e.g., "Section 4.2 states...")
- If the contract does not address the question, the model says so — it never fabricates contract terms
- Questions can be follow-up questions that reference the previous answer
- Example questions the system is optimized for:
  - "Can I work for a competitor after I leave?"
  - "What happens to my equity if I'm terminated?"
  - "Can the client reject my work without paying me?"
  - "What are the notice periods in this contract?"
  - "Who owns the code I write on weekends?"

**UI behavior:**
Full-page chat interface for the selected contract. Chat bubbles with the user's question on the right and the AI answer on the left. The clause citation is shown as a highlighted pill below the answer — clicking it scrolls the clause list to that clause. Input field at the bottom with send button and keyboard shortcut support.

---

### FEATURE 9: Legal Precedent + Confidence Score

**What it does:**
For HIGH-risk clauses, retrieves real court case summaries that involved similar clause language and synthesizes what courts have typically decided, with an overall enforcement likelihood and confidence score.

**How it works:**
Pre-indexed: 500+ court case summaries from CourtListener API are embedded and stored in pgvector, organized by jurisdiction, outcome, and clause type. These are indexed once via the `seed_precedents.py` script.

At analysis time: each HIGH-risk clause is embedded, and a similarity search retrieves the top 3 most relevant case summaries. The LLM synthesizes these into a precedent summary — explaining what courts have typically decided when similar clauses were contested, whether this clause is likely to be enforced as written, and what the confidence level is.

The confidence score is calculated as: RAG retrieval similarity score × LLM self-rated confidence. This produces a grounded, honest confidence number rather than an arbitrary one.

**Output fields:**
- `precedent_summary` — synthesized paragraph on what courts have decided
- `enforcement_likelihood` — "Very Likely", "Likely", "Uncertain", or "Unlikely"
- `confidence_score` — 0 to 100
- `cited_cases` — array of {name, year, outcome} for the matched cases

**UI behavior:**
A "Legal Precedent" tab on each HIGH-risk clause card. Clicking it shows the PrecedentPanel. Each matched case is shown as a CaseCard with the case name, year, jurisdiction, and outcome. The ConfidenceBadge shows the percentage prominently (e.g., "87% confidence"). The enforcement likelihood is shown as a colored label.

Example rendered output: "Based on 3 similar cases (including Donahue v. Permanente, 2019), courts have ruled this non-compete clause unenforceable in California — Confidence: 87%."

---

### FEATURE 10: End-to-End Encryption

**What it does:**
Ensures the user's contract document is encrypted in the browser before it leaves their device, so the server only ever receives and stores an encrypted blob. The encryption key never leaves the browser session.

**How it works:**
When the user selects a file for upload, the browser generates an AES-256-GCM encryption key using the WebCrypto API. The file is encrypted client-side before the upload to Uploadthing begins. The encrypted blob is what gets stored. The encryption key is held in browser session memory only — it is passed in the Authorization header for processing and is never persisted to the database or any server log. When the user's session ends, the key is deleted from memory.

**UI behavior:**
A lock icon with a pulsing animation appears during the encryption + upload step with the text "Your document is encrypted before leaving your device." After the session ends (or when the user explicitly clears their data), the UI shows: "Contract data deleted from servers. Session key: [truncated hash shown for transparency]." An EncryptionStatus panel is accessible from the contract detail page at any time to show the current encryption state.

**Note on scope:**
The encryption architecture is real — WebCrypto AES-256-GCM is genuine client-side encryption. The limitation is that the key is passed in-session for the backend to process the document. True zero-knowledge processing (homomorphic encryption on contract text) is a future roadmap item. The current implementation is labeled accurately.

---

### FEATURE 11: Multilingual Support

**What it does:**
Accepts contracts in any language, performs analysis in English for maximum accuracy, and returns all results in the user's preferred language. Supports English, Spanish, French, German, Portuguese, and Hindi at launch.

**How it works:**
The multilingual pipeline runs as the first step of every scan:

1. `langdetect` identifies the contract language
2. If non-English: DeepL API translates the full contract to English (DeepL is specifically chosen over Google Translate for its superior handling of legal terminology)
3. All analysis pipelines run on the English translation
4. All result fields (plain_english summaries, scenario descriptions, counter-offer clauses, etc.) are translated back to the user's preferred language via DeepL before being stored and returned
5. A bilingual glossary JSON file maps jurisdiction-specific legal terms to their correct equivalents in each target language to preserve accuracy

Post-scan language switching is also supported: a user can toggle the display language at any time after scan completion via the BilingualToggle component, which triggers a worker task to re-translate the stored results.

**UI behavior:**
- Auto-detection banner: "Spanish contract detected — analyzing as [role] perspective"
- LanguageSwitcher in the navbar for manual language selection
- BilingualToggle on the results page for side-by-side English / original language view
- The shareable PDF report also renders in the user's preferred language
- Language preference is persisted per user in the database

---

### FEATURE 12: Shareable Risk Report

**What it does:**
Generates a branded, professional PDF report of the full contract analysis that the user can download or share via a unique link. The report looks like it came from a professional legal tools platform.

**How it works:**
After the scan completes, the user can trigger report generation. A Celery worker task calls the PDF generation service which uses WeasyPrint and Jinja2 HTML templates to render the report. The report is structured into sections: cover page, summary card, clause-by-clause breakdown with risk colors, power asymmetry section, legal precedent section, and counter-offer section.

A UUID-based shareable link is created with a 48-hour expiry. The link is publicly accessible (no login required for viewing) so users can share reports with colleagues or clients. A Celery Beat periodic task cleans up expired report files and database records.

**Report sections:**
1. Cover page — contract name, overall risk score, scan date, user role
2. Executive Summary — one-liner, should-you-sign verdict, top 3 concerns, top 2 positives
3. Risk Overview — risk score meter, risk distribution chart, power asymmetry score
4. Clause Analysis — every clause with its risk level, category, plain-English explanation
5. High-Risk Deep Dives — consequence + legal precedent for each HIGH risk clause
6. Counter-Offer Suggestions — rewritten clause variants for all HIGH-risk clauses
7. Pros vs Cons Summary — the full two-column snapshot

**UI behavior:**
"Download PDF" button generates and downloads the report. "Share Report" button generates the link, copies it to clipboard, and shows a success state. The shareable link opens a read-only branded report viewer (no account required). The report viewer is responsive — judges or colleagues can read it on their phones.

---

## 4. Data Architecture

### 4.1 Contract Processing Pipeline

Every uploaded contract goes through this ordered pipeline:

```
1. File received (encrypted blob)
2. Decrypt for processing
3. Parse: PDF → PyMuPDF, DOCX → python-docx, fallback → unstructured
4. Language detection (langdetect)
5. Translation to English if needed (DeepL)
6. Clause segmentation (spaCy en_core_web_sm)
7. Rule engine triage (regex_rules.py → risk_mapper.py)
8. Contract type detection (LLM call, first 1000 tokens)
9. Risk classification (LLM call on RED + YELLOW clauses)
10. Consequence generation (LLM call per HIGH/MEDIUM clause)
11. Power asymmetry analysis (LLM call on full clause list)
12. Legal precedent retrieval (RAG: embed clause → pgvector search → LLM synthesis)
13. Summary card generation (LLM call, post all-clause analysis)
14. Pros vs cons generation (LLM call, post summary)
15. Embedding for Q&A RAG (sentence-transformers → pgvector)
16. Translate results back to user language if needed (DeepL)
17. Store all results in Postgres
18. Cache results in Redis (for fast re-retrieval and demo pre-computation)
19. Stream results to frontend via SSE as they complete
```

### 4.2 RAG Corpora

Three separate vector indexes are maintained in pgvector:

**Contract Q&A Index:**
Each uploaded contract's text is chunked (overlap chunking strategy for context preservation) and embedded at scan time using `all-MiniLM-L6-v2`. Used exclusively for the per-contract Q&A chat feature. Scoped per contract — a user's chat only retrieves from their contract's chunks.

**Favorable Clause Corpus Index:**
Pre-indexed at setup time using `index_favorable_clauses.py`. Contains industry-standard and user-favorable clause variants sourced from the CUAD dataset and generated synthetic variants. Organized by clause type. Used for counter-offer generation retrieval. Not user-specific — shared across all users.

**Legal Precedent Index:**
Pre-indexed at setup time using `seed_precedents.py`. Contains 500+ court case summaries from CourtListener API across employment, IP, NDA, and vendor contract domains, with metadata: jurisdiction, year, outcome, clause type. Used for legal precedent retrieval. Not user-specific — shared index.

### 4.3 Database Schema

**users** — Clerk user ID, email, preferred language, created_at
**contracts** — id, user_id, file_ref (Uploadthing), contract_type, detected_language, party_roles, created_at
**clauses** — id, contract_id, text, position_index, risk_level, risk_category, plain_english, worst_case, financial_exposure, negotiable, confidence
**scan_jobs** — id, contract_id, status (queued/processing/complete/failed), progress_pct, created_at, completed_at
**analysis_results** — id, contract_id, overall_risk_score, should_sign, top_concerns, top_positives, negotiating_power, power_score, power_label, leverage_points
**counter_offers** — id, clause_id, aggressive_clause, balanced_clause, conservative_clause, negotiation_email
**precedent_matches** — id, clause_id, precedent_summary, enforcement_likelihood, confidence_score, cited_cases (JSONB)
**reports** — id, contract_id, pdf_path, share_uuid, expires_at, language, created_at
**embeddings** — id, contract_id, chunk_text, chunk_index, embedding (vector), embedding_type (contract_qa / favorable_clause / precedent)

---

## 5. LLM Strategy

### 5.1 Models

**Primary model:** `meta-llama/llama-3.3-70b-instruct:free` via OpenRouter
Used for: risk classification, consequence generation, power analysis, counter-offer generation, precedent synthesis, summary card

**Fast model:** `google/gemini-2.0-flash-exp:free` via OpenRouter
Used for: contract type detection, pros/cons generation — fast single-call tasks that don't need the full 70B model

**Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers (runs locally, no API cost)
Used for: all vector embedding — Q&A contract chunks, favorable clause corpus, legal precedent index

### 5.2 Structured Output

All LLM calls use `response_format: json_object` and strict system prompts instructing the model to return only valid JSON with no preamble. All responses are validated with Pydantic v2 before being stored. If a response fails validation, it is retried once with an error correction prompt before falling back to a default error state.

### 5.3 Streaming

The risk classification pipeline uses `stream=True` via OpenRouter. FastAPI returns a `StreamingResponse` with `text/event-stream` content type. The frontend consumes it via the native `EventSource` API. Each SSE event contains a complete clause result JSON object. This is what enables the real-time clause-by-clause animation on the results page.

### 5.4 Context Management

Long contracts (50+ pages) are handled via a parallel batching strategy: clauses are processed in parallel batches of 10. Each batch is a separate LLM call. Results are merged and ordered by clause position index before being returned. The rule engine runs first on all clauses before any LLM calls are made, which means LLM calls are only made on the subset of flagged clauses — keeping costs and latency low even for large contracts.

---

## 6. Async Processing Architecture

All heavy processing runs as Celery background tasks. The FastAPI API never blocks waiting for LLM calls. The flow is:

1. API receives upload → immediately creates a scan_job record with status "queued" → returns the job_id to the frontend
2. Frontend opens an SSE connection to `/scan/{jobId}/stream`
3. Celery worker picks up the job → processes pipeline → updates scan_job status and progress_pct in Redis → pushes clause results to a Redis pub/sub channel
4. SSE endpoint subscribes to the Redis channel → streams events to the connected frontend client as they arrive
5. When the pipeline completes → scan_job status set to "complete" → SSE stream closes

Workers:
- `process_contract` — main scan pipeline (runs all 19 pipeline steps)
- `generate_summary` — summary card generation (triggered after all clauses complete)
- `generate_counter_offer` — on-demand when user requests a counter-offer
- `generate_report` — PDF report generation
- `embed_contract` — pgvector embedding at scan time
- `translate_results` — on-demand when user switches language post-scan
- `cleanup_expired_reports` — Celery Beat periodic task, runs every hour, deletes reports past 48hr expiry

---

## 7. Security and Privacy

### 7.1 Authentication

All `(app)/` routes are protected via Clerk middleware. The Clerk JWT is verified on every FastAPI request via the `security.py` module. No authenticated routes are accessible without a valid session.

### 7.2 Encryption

Files are encrypted client-side with AES-256-GCM using the WebCrypto browser API before upload. The encryption key is session-scoped and never persisted server-side. The server only ever stores encrypted blobs in Uploadthing storage.

### 7.3 Data Isolation

All database queries are scoped to the authenticated user's ID. A user cannot access another user's contracts, scans, results, or reports. Shareable report links are the only intentional exception — these are public by design but are UUID-based (non-guessable) and expire after 48 hours.

### 7.4 Rate Limiting

API endpoints are rate-limited using Upstash Ratelimit (Redis-backed). Limits:
- Upload endpoint: 10 uploads per user per hour
- Scan endpoint: 10 scans per user per hour
- Chat endpoint: 100 messages per user per day
- Counter-offer endpoint: 50 requests per user per day

---

## 8. UI/UX Principles

### 8.1 The Results Page Is Everything

The central design challenge of this product is the scan results page. Every feature must be accessible from this single page without full navigation away. The layout is:
- Top: Summary Card (hero element — risk score, verdict, top concerns)
- Below left: Clause list (animated, filterable by risk level)
- Below right: Detail panel (shows consequence / counter-offer / precedent for selected clause)
- Floating: Power Asymmetry Meter (always visible, anchored to viewport)
- Bottom: Pros vs Cons Snapshot

### 8.2 Animation is Functional

Animations in this product are not decorative — they communicate information. The clause-by-clause stagger animation tells the user "analysis is happening in real time." The power meter needle swing communicates magnitude. The diff color coding (red original, green rewrite) communicates improvement. Every animation serves a purpose.

### 8.3 One Visceral Moment Per Feature

Each feature is designed to have one moment that makes users stop and pay attention:
- Risk Scanner: the IP clause reveal ("You permanently transfer all portfolio rights")
- Power Meter: the needle swinging to -65 with "3.2x more termination rights"
- Counter-Offer: the copy email button (one click = professional leverage)
- Legal Precedent: real case name + 87% confidence ("reads like Westlaw")
- Chat: follow-up question that nuances the answer based on IP clause
- Multilingual: full re-render in Spanish

### 8.4 The Report Must Look Expensive

The shareable PDF report must look like it came from a $500/hr law firm's internal tooling. Custom typography, color-coded severity bands, professional logo treatment. If a user shares this report with their employer or client, it must make a strong impression. The report is also a marketing asset — anyone who receives a shared link sees the product.

---

## 9. Non-Functional Requirements

### 9.1 Performance Targets

- Standard contract (5–15 pages): full analysis complete in under 10 seconds
- Large contract (50+ pages): full analysis complete in under 30 seconds
- Q&A chat first token: under 2 seconds
- Counter-offer generation: under 3 seconds
- PDF report generation: under 8 seconds
- SSE first clause event: under 3 seconds from scan job start

### 9.2 Reliability

- Celery tasks retry up to 3 times on failure with exponential backoff
- LLM call validation failures trigger one correction-prompt retry before error state
- SSE connections re-establish automatically on disconnect with state recovery from Redis
- All scan results are persisted in Postgres — results page can be refreshed and restored at any time

### 9.3 Scalability

- Stateless FastAPI workers — horizontally scalable on Railway
- Celery workers independently scalable
- All shared state in Redis and Postgres — no local state on workers
- pgvector indexes support up to 1M+ vectors before requiring partitioning

---

## 10. Out of Scope (Explicit Exclusions)

The following are explicitly not in scope for the current build:

- Real-time CourtListener API calls during scan (pre-indexed corpus is used instead)
- True zero-knowledge homomorphic processing (roadmap)
- Document signing integration (DocuSign webhook is a roadmap item)
- Collaborative contract review (multiple users on one contract)
- Mobile native app (web app is responsive but no native iOS/Android)
- Contract drafting from scratch (analysis only, not generation)
- Legal advice disclaimer removal (all outputs include "not legal advice" footer)

---

## 11. Key Constraints and Decisions

**OpenRouter free tier models only:** All LLM inference uses free-tier models via OpenRouter. This means occasional rate limiting on heavy usage. The caching layer (Redis) mitigates this by serving cached results for identical clause inputs.

**DeepL free tier (500k chars/month):** Sufficient for development and early production. Character count per contract is typically 5,000–50,000 chars. The free tier supports approximately 10–100 full contract translations per month before upgrade.

**sentence-transformers runs locally:** The embedding model runs in the AI service container, not via API. This means no embedding API costs and no external dependency for the RAG pipeline, but it requires adequate memory in the AI service container (512MB minimum).

**No fine-tuning:** All LLM capabilities are achieved via prompt engineering and RAG. No custom model training. This is a deliberate decision for speed of iteration and cost.

**Next.js 15 App Router only:** No Pages Router. All routing uses the App Router. Server Components are used where possible. Client Components are explicitly marked with `"use client"`.

---

## 12. Glossary

- **Clause** — a distinct section or provision within a contract that establishes a specific right, obligation, or condition
- **Risk Level** — HIGH, MEDIUM, LOW, or SAFE — the assessed risk a clause poses to the user
- **Power Score** — a -100 to +100 integer measuring how much the contract structurally favors one party
- **Counter-Offer** — a rewritten version of a risky clause proposed by the user to the other party
- **Precedent** — a prior court case involving similar clause language whose outcome informs the likelihood of enforcement
- **Confidence Score** — a 0–100 percentage indicating how certain the system is about its precedent analysis, derived from RAG retrieval similarity and LLM self-assessment
- **SSE** — Server-Sent Events — a unidirectional HTTP streaming protocol used to push clause results from server to browser in real time
- **RAG** — Retrieval-Augmented Generation — a technique where relevant documents are retrieved from a vector database and provided to the LLM as context before generation
- **pgvector** — a PostgreSQL extension that stores and queries vector embeddings
- **CUAD** — Contract Understanding Atticus Dataset — a dataset of 510 annotated legal contracts with 41 clause type labels, used to calibrate the rule engine
- **CourtListener** — an open-access database of U.S. court opinions, used as the source for the legal precedent corpus

---

*This document covers the complete product scope. All three documents — PRD.md, TECH_STACK.md, FOLDER_STRUCTURE.md — together provide full context for any agent or developer to understand and build this system.*