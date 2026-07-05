# 🌐 FinMesh Smart Executive Control Suite — Enterprise Portfolio Desk

### 🛡️ Enterprise-Grade Governance, Telemetry, and Automated Auditing for Agentic Workflows
FinMesh is a production-grade, highly responsive agile portfolio governance desk and automated audit framework built with Streamlit and the Google GenAI SDK, leveraging a live cloud data layer for real-time compliance tracking[cite: 2].

---

## 🎯 1. Project Overview & Business Value
The FinMesh Smart Executive Control Suite is a centralized management and audit platform built to bridge the gap between high-level corporate strategy and automated technical execution[cite: 1]. While autonomous AI agents accelerate software delivery, enterprise environments require strict compliance, clear ownership, and strict cost controls[cite: 1]. FinMesh provides financial institutions and enterprise teams with an auditable control pane[cite: 1]. It maps engineering epics directly to corporate OKRs, visualizes technical value streams, calculates economic priorities using data-driven frameworks, tracks real-time LLM token costs, and enforces a mandatory Human-in-the-Loop (HITL) gate before any deployment[cite: 1].

---

## 🏗️ 2. System Architecture & Technical Specifications

### 🗄️ Data & Persistence Layer
The backend database is powered by a live Supabase relational database PostgreSQL instance to ensure robust storage and retrieval[cite: 1, 2]. To ensure lightning-fast read operations and eliminate expensive database table joins at scale, the application implements a high-performance Single-Table Entity-Attribute-Value (EAV) / JSONB Document Store pattern[cite: 2]. System state mutations, user stories, fine-grained tasks, risk ledgers, and compliance verdicts are instantly persisted to downstream tables to ensure total data integrity across the platform lifetime[cite: 1].

### 📊 Database Schema (public.epic_state_store)
All functional requirement matrices, structural roadmaps, and configuration attributes are nested dynamically within binary JSON fields (state_json) tied to their master portfolio key[cite: 2]. The workspace_key acts as the table primary key tracking active enterprise epics from EPIC-001 through EPIC-007[cite: 2]. Within the root JSON schema mappings, state_json->'stories' houses nested requirements objects, agile point sizes, sprint delivery allocations, and requirement compliance tags[cite: 2]. Technical specifications, contract endpoints, and architecture blueprints are persisted via state_json->'sdd' using explicit Upsert operations (INSERT ... ON CONFLICT UPDATE)[cite: 2]. Corporate alignments use state_json->'okr' to track strategic objective goals, while economic prioritization variables for business value, time criticality, risk reduction, and job size map cleanly to state_json->'wsjf'[cite: 2].

### 🔄 Dual-Tier Workspace & Reporting Pipeline
The workspace utilizes a standard mode focused on routine engineering tracking, itemized backlog scoping, and rapid task creation[cite: 1]. It pairs this with an advanced reporting mode that unlocks deeper regulatory oversight features while preserving program-level rollup visibility via a dual-scope metrics pipeline[cite: 1, 2]. The Isolated Focus Context (This Epic) filters dashboard widgets to report individual focus frames cleanly, meaning that evaluating EPIC-001 isolates its exact footprint of 1 Epic, 3 Stories, 3 Tasks, and 16 SP, while switching epics dynamically pulls an independent dataset[cite: 2]. Conversely, the Program Rollup Context (All Epics) runs global aggregation loops across all 7 row entries inside the table layer, compiling live metrics into a detailed Program-Wide Master Report Rollup matrix grid[cite: 2].

| Epic ID | Name | Stories | Tasks | Story Points | WSJF Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **EPIC-001** | Digital KYC Onboarding (Identity) | 3 | 3 | 16 SP | 2.50 |
| **EPIC-002** | EPIC 1 Created | 0 | 0 | 0 SP | 3.00 |
| **EPIC-004** | EPIC 4 TEST | 0 | 0 | 0 SP | 3.00 |
| **EPIC-006** | EPIC 6 Generated for Testing | 0 | 0 | 0 SP | 3.00 |

---

## ⚙️ 3. Automated Enterprise Governance Engines & Component Breakdown

### 📋 Epic Intake Desk & OKR Aligner
The system features a formal metadata schema that registers parent business streams, mapping explicit user narratives, target releases, and delivery cycles[cite: 1]. This structural approach translates development streams directly to high-level corporate objectives, key results, and broader enterprise themes[cite: 1]. The integrated OKR Aligner mechanism automatically fetches active epic records from the live session state, extracts root okr blocks, and cross-verifies active requirements trees against enterprise strategic themes in real-time to output clean semantic execution logs that track specific risk reduction tags[cite: 2].

### 🛡️ Compliance Auditor & Lifecycle Management
To enforce corporate safety, the platform explicitly links each epic to a verified regulatory framework, ensuring downstream agent tasks are executed within regulatory boundaries[cite: 1]. The Strategic Aligner & Compliance Auditor programmatically queries the active System Design Document (sdd) nested within the document table row, extracting individual API route metrics and path contracts to test them against corporate data policies and log execution audits[cite: 2]. This infrastructure breaks down complex epics into clear development units that track assigned engineering nodes, story points, functional task properties, independent compliance check flags, and time footprints[cite: 1].

### 📈 Economic Prioritization: WSJF Calculator Engine
FinMesh eliminates guesswork by mathematically scoring backlog items based on user value, time criticality, and risk reduction to automate standard Scaled Agile Framework (SAFe) business evaluations[cite: 1, 2]. The Real-Time Economic Telemetry Streamer computes the Cost of Delay divided by Job Size, streaming calculations live to update the record state directly into the data summaries[cite: 2].

WSJF Score = (Cost of Delay) / (Job Size)

### 🔑 Human-In-The-Loop (HITL) Governance Center
Responsible AI gatekeeping blocks autonomous systems from executing structural migrations or deployments without manual human attestation[cite: 1]. The governance center generates an official audit trail sign-off requiring a definitive verdict selection, an official text signature identifier, and contextual justifications written directly to the permanent database ledger[cite: 1].

### 🚧 Risk Governance & Infrastructure Tracing
A multi-dimensional blocker and dependency grid continuously logs technical friction points across crucial engineering verticals like package version conflicts, missing software modules, CI/CD pipeline failures, and security vulnerabilities[cite: 1]. Accountability is strictly enforced by assigning clear severity tiers and firm calendar targets[cite: 1]. This tracing visually maps technical transactions from origin to persistence, while an administrative command button features a workspace telemetry reset to wipe active parameters back to a clean slate[cite: 1].

---

## 📊 4. Real-Time Telemetry & Reporting Engine

### 📈 Top-Level Executive Dashboard
The top-level executive dashboard aggregates live program ratios and total delivery velocities across all epics[cite: 1]. It monitors financial computation overhead by calculating cumulative text metrics and precise operational spend down to micro-cents, allowing managers to see the exact fiscal impact of running agentic LLM workflows[cite: 1].

### 🗺️ Multi-Agent Telemetry Tracking Matrix
This matrix tracks active processing modules executing background tasks[cite: 1]. It exposes critical performance metadata, logging real-time text consumption metrics, operational execution speeds, downstream valuation flags, and sequential logical paths to keep agent behavior entirely transparent[cite: 1].

---

## 🛠️ 5. Setup & Installation

### 📂 Step 1: Navigate to the App Workspace
Open your preferred terminal or command prompt and switch to your local project directory:
cd c:/kaggle-ai-agent-app

### 💻 Step 2: Configure the Virtual Environment
Create and boot an isolated Python virtual environment to manage dependencies securely without system-wide conflicts:

For Windows:
python -m venv .venv
.venv\Scripts\activate

For macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

### 📦 Step 3: Install Required Dependencies
Ensure your environment is active, then install the necessary application framework packages:
pip install -r requirements.txt

---

## ⚡ 6. Running the App

### 🔑 Step 1: Set your Gemini API Key
Configure your access credentials via environment variables so the application can communicate securely with the Google GenAI models:

For Windows (CMD):
set GEMINI_API_KEY=your_api_key_here

For Windows (PowerShell):
$env:GEMINI_API_KEY="your_api_key_here"

For macOS / Linux:
export GEMINI_API_KEY="your_api_key_here"

### 🚀 Step 2: Launch the Application Stream
Start the application instance through the command line interface:
streamlit run app.py

The client opens automatically inside your local web browser environment at: http://localhost:8501

---

## 📁 7. Project Structure

The root directory contains the following core engineering artifacts and directories:

├── .venv/               # Python Virtual Environment (ignored)
├── .gitignore          # Standard Git ignore configurations
├── requirements.txt    # Streamlit & Google GenAI SDK dependencies
├── app.py              # Core Streamlit application & custom UI design
└── README.md           # Master System Documentation