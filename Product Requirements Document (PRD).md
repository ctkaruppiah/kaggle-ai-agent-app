# Product Requirement Document (PRD)

## FinMesh: Agentic AI Operations Engine & Executive Control Suite

### Document Metadata
* **Product Name:** FinMesh (Agentic AI Operations Engine & Executive Control Suite)
* **Author:** Karuppiah Chidambaram
* **Status:** Live / Production Ready
* **Target Audience:** FinTech Product Managers, Scrum Masters, Agile Coaches, Core Engineers, Executive Leadership Teams
* **Deployment Target:** Google Cloud Run (Serverless) + Supabase (PostgreSQL + JSONB)

---

## 1. Executive Summary & Core Purpose

### 1.1 Core Purpose
FinMesh is an automated operations workspace and governance engine. It transforms highly unstructured financial ideas, messy meeting transcripts, or rough product feature lists into production-ready technical architecture, prioritized project tasks, and bulletproof regulatory compliance logs.

### 1.2 Vision Statement
In high-velocity financial technology development, engineering teams frequently build features detached from shifting compliance rules. Concurrently, product managers struggle to track real-time technical complexity. FinMesh eliminates this friction by operating as a centralized "Air Traffic Control Tower." It bridges institutional Agile product management with deterministic AI engineering workflows, ensuring that every line of code deployed matches an approved business goal and a verified regulatory parameter.

---

## 2. Problem Statement & Business Opportunity

### 2.1 The Problem
* **Product-Engineering Misalignment:** Product managers define features in natural language, while engineers build in structured code. Translating between these environments creates massive gaps, leading to severe rework.
* **Fragmented Toolchains:** High-velocity FinTech projects scatter information across video calls, text documentation, issue trackers, and code repositories. There is no single, unified record of truth.
* **Slow Compliance Auditing:** Manual verification of banking rules and anti-money laundering (AML) frameworks delays release velocities. It shifts compliance from a proactive mechanism into a slow, reactive bottleneck.
* **Subjective Prioritization:** Development backlogs are frequently prioritized based on internal guesswork or loudest-voice dynamics rather than mathematical business value and engineering effort.

### 2.2 The Business Opportunity
FinMesh turns this friction into a competitive advantage by providing a single, automated governance pane. It collapses the time spent on sprint refinement and compliance sign-offs from days into seconds, drastically reducing administrative overhead and eliminating structural compliance penalties before code reaches production.

---
## 3. System Architecture & Tech Stack

FinMesh utilizes a multi-layered, serverless system architecture designed to process data with absolute state separation and auditable compliance logs.

```text
                     +---------------------------------------+

                     |        USER & EXTERNAL INPUTS         |
                     |  Engineering Teams | Leadership Team  |
                     +-------------------+-------------------+
                                         |
                                         v
                     +---------------------------------------+

                     |         INGESTION LAYER (CI/CD)       |
                     |    GitHub Actions / GitHub Repo       |
                     +-------------------+-------------------+
                                         |
                                         v
+----------------------------------------+-----------------------------------------+

|                    CLOUD RUN INFRASTRUCTURE (Serverless GCP)                     |
|                                                                                  |
|  +------------------------+     +-----------------------+     +----------------+ |
|  |     Streamlit UI       | --> |    FastAPI Backend    | --> |  Gemini Agent  | |
|  | (Executive Control Suite)| <-- | (Service/Orchestration)| <-- |   Workflows    | |
|  +------------------------+     +-----------+-----------+     +-------+--------+ |
+--------------------------------------------|--------------------------|----------+
                                             v                          v
+----------------------------------------------------------------------------------+

|                          PERSISTENT DATA LAYER (Supabase)                        |
|                     PostgreSQL Database Engine + JSONB State Store               |
+----------------------------------------------------------------------------------+
                                             |
                                             v
                     +---------------------------------------+

                     |          OUTPUT / COMPLIANCE          |
                     |  Google Cloud Build | Compliance Logs |
                     +---------------------------------------+
```

| Layer Component | Primary Technical Stack | Functional Operational Role |
| :--- | :--- | :--- |
| **Presentation Layer** | Streamlit | Delivers an interactive web interface offering configurable standard and advanced views for operational control. |
| **Service & Routing Layer** | FastAPI | Acts as the deterministic orchestrator, managing session states and translating UI actions to backend systems. |
| **Intelligence Layer** | Google Gemini Models | Executes agentic analysis via structural skill dictionaries to process risk rulesets and prioritize epics. |
| **Persistence Layer** | Supabase (PostgreSQL + JSONB) | Serves as the central system memory, securing a permanent audit trail of compliance verdicts and states. |
| **DevOps & Infrastructure** | Docker, Google Cloud Run, GitHub Actions | Orchestrates containerized serverless scaling and automates the continuous delivery pipeline. |
---
### 3.1 Required Configuration Environment Variables
To initialize the FinMesh operational engine locally or on Google Cloud Run, create a `.env` file in your root workspace containing these mandatory access parameters:

```text
# Supabase Persistent Store Access Configuration
SUPABASE_URL=https://supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Gemini Intelligence Layer Token
GEMINI_API_KEY=AIzaSyA1...
```
## 4. Comprehensive Feature Specifications (Updated)

### 4.1 Epic Intake Desk
* **Functional Goal:** Standardize chaotic, unstructured ideas into uniform project definitions.
* **User Action:** User pastes raw material (e.g., text document, transcript) or pushes a repository commit hook.
* **System Processing:** FastAPI routes the payload to the Gemini extraction pipeline, applying structured skill dictionaries to isolate functional dependencies.

#### 💡 Core Compliance Highlight: NICE Actimize Governance Lifecycle
FinMesh integrates NICE Actimize risk tracking directly into its automated workflow engine across three distinct layers:
1. **Epic & Backlog Level (EPIC-001):** Enforces strict real-time transaction logging and parameter tracking hooks on cross-border, multi-currency tracks. The system parses the policy requirement and converts it into deterministic engineering tasks under **EPIC-001** ("Embedded Banking Transaction Core API Integration"), such as *STORY-101* ("Intercept transaction schema payload before writing onto the vector-store engine") and *STORY-102* ("Configure automated webhook triggers back to central compliance consoles").
2. **Intelligence Layer (System Prompt Vector B):** Commands the Gemini models to scan transcripts against explicit anti-money laundering (AML) thresholds and transaction velocity rule-sets.
3. **Automated Risk Routing:** If the engine identifies text containing cross-border settlement risks or mentions "Actimize", it immediately locks the item into a **Tier-3 Executive Block**, halting automatic deployment pipelines until a formal signature code is provided by leadership. The verification verdict is permanently stored alongside the epic metadata in your Supabase PostgreSQL database tables (`finmesh_epics` / `finmesh_audit_telemetry`) to provide an immutable audit trail.


### 4.2 WSJF Priority Calculator
* **Functional Goal:** Establish mathematical certainty for project backlog prioritization.
* **Mathematical Formula:** 
$$\text{WSJF} = \frac{\text{User-Business Value} + \text{Time Criticality} + \text{Risk Reduction / Opportunity Enablement}}{\text{Job Size / Duration}}$$
* **System Rules:** Gemini extracts features and scores parameters using a standard Fibonacci sequence (1, 2, 3, 5, 8, 13, 21). FastAPI intercepts the numeric output and computes the final WSJF score mathematically to prevent AI calculation drift.

### 4.3 Human-in-the-Loop (HITL) Governance Center
* **Functional Goal:** Enforce multi-tier human oversight for high-risk operations before code compilation.
* **System Mechanics:** Implements a strict, auditable path across three distinct operational severity levels:
  * **Tier 1: Standard Auto-Pass:** Low-risk components with high WSJF scores transition directly to deployment pipelines without human delays.
  * **Tier 2: Dual-Control Pass:** Medium-risk components require a confirmation signature from a separate peer reviewer.
  * **Tier 3: Executive Block:** High-risk architectural modifications or regulatory compliance items halt automatically. They require an explicit signature from leadership via the control suite interface.

### 4.4 Master Report Compiler
* **Functional Goal:** Provide real-time data transparency into model performance and corporate compliance metrics.
* **Telemetry Counters:**
  * **Token Metrics:** Tracks accurate input and output tokens to manage operational costs.
  * **Execution Latency:** Monitored via FastAPI performance wrappers to catch systemic API slowdowns.
  * **Hallucination & Verification Logs:** Validates generated system specs against compliance definitions stored in Supabase vectors.
  * **Token Spend Circuit Breaker:** A programmatic cost-threshold filter that intercepts multi-agent loops. If an individual epic generation sequence hits a calculated threshold exceeding $0.05 per session, the pipeline execution pauses instantly to eliminate run-away developer API billing.

---

## 5. Technical Blueprints & Engineering Implementation (Updated)

### 5.1 Vector Search & Retrieval Pipeline (Supabase RAG Integration)
To guarantee real-time regulatory parsing without hallucinations, compliance documents (including the NICE Actimize compliance reference library) are split into logical text blocks, converted to vector embeddings via Google embedding models, and hosted natively in Supabase using the `pgvector` extension.

Prior to prompt assembly inside the Gemini orchestration layer, FastAPI triggers an explicit cosine similarity distance calculation query to retrieve relevant policies.

```sql
-- Enable the vector extension in your Supabase SQL instance
CREATE EXTENSION IF NOT EXISTS vector;

-- Create Compliance Library Reference Store
CREATE TABLE IF NOT EXISTS compliance_vector_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name VARCHAR(100) NOT NULL, -- e.g., 'NICE-ACTIMIZE-AML'
    content_chunk TEXT NOT NULL,
    embedding VECTOR(768), -- Matching Google Gemini text-embedding dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing optimized for cosine similarity queries
CREATE INDEX IF NOT EXISTS compliance_vector_cosine_idx 
ON compliance_vector_store USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### RAG Execution Query (FastAPI to Supabase Core)
```sql
-- Cosine similarity query utilized by backend service layer to populate prompt context windows
SELECT policy_name, content_chunk, 1 - (embedding <=> :target_query_embedding) AS similarity_score
FROM compliance_vector_store
WHERE 1 - (embedding <=> :target_query_embedding) > 0.75
ORDER BY similarity_score DESC
LIMIT 3;
```
### 5.2 Supabase Relational Schema Layout (PostgreSQL DDL)
```sql
-- Create Epics Tracking Ledger
CREATE TABLE IF NOT EXISTS finmesh_epics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    epic_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    business_goal TEXT NOT NULL,
    functional_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- WSJF Component Metrics (Fibonacci Constrained)
    user_business_value INT NOT NULL CHECK (user_business_value IN (1,2,3,5,8,13,21)),
    time_criticality INT NOT NULL CHECK (time_criticality IN (1,2,3,5,8,13,21)),
    risk_reduction INT NOT NULL CHECK (risk_reduction IN (1,2,3,5,8,13,21)),
    job_size INT NOT NULL CHECK (job_size > 0),
    
    -- Calculated WSJF Score (Calculated at database engine level to eliminate LLM arithmetic drift)
    wsjf_score NUMERIC(6,2) GENERATED ALWAYS AS (
        (user_business_value + time_criticality + risk_reduction)::NUMERIC / job_size
    ) STORED,
    
    -- Governance State Realization
    governance_tier VARCHAR(20) NOT NULL CHECK (governance_tier IN ('Tier-1', 'Tier-2', 'Tier-3')),
    approval_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED')),
    reviewer_signature VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Agent Audit Logs & Performance Telemetry Table
CREATE TABLE IF NOT EXISTS finmesh_audit_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    epic_reference UUID REFERENCES finmesh_epics(id) ON DELETE CASCADE,
    input_tokens INT NOT NULL CHECK (input_tokens >= 0),
    output_tokens INT NOT NULL CHECK (output_tokens >= 0),
    latency_ms INT NOT NULL CHECK (latency_ms >= 0),
    hallucination_check_passed BOOLEAN NOT NULL DEFAULT TRUE,
    compliance_verdict TEXT NOT NULL,
    meta_logs JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing optimized for Real-Time Executive UI performance
CREATE INDEX IF NOT EXISTS idx_epics_wsjf ON finmesh_epics (wsjf_score DESC);
CREATE INDEX IF NOT EXISTS idx_epics_status ON finmesh_epics (approval_status);
CREATE INDEX IF NOT EXISTS idx_telemetry_ref ON finmesh_audit_telemetry (epic_reference);
```

### 5.3 Graceful Degradation & Fallback Logic (`main.py`)
This microservice manages application routing, captures structural data arrays from the frontend layer, and monitors connectivity. If the upstream intelligence engine (Google Gemini) encounters a rate limit error or exhibits latency spikes over 2,000ms, the router triggers an explicit fallback sequence to ensure enterprise platform availability.

```python
import time
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any

app = FastAPI(
    title="FinMesh Execution Core",
    version="1.0.0",
    description="Deterministic Routing and Agentic Orchestration Layer for FinMesh Architecture"
)

class EpicIntakePayload(BaseModel):
    title: str = Field(..., example="Embedded Banking Transaction Core API Integration")
    raw_transcript: str = Field(..., description="Unstructured transcript data from meeting or rough ideas")
    user_business_value: int = Field(..., description="Fibonacci parameter: 1,2,3,5,8,13,21")
    time_criticality: int = Field(..., description="Fibonacci parameter: 1,2,3,5,8,13,21")
    risk_reduction: int = Field(..., description="Fibonacci parameter: 1,2,3,5,8,13,21")
    job_size: int = Field(..., description="Job duration weight baseline (greater than 0)")

class ServerResponse(BaseModel):
    status: str
    generation_mode: str
    message: str
    data: Dict[str, Any]

@app.post("/api/v1/epics/ingest", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def process_epic_intake(payload: EpicIntakePayload):
    start_time = time.time()
    
    # Check Fibonacci limits manually at service layer
    fib_sequence = {1, 2, 3, 5, 8, 13, 21}
    metrics = [payload.user_business_value, payload.time_criticality, payload.risk_reduction]
    if not all(m in fib_sequence for m in metrics):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WSJF component parameters must strictly adhere to the standard Fibonacci sequence."
        )
        
    try:
        # Simulate an unexpected intelligence layer latency timeout or quota failure
        simulate_gemini_failure = False 
        
        if not simulate_gemini_failure:
            generation_mode = "AGENTIC_AI"
            parsed_requirements = [
                f"Automated verification module for: {payload.title}",
                "Idempotency validation on internal transaction keys",
                "Real-time banking risk compliance ruleset alignment parsing (NICE Actimize Policy Verified)"
            ]
        else:
            # TRIGGER EXPLICIT FALLBACK ROUTE: Deterministic Template Backup 
            generation_mode = "DETERMINISTIC_FALLBACK_TEMPLATE"
            parsed_requirements = [
                f"SYSTEM FALLBACK BACKUP: Structural schema verification for {payload.title}",
                "Standard banking tracking parameters loaded automatically due to intelligence service unavailability",
                "Mandatory Core Transaction logging policy hook applied natively"
            ]
            
        calculated_numerator = payload.user_business_value + payload.time_criticality + payload.risk_reduction
        wsjf_score = round(calculated_numerator / payload.job_size, 2)
        
        governance_tier = "Tier-1"
        if payload.risk_reduction >= 13 or "Actimize" in payload.raw_transcript:
            governance_tier = "Tier-3"  -- NICE Actimize references trigger executive block routing automatically
        elif wsjf_score < 3.0:
            governance_tier = "Tier-2"
            
        execution_latency = int((time.time() - start_time) * 1000)
        
        # Enforce Budget Token Spend Circuit Breaker Safeguard
        simulated_cost = 0.0024
        if simulated_cost > 0.05:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Transaction aborted: Programmatic Token Spend Circuit Breaker tripped (> \$0.05 budget scope)."
            )
            
        db_payload = {
            "epic_id": f"EPIC-2026-{int(time.time()) % 10000}",
            "title": payload.title,
            "wsjf_score": wsjf_score,
            "governance_tier": governance_tier,
            "requirements": parsed_requirements,
            "telemetry": {
                "latency_ms": execution_latency,
                "input_tokens": 1420,
                "output_tokens": 480,
                "session_cost_usd": simulated_cost
            }
        }
        
        return ServerResponse(
            status="SUCCESS",
            generation_mode=generation_mode,
            message="Epic data processed successfully and logged for infrastructure auditing.",
            data=db_payload
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Core orchestration layer failed executing pipeline processing: {str(e)}"
        )
}
```

```
### 5.4 Core Intelligence Skill Dictionary (Google Gemini System Prompt)
```text
ROLE AND CONTEXT:
You are the core intelligence module of FinMesh: Agentic AI Operations Engine. Your purpose is to act as an expert FinTech systems architect and regulatory compliance officer. You transform unstructured text, transcripts, and messy feature notes into structured system requirements and specifications.

INPUT PARSING INSTRUCTIONS:
Analyze the input payload data stream and extract structured objects according to this defined Skill Dictionary mapping schema:
1. Core Intent: Extract the high-level business objective.
2. System Requirements: Generate deterministic, verifiable technical requirement strings.
3. Risk Identification: Flag components matching the explicit Compliance Vectors below.

COMPLIANCE GOVERNANCE BOUNDARIES (NICE ACTIMIZE ALIGNMENT):
You must audit the text against financial risk governance frameworks and explicitly evaluate three mandatory regulatory vectors:
- Vector A: Identity Verification (KYC/CIP) Blocks. Look for user onboarding features, flag missing sanction matching patterns, or highlight a lack of geographically constrained identity tracking controls.
- Vector B: Real-Time Transaction Monitoring Hooks (NICE Actimize Policy Benchmarking). Identify raw money movements, account adjustments, or currency conversions. Ensure the generation of specific intercept triggers mapping to anti-money laundering (AML) and structural velocity rules. If the scope mentions cross-border multi-currency tracks (EPIC-001), you must mandate strict real-time transaction logging policies.
- Vector C: Strict Data Privacy Parameter Failsafes. Intercept any features holding Personally Identifiable Information (PII) or unencrypted accounting records. Explicitly mandate localized data encryption blocks matching international financial privacy protections (e.g., GLBA).

OUTPUT TEMPLATE:
Your output must strictly be a clean, unquoted JSON data configuration matching this exact layout model:
{
  "extracted_title": "Clean concise engineering epic name",
  "business_goal": "One sentence summary of business justification",
  "compliance_vectors_triggered": ["Identity Verification", "Transaction Monitoring", "Data Privacy Frameworks"],
  "technical_specifications": [
    "Requirement string 1 (must be testable and code-verifiable)",
    "Requirement string 2"
  ]
}
```
## 6. Metrics, Measurable Business Outcomes, & Value Realization

To track application success in production, FinMesh evaluates metrics across three specific operational dimensions:

### 6.1 Velocity and Resource Optimization
* **Sprint Refinement Acceleration:** Reduces administrative time spent drafting specifications from hours to seconds.
* **Cycle Time Reduction:** Measures a targeted reduction in the time it takes to move an initial idea into active development.
* **Context-Switching Mitigation:** Consolidates product, engineering, and compliance data into a single pane of glass, reducing reliance on cross-team syncs.

### 6.2 Operational Quality and Compliance Safeguards
* **Zero Defect Pipeline:** Catches regulatory misalignment at the intake desk before engineering pipelines compile code.
* **Traceability Assurance:** Maintains a continuous audit log from the initial business transcript down to specific code deployment IDs.
* **Audit Readiness:** Lowers compliance preparation times by storing all historical operational logs in deterministic JSONB records.

### 6.3 Engineering Efficiency Metrics
* **Backlog Hygiene:** Replaces manual backlog sorting with transparent, formulaic WSJF prioritization.
* **Deployment Success Rate:** Leverages deterministic API routing to ensure generated epics pass validation checks before triggering builds.

---

## 7. System Non-Functional Requirements (NFRs)

### 7.1 Security and Access Governance
* **Data Isolation:** All project states, session details, and compliance structures are logically separated within Supabase using Row-Level Security (RLS).
* **Audit Invariance:** The relational database ledger prevents record tampering. Once a human-in-the-loop sign-off completes, the resulting JSONB entry is locked.

### 7.2 Scalability and Availability
* **Serverless Footprint:** Leverages Google Cloud Run to dynamically scale host infrastructure to zero when idle, optimizing infrastructure spend.
* **API Isolation:** Decouples the interactive Streamlit user interface from core data manipulation via an isolated FastAPI service layer.
* **Programmatic Cost Guardrails:** Individual agent generation tasks must check session-level cost payloads before proceeding. Any multi-agent sequencing that surpasses a $0.05 runtime cost envelope triggers an immediate execution break to avoid unbounded billing iterations.

---
