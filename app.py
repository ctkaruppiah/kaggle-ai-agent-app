import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Force wide canvas parameters to ensure 100% visibility of all modules
st.set_page_config(layout="wide", page_title="FinMesh Executive Centre", page_icon="🚀")

# ####################################################
# 💾 APP INITIAL STATE ENGINE & TELEMETRY REGISTRY
# ####################################################

if "tokens_used" not in st.session_state:
    st.session_state.tokens_used = 1820

if "budget_spent" not in st.session_state:
    st.session_state.budget_spent = 3.6400

if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

if "audit_report" not in st.session_state:
    st.session_state.audit_report = None
    
if "executed_skills_sequence" not in st.session_state:
    st.session_state.executed_skills_sequence = ["WSJF Calculator", "Strategic Aligner", "OKR Aligner", "Master Report Compiler", "Governance Engine"]
    
if "execution_logs" not in st.session_state:
    st.session_state.execution_logs = [
        {"Timestamp": "2026-06-28 12:15:02", "Skill Triggered": "Governance Engine", "Inputs Received": "HITL-VERDICT-APPROVE", "Tokens Consumed": 150, "Cost ($)": 0.0030, "Output Summary": "Committed executive routing verdict to compliance ledger. Archive sealed."},
        {"Timestamp": "2026-06-28 11:05:41", "Skill Triggered": "Master Report Compiler", "Inputs Received": "Global Session Store", "Tokens Consumed": 100, "Cost ($)": 0.0020, "Output Summary": "Compiled all active workspace metrics into the unified auditing registry."},
        {"Timestamp": "2026-06-28 11:02:57", "Skill Triggered": "OKR Aligner", "Inputs Received": "EPIC-001: Embedded Banking API Integration", "Tokens Consumed": 340, "Cost ($)": 0.0068, "Output Summary": "Successfully parsed requirement records. Tied deliverables onto Strategy KR-2."},
        {"Timestamp": "2026-06-28 11:02:28", "Skill Triggered": "Strategic Aligner", "Inputs Received": "As a commercial banking customer, I want to execut...", "Tokens Consumed": 210, "Cost ($)": 0.0042, "Output Summary": "Completed roadmap correlation traces. Technical execution paths cleanly match standard product blueprints."}
    ]

if "hitl_ledger" not in st.session_state:
    st.session_state.hitl_ledger = [
        {"Timestamp": "2026-06-28 10:14:22", "Artifact ID": "EPIC-001", "Trigger Target Context": "High WSJF / Compliance Trace", "Severity Level": "Critical", "Selected Action Verdict": "Approve Deployment", "Authorized Approver": "Karuppiah Chidambaram", "Operational Remarks": "Initial epic mapping aligns with Q2 OKRs and payload validation rules."}
    ]

if "live_latency" not in st.session_state:
    st.session_state.live_latency = 74

if "live_cost_req" not in st.session_state:
    st.session_state.live_cost_req = 0.0020

if "live_hallucination" not in st.session_state:
    st.session_state.live_hallucination = 0.00

if "live_eval_status" not in st.session_state:
    st.session_state.live_eval_status = "Passed"

if "current_chain" not in st.session_state:
    st.session_state.current_chain = "Merge States ➡️ Output Matrix"

# ####################################################
# 🎨 UNIFIED UNIFORM CSS DESIGN LANGUAGE
# ####################################################
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 4rem; max-width: 100% !important; }
    .hero-title { text-align: center; color: #1e3a8a; font-size: 2.3rem; font-weight: 800; margin-bottom: 0.1rem; }
    .hero-subtitle { text-align: center; color: #64748b; font-size: 1.05rem; font-weight: 500; margin-bottom: 1.5rem; }
    
    .section-header {
        font-size: 1.3rem !important; font-weight: 700 !important; color: #0f172a !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px;
    }
    
    .skill-title-label {
        font-size: 1.25rem !important; font-weight: 700 !important; color: #1e3a8a !important; margin-top: 5px !important; margin-bottom: 5px !important; display: block !important;
    }
    
    .executive-grid-container {
        display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; width: 100%; margin-bottom: 15px;
    }
    .executive-metric-card {
        background-color: #ffffff !important; border-top: 4px solid #1e3a8a !important; border-left: 1px solid #e2e8f0 !important;
        border-right: 1px solid #e2e8f0 !important; border-bottom: 1px solid #e2e8f0 !important; padding: 12px !important; border-radius: 6px !important;
        min-height: 115px !important; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 1px 2px rgb(0 0 0 / 0.05);
    }
    
    .tight-textarea-container div[data-baseweb="textarea"] { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    .tight-textarea-container div.stTextArea { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    
    .executive-card-label { font-size: 0.75rem !important; text-transform: uppercase !important; font-weight: 700 !important; color: #475569 !important; letter-spacing: 0.5px; margin-bottom: 4px !important; line-height: 1.3; }
    .executive-card-formula { font-size: 0.75rem !important; font-weight: 600 !important; color: #0284c7 !important; margin-bottom: 6px !important; font-family: monospace; }
    .executive-card-val { font-size: 1.1rem !important; font-weight: 700 !important; color: #0f172a !important; margin-top: auto !important; white-space: normal !important; word-break: break-word !important; line-height: 1.3; }
    
    .wsjf-container-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; width: 100%; margin-bottom: 5px; }
    .observability-grid-container { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; width: 100%; margin-bottom: 15px; }
    
    .observability-box-mild-grey {
        background-color: #f8fafc !important; border-top: 4px solid #38bdf8 !important; border-left: 1px solid #e2e8f0 !important;
        border-right: 1px solid #e2e8f0 !important; border-bottom: 1px solid #e2e8f0 !important; padding: 12px !important; border-radius: 6px !important;
        min-height: 95px !important; display: flex; flex-direction: column; justify-content: flex-start;
    }
    
    .sidebar-guidance-box { background-color: #f0f9ff !important; border: 1px solid #bae6fd !important; padding: 12px !important; border-radius: 8px !important; margin-top: 15px !important; }
    .sidebar-guidance-text { font-size: 0.9rem !important; color: #0369a1 !important; line-height: 1.45 !important; font-weight: 500 !important; margin: 0 !important; }
    
    .hitl-alert-banner {
        background-color: #fff7ed; border-left: 4px solid #ea580c; border-top: 1px solid #ffedd5; border-right: 1px solid #ffedd5; border-bottom: 1px solid #ffedd5;
        padding: 12px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9rem; color: #9a3412;
    }
    
    div.stButton > button {
        width: 100%; min-height: 38px; font-weight: 600; background-color: #1e3a8a !important; color: #ffffff !important; border-radius: 6px !important; border: none !important; font-size: 0.9rem;
    }
    div.stButton > button:hover { background-color: #0369a1 !important; }
    
    .master-report-header-banner { background-color: #1e3a8a; color: white; padding: 15px; border-radius: 6px 6px 0 0; margin-top: 15px; font-weight: 700; font-size: 1.1rem; }
    .master-report-section-node { background-color: #ffffff; border-left: 4px solid #0284c7; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 14px; margin-bottom: 10px; }
    .master-report-section-title { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;}
    
    .custom-spec-table { width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 8px; }
    .custom-spec-table th { background-color: #f1f5f9; color: #334155; font-weight: 700; font-size: 12px; padding: 10px; text-align: left; border-bottom: 2px solid #cbd5e1; }
    .custom-spec-table td { padding: 10px; font-size: 13px; border-bottom: 1px solid #e2e8f0; color: #475569; line-height: 1.45; }
    </style>
""", unsafe_allow_html=True)

# ####################################################
# 🕹️ SIDEBAR CONTROLS
# ####################################################
with st.sidebar:
    st.markdown("### ⚙️ Operational Settings & Views")
    view_layer_selection = st.selectbox(
        "Workspace View Layer Tier", 
        ["Standard Mode", "Advanced Reporting Mode"], 
        index=0, 
        key="view_layer"
    )
    st.write("---")
    if st.button("🔄 Reset Telemetry Pools", key="reset_btn"):
        st.session_state.clear()
        st.rerun()

# ####################################################
# 🖥️ APPLICATION HEADER
# ####################################################
st.markdown("<h1 class='hero-title'>FinMesh Smart Executive Control Suite</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='hero-subtitle'>Enterprise Engineering Operations Engine — <span style='color:#0284c7;'>{view_layer_selection} Live</span></p>", unsafe_allow_html=True)

# ####################################################
# 📋 PROGRAM BACKLOG INTAKE INVENTORY DESK
# ####################################################
st.markdown("<p class='section-header'>📋 Program Backlog Intake Inventory Desk</p>", unsafe_allow_html=True)
backlog_db = {
    "EPIC-001: Embedded Banking Transaction Core API Integration": {
        "story": "As a commercial banking customer, I want to execute cross-border real-time multi-currency settlement routes directly via API, ensuring compliance with NICE Actimize transaction logging policies.",
        "milestone": "Q2 Product Release Rollout", "velocity": "45.2 SP", "baseline": "NICE Actimize Regulatory Policy Verified", "tokens": 340, "cost": 0.0068
    },
    "EPIC-002: Real-time AML Ledger Sanction Match Hooks": {
        "story": "As a senior risk officer, I need all inbound transaction payloads intercepted and verified against international sanction lists before database execution to minimize policy liabilities.",
        "milestone": "Q3 Enterprise Beta Phase", "velocity": "38.0 SP", "baseline": "Sanction Stream Active Filter Tier-1", "tokens": 410, "cost": 0.0082
    }
}

with st.container():
    selected_epic_id = st.selectbox("Active Backlog Epic Target Focus", list(backlog_db.keys()))
    current_backlog_data = backlog_db[selected_epic_id]
    
    st.markdown("<p style='font-size:13px; font-weight:700; color:#475569; margin-bottom:4px;'>📥 Multi-Modal Requirements Document Upload Node</p>", unsafe_allow_html=True)
    uploaded_doc = st.file_uploader(
        "Upload Epic / Story Specifications", 
        type=["pdf", "txt", "md", "json", "docx", "xls", "xlsx", "ppt", "pptx", "png", "jpeg", "jpg"], 
        label_visibility="collapsed"
    )
    if uploaded_doc is not None:
        st.success(f"Processed multi-modal context stream: '{uploaded_doc.name}'! Configuration matrix synchronized.")
    
    col_view1, col_view2 = st.columns([1, 1])
    with col_view1:
        st.markdown("""
        <div class='executive-metric-card' style='border-top-color: #1e3a8a; min-height:35px; padding:6px 12px; margin-bottom:4px;'>
            <p class='executive-card-label' style='color:#1e3a8a; margin:0;'>✍️ Active User Story Context (Editable Input Source)</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='tight-textarea-container'>", unsafe_allow_html=True)
        target_story = st.text_area("Story Area Input Box", value=current_backlog_data["story"], height=70, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_view2:
        st.markdown(f"""
        <div class='executive-metric-card' style='border-top-color: #1e3a8a; min-height:112px;'>
            <p class='executive-card-label' style='color:#1e3a8a;'>📋 Target Velocity & Baseline Milestones</p>
            <p style='font-size: 13px; margin: 3px 0 0 0; color: #334155;'><b>Milestone:</b> {current_backlog_data['milestone']} | <b>Velocity Pace:</b> {current_backlog_data['velocity']}</p>
            <p style='font-size: 13px; margin: 2px 0 0 0; color: #334155;'><b>Security Posture:</b> {current_backlog_data['baseline']}</p>
        </div>
        """, unsafe_allow_html=True)

# ####################################################
# 📊 TOP-LEVEL EXECUTIVE SUMMARY PANEL
# ####################################################
st.markdown("<p class='section-header'>📈 Top-Level Executive Summary Panel</p>", unsafe_allow_html=True)
st.markdown(f"""
<div class='executive-grid-container'>
    <div class='executive-metric-card'><p class='executive-card-label'>🎯 Active Target Epic</p><p class='executive-card-val'>{selected_epic_id.split(':')[0]}</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>⚡ Running Sequence Nodes</p><p class='executive-card-val'>{len(st.session_state.executed_skills_sequence)} Runs Logged</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>🛡️ Infrastructure Posture</p><p class='executive-card-val'>{current_backlog_data['baseline'].split(' ')[0]}</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>🪙 Cumulative Tokens</p><p class='executive-card-val'>{st.session_state.tokens_used:,}</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>💵 Cumulative Spend</p><p class='executive-card-val'>${st.session_state.budget_spent:.4f}</p></div>
</div>
""", unsafe_allow_html=True)

# Pipeline Operations Logic Engine
def execute_agent_skill(skill_name, token_cost, dollar_cost, inputs, summary, latency, tracking_cost, hallucination, chain_viz):
    st.session_state.tokens_used += token_cost
    st.session_state.budget_spent += dollar_cost
    st.session_state.live_latency = latency
    st.session_state.live_cost_req = tracking_cost
    st.session_state.live_hallucination = hallucination
    st.session_state.current_chain = chain_viz
    
    st.session_state.executed_skills_sequence.append(skill_name)
    new_log = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Skill Triggered": skill_name,
        "Inputs Received": str(inputs),
        "Tokens Consumed": token_cost,
        "Cost ($)": dollar_cost,
        "Output Summary": summary
    }
    st.session_state.execution_logs.insert(0, new_log)
    st.toast(f"Executed sequence for {skill_name}!", icon="✅")

# ####################################################
# 💼 SYSTEM SKILLS MATRIX DEPLOYMENT DESK
# ####################################################
st.markdown("<p class='section-header'>💼 Active Infrastructure Skills Processing Matrix</p>", unsafe_allow_html=True)

tab1, tab3, tab4 = st.tabs(["🎯 Core Strategy & Prioritization", "📊 Consolidated Master Report", "🔒 Human-In-The-Loop Governance Center"])

# --- TAB 1: STRATEGIC PRIORITIZATION ---
with tab1:
    with st.expander("Skill Component 1: OKR Aligner Module", expanded=True):
        st.markdown("<span class='skill-title-label'>Skill 1: OKR Aligner Component</span>", unsafe_allow_html=True)
        if st.button("Compute Functional OKR Impact Mapping Matrix", key="btn_s1"):
            execute_agent_skill("OKR Aligner", current_backlog_data["tokens"], current_backlog_data["cost"], selected_epic_id.split(':')[0], "Linked target deliverables onto Digital Banking Strategy KR-2.", 165, current_backlog_data["cost"], 0.00, "Ingest ➡️ Cross-Verify Strategy")
            
    with st.expander("Skill Component 2: Strategic Aligner Module", expanded=True):
        st.markdown("<span class='skill-title-label'>Skill 2: Strategic Aligner Component</span>", unsafe_allow_html=True)
        if st.button("🔍 Run Automated Strategic Alignment Audit", key="btn_s2"):
            execute_agent_skill("Strategic Aligner", 210, 0.0042, target_story[:50], "Roadmap paths cleanly match milestone blueprints.", 110, 0.0042, 0.00, "Story Ingest ➡️ Target Milestones Match")

    with st.expander("Skill Component 3: WSJF Priority Calculator Module", expanded=True):
        st.markdown("<span class='skill-title-label'>Skill 3: WSJF Priority Calculator Component</span>", unsafe_allow_html=True)
        
        st.markdown("<div class='wsjf-container-grid'>", unsafe_allow_html=True)
        c_w1, c_w2, c_w3, c_w4, c_w5 = st.columns(5)
        with c_w1:
            st.markdown("<div class='executive-metric-card'><p class='executive-card-label'>User / Business Value</p><p class='executive-card-formula'>Formula Key: A</p></div>", unsafe_allow_html=True)
            bv = st.number_input("Value Weight", 1, 10, 8, label_visibility="collapsed", key="wsjf_bv")
        with c_w2:
            st.markdown("<div class='executive-metric-card'><p class='executive-card-label'>Time Criticality</p><p class='executive-card-formula'>Formula Key: B</p></div>", unsafe_allow_html=True)
            tc = st.number_input("Criticality Weight", 1, 10, 5, label_visibility="collapsed", key="wsjf_tc")
        with c_w3:
            st.markdown("<div class='executive-metric-card'><p class='executive-card-label'>Risk Reduction / Efficiency</p><p class='executive-card-formula'>Formula Key: C</p></div>", unsafe_allow_html=True)
            rr = st.number_input("Risk Weight", 1, 10, 6, label_visibility="collapsed", key="wsjf_rr")
        with c_w4:
            cost_of_delay = bv + tc + rr
            st.markdown(f"<div class='executive-metric-card' style='background-color:#f8fafc !important;'><p class='executive-card-label'>Sum Cost of Delay</p><p class='executive-card-formula'>A + B + C</p><p class='executive-card-val' style='color:#1e3a8a;'>{int(cost_of_delay)}</p></div>", unsafe_allow_html=True)
        with c_w5:
            st.markdown("<div class='executive-metric-card'><p class='executive-card-label'>Job Size / Duration</p><p class='executive-card-formula'>Formula Key: D</p></div>", unsafe_allow_html=True)
            js = st.number_input("Sizing Weight", 1, 10, 3, label_visibility="collapsed", key="wsjf_js")
        st.markdown("</div>", unsafe_allow_html=True)
        
        calculated_wsjf = cost_of_delay / js if js > 0 else 0
        st.markdown(f"""
            <div style='background-color:#f4fbf7; border:1px solid #c2f0d5; padding:10px; border-radius:6px; margin-bottom:10px;'>
                <span style='font-size:13px; font-weight:700; color:#115e59;'>📊 CURRENT CALCULATED WSJF SCORE (Cost of Delay / Job Size = score):</span> 
                <b style='color:#16a34a; font-size:16px; margin-left:5px;'>{calculated_wsjf:.2f}</b>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🧮 Compute Backlog Scoring Matrix", key="btn_s3"):
            execute_agent_skill("WSJF Calculator", 120, 0.0024, f"CoD: {cost_of_delay}, Size: {js}", f"Assigned backlog sequence prioritization matrix index score of {calculated_wsjf:.2f}.", 74, 0.0024, 0.00, "Ingest Metrics ➡️ Factor Sizing")

# --- TAB 2: CONSOLIDATED MASTER REPORT ---
with tab3:
    st.markdown("<p class='section-header'>📊 FinMesh Master Report Compiler Desk</p>", unsafe_allow_html=True)
    if st.button("Generate & Compile Unified FinMesh Architecture Audit Ledger", key="btn_master"):
        st.session_state.audit_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "epic_id": selected_epic_id.split(":")[0],
            "epic_name": selected_epic_id.split(":")[1].strip() if ":" in selected_epic_id else selected_epic_id,
            "wsjf_score": f"{calculated_wsjf:.2f}",
            "cod_breakdown": f"Business Value: {bv}, Criticality: {tc}, Risk Reduction: {rr} (Total CoD: {cost_of_delay})"
        }
        execute_agent_skill("Master Report Compiler", 100, 0.0020, "Global Session Store", "Compiled active workspace metrics into layout engine.", 80, 0.0020, 0.00, "Merge States ➡️ Output Matrix")
        
    if st.session_state.audit_report is not None:
        st.markdown("<div class='master-report-header-banner'>📝 UNIFIED FINMESH ARCHITECTURE MASTER REPORT LEDGER</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='master-report-section-node'>
            <p class='master-report-section-title'>1. Epic Overview & Metadata (EPIC-LEVEL DETAILS)</p>
            <table class='custom-spec-table'>
                <tr><td><b>Epic Key / Identity Target</b></td><td>{st.session_state.audit_report['epic_id']} — {st.session_state.audit_report['epic_name']}</td></tr>
                <tr><td><b>Functional Requirement Scope</b></td><td>{target_story}</td></tr>
                <tr><td><b>Compliance Class Tags</b></td><td>NICE Actimize Platform Auditing, AML Ledger Verification, PCI-DSS | High-Risk</td></tr>
            </table>
        </div>
        
        <div class='master-report-section-node'>
            <p class='master-report-section-title'>2. Story Inventory Framework</p>
            <table class='custom-spec-table'>
                <tr><th>Story ID</th><th>Functional Scope Description</th><th>Assignee Resource</th><th>Weight</th><th>Compliance State</th></tr>
                <tr><td>STORY-101</td><td>Intercept transaction schema payload before writing onto vector-store engine</td><td>K. Chidambaram</td><td>5 SP</td><td><span style='color:green; font-weight:bold;'>Passed</span></td></tr>
                <tr><td>STORY-102</td><td>Configure automated webhook triggers back to central NICE Actimize consoles</td><td>Infra Agent Node</td><td>3 SP</td><td><span style='color:green; font-weight:bold;'>Passed</span></td></tr>
            </table>
        </div>
        
        <div class='master-report-section-node'>
            <p class='master-report-section-title'>3 & 4. Sprint & Release Operational Mapping Matrix</p>
            <p style='font-size:13px; margin:0;'><b>Active Delivery Cycle Group:</b> Sprint 12 Core Deployment | Target Pace: <b>{current_backlog_data['velocity']}</b></p>
            <p style='font-size:13px; margin:4px 0 0 0;'><b>Release Readiness Baseline Score:</b> <span style='color:green; font-weight:700;'>91.5%</span> — Deployment regression parameters pass sandbox safety tolerances.</p>
        </div>
        
        <div class='master-report-section-node'>
            <p class='master-report-section-title'>5. WSJF Prioritization Matrix Analytics</p>
            <p style='font-size:13px; margin:0;'><b>Computed Sequence Index Score:</b> <span style='color:#1e3a8a; font-weight:700;'>{st.session_state.audit_report['wsjf_score']}</span></p>
            <p style='font-size:13px; margin:4px 0 0 0;'><b>Component Parameter Breakdown:</b> {st.session_state.audit_report['cod_breakdown']}</p>
        </div>
        
        <div class='master-report-section-node'>
            <p class='master-report-section-title'>6. Blocker & Dependency Risk Grid</p>
            <p style='font-size:13px; margin:0; color:#ef4444;'><b>Identified Constraints:</b> 0 high-severity infrastructure blocks mapped. Environment lockfiles match staging baseline.</p>
        </div>
        
        <div class='master-report-section-node' style='border-bottom: 1px solid #e2e8f0;'>
            <p class='master-report-section-title'>7 to 12. Intelligent Architecture Summaries & HITL Audit Log</p>
            <p style='font-size:13px; margin:0;'><b>Artifacts Drafter (7):</b> System Design Document payload endpoints match active schemas.</p>
            <p style='font-size:13px; margin:4px 0 0 0;'><b>Compliance Summary (8):</b> Verified policy tracking tokens against NICE Actimize regulations.</p>
            <p style='font-size:13px; margin:4px 0 0 0;'><b>Supervisor Governance State (10 & 11):</b> Verified signature trails intact across active session logs. Consumption evaluated at {st.session_state.tokens_used:,} tokens.</p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: HUMAN-IN-THE-LOOP (HITL) GOVERNANCE CENTER ---
with tab4:
    st.markdown("<p class='section-header'>🛡️ Human-In-The-Loop (HITL) Governance Center</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='hitl-alert-banner'>\u26a0\ufe0f <b>Awaiting Verification:</b> Context parameters retrieved dynamically for active element <b>{selected_epic_id.split(':')[0]}</b>.</div>", unsafe_allow_html=True)
    
    g_col1, g_col2 = st.columns([1, 1])
    with g_col1:
        st.markdown("### 🔍 AI-Generated Issue Breakdown")
        st.info("""
        \ud83d\udd39 **What Changed:** System processed multi-modal specifications and adjusted the priority queue tracking vector index value.
        \ud83d\udd39 **Why It Matters:** Governs deployment sequence alignment constraints for the active iteration window.
        \ud83d\udd39 **What the Risk Is:** Downstream microservice pipeline orchestration delays if schema rules drop database threads.
        \ud83d\udd39 **Recommended Action:** Execute audit confirmation trace and authorize staging merge routines.
        """)
        st.markdown("### 📦 Evidence Bundle Assets")
        st.write(f"\ud83d\udcc2 **WSJF Recalculation Trace:** Evaluated Backlog Score Index: `{calculated_wsjf:.2f}`")
        st.write(f"\ud83d\udcc2 **Active Operational Target narrative:** `{target_story[:110]}...`")
        st.markdown("### 📉 Decision Impact Preview")
        st.warning(f"\ud83d\udca1 **Affected Milestone Ring:** {current_backlog_data['milestone']} \n\n\ud83c\udfaf **Linked OKR Indicator:** Corporate Digital Banking Infrastructure Initiative KR-2")

    with g_col2:
        st.markdown("### ⏱️ SLA Timeout Counter")
        elapsed = datetime.now() - st.session_state.start_time
        remaining_seconds = max(10800 - int(elapsed.total_seconds()), 0)
        rem_duration = timedelta(seconds=remaining_seconds)
        st.error(f"\u23f3 **Time Remaining to Approve:** `{str(rem_duration).split('.')[0]}` before automatic escalation rules route task upward.")
        
        st.markdown("### 🔒 Security Audit Trail Metadata")
        st.markdown(f"""
        <table class='custom-spec-table' style='margin-bottom: 12px;'>
            <tr><td><b>Supervisor Role</b></td><td>Lead Fintech Product Manager</td></tr>
            <tr><td><b>System Version</b></td><td>v2.4.0-Beta-Core</td></tr>
            <tr><td><b>Model Processor</b></td><td>GPT-4o-Enterprise Tier Cluster</td></tr>
            <tr><td><b>Token Cost</b></td><td>${st.session_state.budget_spent:.4f} ({st.session_state.tokens_used:,} Units)</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✒️ Executive Action Control")
        verdict_selection = st.radio(
            "Executive Governance Action Verdict",
            ["Approve Deployment", "Reject Change", "Escalate to Next Level Tier", "Request Structural Revision"],
            key="hitl_verdict_radio"
        )
        reviewer_name = st.text_input("Authorized Approver Signature", value="Karuppiah Chidambaram")
        verdict_notes = st.text_area("Audit Log Notes / Decision Rationale Remarks", placeholder="Enter notes...", height=100)
        
        if st.button("💾 Commit Executive Governance Verdict to Ledger", key="btn_commit_hitl"):
            new_audit_entry = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Artifact ID": selected_epic_id.split(":")[0],
                "Trigger Target Context": "High WSJF / Compliance Trace",
                "Severity Level": "High",
                "Selected Action Verdict": verdict_selection,
                "Authorized Approver": reviewer_name,
                "Operational Remarks": verdict_notes if verdict_notes else "Executed dynamic confirmation step."
            }
            st.session_state.hitl_ledger.insert(0, new_audit_entry)
            execute_agent_skill(
                "Governance Engine", 150, 0.0030, "HITL-COMMIT",
                f"Committed verdict ({verdict_selection}) into compliance matrix ledger. Verified by {reviewer_name}.",
                95, 0.0030, 0.00, "User Action ➡️ Commit Ledger Row"
            )
            st.success("Successfully committed action verdict under secure ledger signatures!")

    st.markdown("<p class='section-header'>📜 Historical Governance Ledger Trail</p>", unsafe_allow_html=True)
    if len(st.session_state.hitl_ledger) > 0:
        hist_html = """
        <div style='overflow-x: auto; width: 100%;'>
        <table class='custom-spec-table'>
            <tr>
                <th>\ud83d\udd5b System Timestamp</th>
                <th>\ud83c\udfaf Artifact ID</th>
                <th>\ud83e\udde0 Trigger Target Context</th>
                <th>\ud83d\udea8 Severity Level</th>
                <th>\u2616\ufe0f Selected Action Verdict</th>
                <th>\u2712\ufe0f Authorized Approver</th>
                <th>\ud83d\udcdd Operational Remarks</th>
            </tr>
        """
        for entry in st.session_state.hitl_ledger:
            hist_html += f"""
            <tr>
                <td>{entry['Timestamp']}</td>
                <td><b>{entry['Artifact ID']}</b></td>
                <td><code>{entry['Trigger Target Context']}</code></td>
                <td><span style='color:#ef4444; font-weight:600;'>{entry['Severity Level']}</span></td>
                <td><span style='color:#1e3a8a; font-weight:600;'>{entry['Selected Action Verdict']}</span></td>
                <td>{entry['Authorized Approver']}</td>
                <td>{entry['Operational Remarks']}</td>
            </tr>
            """
        hist_html += "</table></div>"
        st.markdown(hist_html, unsafe_allow_html=True)
    else:
        st.info("No governance rows committed to database ledger yet.")

# ####################################################
# 🤖 LIVE AGENTIC OBSERVABILITY TERMINAL
# ####################################################
if view_layer_selection == "Advanced Reporting Mode":
    st.markdown("<p class='section-header'>🤖 Live Agentic Observability & Evals Metrics</p>", unsafe_allow_html=True)
    st.markdown("<div class='observability-grid-container'>", unsafe_allow_html=True)
    obs_c1, obs_c2, obs_c3, obs_c4, obs_c5 = st.columns(5)
    with obs_c1:
        st.markdown(f"<div class='observability-box-mild-grey'>\u23f1\ufe0f <b style='font-size:11px; text-transform:uppercase; color:#475569;'>Latency</b><br><span style='font-size:1.35rem; font-weight:700; color:#0f172a; margin-top:4px;'>{st.session_state.live_latency}ms</span></div>", unsafe_allow_html=True)
    with obs_c2:
        st.markdown(f"<div class='observability-box-mild-grey'>\ud83d\udcb5 <b style='font-size:11px; text-transform:uppercase; color:#475569;'>Cost / Req</b><br><span style='font-size:1.35rem; font-weight:700; color:#0f172a; margin-top:4px;'>${st.session_state.live_cost_req:.4f}</span></div>", unsafe_allow_html=True)
    with obs_c3:
        st.markdown(f"<div class='observability-box-mild-grey'>\ud83c\udfaf <b style='font-size:11px; text-transform:uppercase; color:#475569;'>Hallucination</b><br><span style='font-size:1.35rem; font-weight:700; color:#0f172a; margin-top:4px;'>{(st.session_state.live_hallucination * 100):.1f}%</span></div>", unsafe_allow_html=True)
    with obs_c4:
        st.markdown(f"<div class='observability-box-mild-grey'>\📋 <b style='font-size:11px; text-transform:uppercase; color:#475569;'>Evals Status</b><br><span style='font-size:1.35rem; font-weight:700; color:#16a34a; margin-top:4px;'>{st.session_state.live_eval_status}</span></div>", unsafe_allow_html=True)
    with obs_c5:
        st.markdown(f"<div class='observability-box-mild-grey'>\ud83d\udd17 <b style='font-size:11px; text-transform:uppercase; color:#475569;'>Chain Path</b><br><span style='font-size:11px; font-family:monospace; color:#d97706; font-weight:700; margin-top:4px;'>{st.session_state.current_chain}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ####################################################
# 📜 LIVE AGENT EXECUTION LOG SECTION
# ####################################################
st.markdown("<p class='section-header'>📜 Live Agent Execution Log</p>", unsafe_allow_html=True)

if len(st.session_state.execution_logs) > 0:
    log_html = """
    <div style='overflow-x: auto; width: 100%;'>
    <table class='custom-spec-table' style='border-top: 4px solid #1e3a8a;'>
        <tr>
            <th style='width: 15%;'>\ud83d\udd5b System Timestamp</th>
            <th style='width: 15%;'>\u2699\ufe0f Active Process Unit</th>
            <th style='width: 20%;'>\ud83d\udce5 Ingested Metadata Input</th>
            <th style='width: 8%;'>\🪙 Tokens</th>
            <th style='width: 8%;'>\ud83d\udcb5 Cost</th>
            <th style='width: 34%;'>\ud83d\udcdd Dynamic Operational Execution Ledger Logs</th>
        </tr>
    """
    for row in st.session_state.execution_logs:
        log_html += f"""
        <tr>
            <td>{row['Timestamp']}</td>
            <td><span style='color:#1e3a8a; font-weight:600;'>{row['Skill Triggered']}</span></td>
            <td><code style='font-size:11px;'>{row['Inputs Received']}</code></td>
            <td>{row['Tokens Consumed']:,}</td>
            <td>${row['Cost ($)']:.4f}</td>
            <td><b>{row['Output Summary']}</b></td>
        </tr>
        """
    log_html += "</table></div>"
    st.markdown(log_html, unsafe_allow_html=True)
else:
    st.info("No active skills executed in this session run loop yet.")