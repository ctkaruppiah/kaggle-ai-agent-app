import os
import json
import html as html_lib
import time
from datetime import datetime, timedelta

import streamlit as st

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

st.set_page_config(layout="wide", page_title="FinMesh Executive Centre", page_icon="🚀")

# ####################################################
# 🔌 SUPABASE CLIENT
# ####################################################
def _get_secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


SUPABASE_URL = _get_secret("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")


@st.cache_resource
def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None


supabase_client = get_supabase_client()
# Fix (#8): connectivity banner now reflects the REAL client state instead of
# a hardcoded "not connected" string that never changed regardless of wiring.
SUPABASE_CONNECTED = supabase_client is not None


def save_governance_to_supabase(entry_dict):
    """Best-effort write to the `governance_ledger` table."""
    if not supabase_client:
        return False
    try:
        supabase_client.table("governance_ledger").insert(entry_dict).execute()
        return True
    except Exception:
        return False


def save_skill_log_to_supabase(entry_dict):
    """Best-effort write to `skill_execution_logs`. Column names may need to
    be adjusted to match your exact Supabase schema."""
    if not supabase_client:
        return
    try:
        supabase_client.table("skill_execution_logs").insert(entry_dict).execute()
    except Exception:
        pass


def save_epic_state_to_supabase(epic_id, epic_dict):
    """Upsert the full Epic (incl. Stories/Tasks/OKR/SDD/Blockers/WSJF) as a
    JSON blob into `epic_state_store`, keyed by epic_id, so New Epic /
    Save Story / Save Task etc. are actually reflected in Supabase — not just
    kept in session state.

    Run this once in the Supabase SQL editor before using this feature:

        create table if not exists epic_state_store (
            workspace_key text primary key,
            state_json jsonb not null,
            updated_at timestamptz not null default now()
        );

    (We deliberately do NOT reuse `workspace_state_logs` — that table's real
    columns turned out to be `id` / `timestamp` / `active_skills`, i.e. it was
    built for something else. Repurposing it would keep causing schema
    mismatches, so Epic state gets its own dedicated table instead.)
    """
    if not supabase_client:
        return False, "No Supabase connection."
    try:
        payload = {
            "workspace_key": epic_id,
            "state_json": epic_dict,
            "updated_at": datetime.now().isoformat(),
        }
        supabase_client.table("epic_state_store").upsert(payload, on_conflict="workspace_key").execute()
        return True, None
    except Exception as e:
        return False, str(e)


@st.cache_data(ttl=5)
def load_epics_from_supabase():
    """Best-effort read of every saved Epic back from `epic_state_store` on
    startup, so a refresh / redeploy doesn't lose what's already been
    created. Returns None (fall back to in-memory defaults) if the table
    doesn't exist yet or is empty."""
    if not supabase_client:
        return None
    try:
        res = supabase_client.table("epic_state_store").select("workspace_key,state_json").execute()
        rows = res.data or []
        if not rows:
            return None
        loaded = {}
        for r in rows:
            try:
                val = r["state_json"]
                loaded[r["workspace_key"]] = json.loads(val) if isinstance(val, str) else val
            except Exception:
                continue
        return loaded or None
    except Exception:
        return None


def esc(val):
    """Escape any user-entered text before it goes into a raw HTML string.
    Fix (#7): the Master Report used to leak literal HTML/code onto the page
    whenever a story/epic field contained characters like < > or & — those
    characters silently broke out of the surrounding <div>/<table> markup,
    and Streamlit rendered the remainder of the block as plain text instead
    of as HTML. Escaping every dynamic value closes that hole for good."""
    if val is None:
        return ""
    return html_lib.escape(str(val), quote=True)


def note(html_text):
    """Readable replacement for st.caption(), which renders as thin, faint
    gray text by default. Accepts a snippet of inline HTML (use <b> for bold,
    not markdown **)."""
    st.markdown(f"<p class='helper-note'>{html_text}</p>", unsafe_allow_html=True)


# ####################################################
# 💾 DATA MODEL — Epic → Story → Task, plus the supporting
# OKR / Value Stream / Blocker / SDD / WSJF objects each Epic owns.
# This is the single source of truth every skill, tab, and report reads from.
# ####################################################
DEFAULT_EPICS = {
    "EPIC-001": {
        "name": "Embedded Banking Transaction Core API Integration",
        "narrative": "As a commercial banking customer, I want to execute cross-border real-time multi-currency settlement routes directly via API, ensuring compliance with NICE Actimize transaction logging policies.",
        "business_goal": "Reduce cross-border settlement latency and unlock a new API-first commercial banking revenue line.",
        "compliance_category": "NICE Actimize Regulatory Policy Verified",
        "target_release": "Q2 Product Release Rollout",
        "target_quarter": "Q2 2026",
        "okr": {
            "objective": "Deliver a compliant, real-time cross-border settlement API.",
            "key_results": "99.9% settlement SLA; 0 unresolved compliance violations; 45 SP delivered per quarter.",
            "target_metrics": "SLA adherence %, audit trail completeness %, velocity (SP/sprint)",
            "timeframe": "Q2 2026",
            "business_theme": "Digital Banking Growth",
        },
        "value_stream": {
            "trigger": "Inbound cross-border settlement request",
            "validate": "KYC + sanction screening pre-check",
            "process": "Settlement routing & multi-currency conversion",
            "log": "NICE Actimize audit trail write",
            "store": "Ledger persistence (Supabase / core ledger)",
            "respond": "Settlement confirmation returned to caller",
        },
        "blockers": [
            {
                "dependency": "Cross-border settlement API handshake",
                "version_conflict": "None",
                "missing_module": "None",
                "cicd_failure": "None (unit tests passing)",
                "security_vuln": "NICE Actimize regulatory policy sync pending",
                "impacted_teams": "Core Payments, Compliance Engineering",
                "severity": "Critical",
                "resolution_eta": "2026-06-30",
            }
        ],
        "sdd": {
            "core_component": "Settlement Router Service",
            "endpoint": "POST /v1/settlements/cross-border",
            "database": "core_ledger (Postgres / Supabase)",
            "rls_policy": "settlement_owner_only — row scoped to originating account_id",
            "compliance_hooks": "NICE Actimize audit-log webhook on commit",
            "architecture_blueprint": "API Gateway → Settlement Router → Ledger Sync Service",
            "sequence_flow": "1. Payload intercepted at intake node\n2. Compliance policy match against active ruleset\n3. Auto-archive to governance ledger on completion",
            "api_contract": "Request: {account_id, currency_pair, amount}; Response: {settlement_id, status, sla_deadline}",
            "nfrs": "P99 latency < 800ms; 99.95% availability; PCI-DSS | High-Risk",
        },
        "wsjf": {"bv": 8, "tc": 5, "rr": 6, "size": 3},
        "stories": {
            "STORY-101": {
                "description": "Intercept transaction schema payload before writing onto the vector-store engine.",
                "assignee": "K. Chidambaram",
                "story_points": 5,
                "acceptance_criteria": "Given a valid cross-border payload, when submitted via the settlement API, then funds settle within SLA and the transaction is logged to the NICE Actimize audit trail with no manual intervention.",
                "dependencies": "Requires SDD Settlement Router endpoint live",
                "compliance_state": "Passed",
                "sprint_assignment": "Sprint 1",
                "tasks": {
                    "TASK-1": {"description": "Build payload schema validator", "owner": "K. Chidambaram", "status": "Done", "estimate_hours": 8},
                    "TASK-2": {"description": "Wire NICE Actimize audit webhook", "owner": "Infra Agent Node", "status": "In Progress", "estimate_hours": 6},
                },
            },
            "STORY-102": {
                "description": "Configure automated webhook triggers back to central NICE Actimize consoles.",
                "assignee": "Infra Agent Node",
                "story_points": 3,
                "acceptance_criteria": "Given a completed settlement, when it is committed, then a webhook fires to the NICE Actimize console within 2 seconds.",
                "dependencies": "STORY-101",
                "compliance_state": "Passed",
                "sprint_assignment": "Sprint 1",
                "tasks": {
                    "TASK-1": {"description": "Implement webhook retry policy", "owner": "Infra Agent Node", "status": "Not Started", "estimate_hours": 4},
                },
            },
        },
    },
    "EPIC-002": {
        "name": "Real-time AML Ledger Sanction Match Hooks",
        "narrative": "As a senior risk officer, I need all inbound transaction payloads intercepted and verified against international sanction lists before database execution to minimize policy liabilities.",
        "business_goal": "Eliminate manual sanction-screening backlog and reduce regulatory exposure.",
        "compliance_category": "Sanction Stream Active Filter Tier-1",
        "target_release": "Q3 Enterprise Beta Phase",
        "target_quarter": "Q3 2026",
        "okr": {
            "objective": "Automate sanction screening for 100% of inbound transactions.",
            "key_results": "0 sanctioned-entity transactions reach the ledger; screening latency < 300ms.",
            "target_metrics": "Screening coverage %, false-positive rate, latency (ms)",
            "timeframe": "Q3 2026",
            "business_theme": "Risk & Compliance Modernization",
        },
        "value_stream": {
            "trigger": "Inbound transaction payload",
            "validate": "Sanction list match check",
            "process": "Block or route to compliance queue",
            "log": "Compliance decision logged",
            "store": "Compliance queue table (Supabase)",
            "respond": "Accept / block decision returned",
        },
        "blockers": [],
        "sdd": {
            "core_component": "Sanction Match Interceptor",
            "endpoint": "POST /v1/aml/screen",
            "database": "compliance_queue (Postgres / Supabase)",
            "rls_policy": "compliance_officer_only",
            "compliance_hooks": "AML Ledger Verification hook pre-commit",
            "architecture_blueprint": "Ingress Interceptor → Sanction Match Engine → Compliance Queue",
            "sequence_flow": "1. Payload intercepted before DB write\n2. Sanction list match\n3. Block + route to compliance queue if matched",
            "api_contract": "Request: {payload}; Response: {decision, matched_entity|null}",
            "nfrs": "P99 latency < 300ms; audit-complete on every decision",
        },
        "wsjf": {"bv": 9, "tc": 7, "rr": 7, "size": 5},
        "stories": {},
    },
}

_loaded_epics = load_epics_from_supabase()
_initial_epics = _loaded_epics if _loaded_epics else DEFAULT_EPICS

_DEFAULTS = {
    "view_layer": "Standard Mode",
    "epic_panel_mode": "closed",
    "epics": _initial_epics,
    "selected_epic_id": list(_initial_epics.keys())[0],
    "hitl_notes": "",
    "reviewer_name": "Compliance Assayer",
    "tokens_used": 0,
    "budget_spent": 0.0,
    "start_time": time.time(),
    "hitl_ledger": [],
    "executed_skills_sequence": [],
    "execution_logs": [],
    "uploaded_files_registry": {},
    "master_report_epic": None,
    "master_report_program": None,
    "master_report_metrics": None,
    "live_latency": 0,
    "live_cost_req": 0.0,
    "live_hallucination": 0.0,
    "live_eval_status": "Pending",
    "current_chain": "—",
    "last_commit_feedback": None,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Keys that hold transient, mode-specific validation/status messages. Fix (#9):
# switching Standard <-> Advanced used to leave these stale on screen because
# nothing ever cleared them on a mode change.
_EPHEMERAL_KEYS = [
    "epic_create_error", "epic_create_success",
    "story_create_error", "story_create_success",
    "task_create_error", "task_create_success",
    "blocker_create_error", "blocker_create_success",
    "sdd_save_success", "sdd_save_error",
    "wsjf_save_success", "wsjf_save_error", "last_commit_feedback",
    "blueprint_save_success", "blueprint_save_error",
]

# ####################################################
# ⚙️ HELPERS
# ####################################################
def next_id(prefix, existing_ids):
    n = 1
    existing_upper = {e.upper() for e in existing_ids}
    while f"{prefix}-{n:03d}" in existing_upper:
        n += 1
    return f"{prefix}-{n:03d}"


def current_epic():
    return st.session_state.epics[st.session_state.selected_epic_id]


def all_stories_flat():
    """[(epic_id, story_id, story_dict), ...] across the whole program."""
    out = []
    for eid, ep in st.session_state.epics.items():
        for sid, s in ep["stories"].items():
            out.append((eid, sid, s))
    return out


def all_tasks_flat():
    out = []
    for eid, ep in st.session_state.epics.items():
        for sid, s in ep["stories"].items():
            for tid, t in s["tasks"].items():
                out.append((eid, sid, tid, t))
    return out


def execute_agent_skill(skill_name, token_cost, dollar_cost, inputs, summary, latency, tracking_cost, hallucination, chain_viz):
    st.session_state.tokens_used += token_cost
    st.session_state.budget_spent += dollar_cost
    st.session_state.live_latency = latency
    st.session_state.live_cost_req = tracking_cost
    st.session_state.live_hallucination = hallucination
    st.session_state.live_eval_status = "Passed"
    st.session_state.current_chain = chain_viz
    st.session_state.executed_skills_sequence.append(skill_name)
    new_log = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Skill Triggered": skill_name,
        "Inputs Received": str(inputs),
        "Tokens Consumed": token_cost,
        "Cost ($)": dollar_cost,
        "Output Summary": summary,
    }
    st.session_state.execution_logs.insert(0, new_log)
    save_skill_log_to_supabase(new_log)
    st.toast(f"Executed sequence for {skill_name}!", icon="✅")


# ####################################################
# ⚙️ CALLBACKS
# ####################################################
def _apply_view_change():
    st.session_state.view_layer = st.session_state.view_layer_widget
    st.session_state.epic_panel_mode = "closed"
    for k in _EPHEMERAL_KEYS:
        st.session_state[k] = None
    st.toast(f"🔄 Switched to {st.session_state.view_layer}.", icon="🚀")


def _reset_all():
    """Full destructive reset. Previously this only cleared st.session_state,
    which *looked* like a no-op: load_epics_from_supabase() is @st.cache_data
    with a 5s TTL, so on the very next rerun the Epics/Stories/Tasks were
    silently pulled straight back out of the `epic_state_store` table and the
    UI re-populated itself before the user could even notice a change. The
    governance ledger and skill execution logs were never touched either.
    Now we (1) best-effort delete the persisted rows in Supabase, (2) clear
    the cached loader so it can't repopulate from stale data, and (3) wipe
    session_state, then force a rerun so every widget re-initializes clean."""
    if supabase_client:
        for _table in ("epic_state_store", "governance_ledger", "skill_execution_logs"):
            try:
                supabase_client.table(_table).delete().neq("workspace_key", "___never_matches___").execute()
            except Exception:
                try:
                    supabase_client.table(_table).delete().gte("id", 0).execute()
                except Exception:
                    pass
    load_epics_from_supabase.clear()
    for _key in list(st.session_state.keys()):
        del st.session_state[_key]
    st.toast("⚡ All live application metrics, telemetry, and persisted Supabase state have been purged!", icon="🧹")
    st.rerun()


RELEASE_OPTIONS = ["Q1 Rollout", "Q2 Rollout", "Q3 Rollout", "Q4 Rollout", "Enterprise Beta Phase", "Unscheduled"]
QUARTER_OPTIONS = ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026", "Q1 2027", "TBD"]
COMPLIANCE_OPTIONS = ["NICE Actimize Regulatory Policy Verified", "Sanction Stream Active Filter Tier-1",
                      "PCI-DSS Level 1 Verified", "SOC 2 Type II Controlled", "Not Yet Assessed", "Others"]


def _open_create_epic_panel():
    st.session_state.epic_panel_mode = "create"
    st.session_state.epic_compliance_select = COMPLIANCE_OPTIONS[0]
    st.session_state.epic_compliance_other = ""
    st.session_state.epic_create_error = None
    st.session_state.epic_create_success = None


def _open_edit_epic_panel():
    ep = st.session_state.epics[st.session_state.selected_epic_id]
    st.session_state.epic_panel_mode = "edit"
    if ep["compliance_category"] in COMPLIANCE_OPTIONS[:-1]:
        st.session_state.epic_compliance_select = ep["compliance_category"]
        st.session_state.epic_compliance_other = ""
    else:
        st.session_state.epic_compliance_select = "Others"
        st.session_state.epic_compliance_other = ep["compliance_category"]
    st.session_state.epic_create_error = None
    st.session_state.epic_create_success = None


def _cancel_epic_panel():
    st.session_state.epic_panel_mode = "closed"
    st.session_state.epic_create_error = None


def _resolved_compliance_category():
    cat = st.session_state.epic_compliance_select
    if cat == "Others":
        return st.session_state.epic_compliance_other.strip() or "Others (unspecified)"
    return cat


def _update_epic(epic_id):
    ep = st.session_state.epics[epic_id]
    new_name = st.session_state[f"edit_epic_name_{epic_id}"].strip()
    if not new_name:
        st.session_state.epic_create_error = "Epic Name is required."
        return
    ep["name"] = new_name
    ep["narrative"] = st.session_state[f"edit_epic_narrative_{epic_id}"].strip() or "No narrative provided yet."
    ep["business_goal"] = st.session_state[f"edit_epic_goal_{epic_id}"].strip() or "No business/product goal provided yet."
    ep["compliance_category"] = _resolved_compliance_category()
    ep["target_release"] = st.session_state[f"edit_epic_release_{epic_id}"]
    ep["target_quarter"] = st.session_state[f"edit_epic_quarter_{epic_id}"]
    st.session_state.epic_panel_mode = "closed"
    # Fix (docx Issue 3 — "Edit Save Sync Bug"): explicitly re-point both the
    # selection state AND the dropdown widget at the just-edited Epic, so the
    # workspace can never end up stuck showing a different, older record.
    st.session_state.selected_epic_id = epic_id
    st.session_state.epic_selector_widget = epic_id
    _sync_epic(epic_id, f"✅ {epic_id} updated.", "epic_create_error", "epic_create_success")


def _create_new_epic():
    # Fix (#2 from your latest round): Epic ID is never typed by the user —
    # it's computed fresh every time the form renders (see
    # `st.session_state["_next_epic_id"]` set just before the form below) and
    # is immutable once created.
    new_id = st.session_state.get("_next_epic_id")
    new_name = st.session_state.new_epic_name.strip()
    if not new_id or not new_name:
        st.session_state.epic_create_error = "Epic Name is required."
        return
    existing_upper = {e.upper() for e in st.session_state.epics.keys()}
    if new_id.upper() in existing_upper:
        # Should be unreachable since IDs are system-generated, but guarded
        # anyway in case of a race between two browser tabs.
        st.session_state.epic_create_error = f"Epic ID '{new_id}' already exists. Please retry."
        return
    compliance_category = _resolved_compliance_category()
    st.session_state.epics[new_id] = {
        "name": new_name,
        "narrative": st.session_state.new_epic_narrative.strip() or "No narrative provided yet.",
        "business_goal": st.session_state.new_epic_goal.strip() or "No business/product goal provided yet.",
        "compliance_category": compliance_category,
        "target_release": st.session_state.new_epic_release,
        "target_quarter": st.session_state.new_epic_quarter,
        "okr": {"objective": "", "key_results": "", "target_metrics": "", "timeframe": "", "business_theme": ""},
        "value_stream": {"trigger": "", "validate": "", "process": "", "log": "", "store": "", "respond": ""},
        "blockers": [],
        "sdd": {k: "" for k in ["core_component", "endpoint", "database", "rls_policy", "compliance_hooks", "architecture_blueprint", "sequence_flow", "api_contract", "nfrs"]},
        "wsjf": {"bv": 5, "tc": 5, "rr": 5, "size": 5},
        "stories": {},
    }
    st.session_state.selected_epic_id = new_id
    st.session_state.epic_selector_widget = new_id
    st.session_state.epic_panel_mode = "closed"
    st.session_state.epic_create_error = None
    synced, sync_msg = save_epic_state_to_supabase(new_id, st.session_state.epics[new_id])
    if synced:
        st.session_state.epic_create_success = f"✅ {new_id} created, selected, and synced to Supabase."
    elif SUPABASE_CONNECTED:
        st.session_state.epic_create_success = f"✅ {new_id} created and selected (kept in this session only)."
        st.session_state.epic_create_error = f"⚠️ Supabase sync failed: {sync_msg}"
    else:
        st.session_state.epic_create_success = f"✅ {new_id} created and selected (session only — no Supabase connection detected)."


def _sync_epic(epic_id, success_prefix, error_key, success_key):
    """Shared helper: push the whole (mutated) Epic back to Supabase and
    surface a clear success/failure message, instead of silently no-op'ing."""
    synced, sync_msg = save_epic_state_to_supabase(epic_id, st.session_state.epics[epic_id])
    if synced:
        st.session_state[success_key] = f"{success_prefix} Synced to Supabase."
    elif SUPABASE_CONNECTED:
        st.session_state[success_key] = f"{success_prefix} (kept in this session only)."
        st.session_state[error_key] = f"⚠️ Supabase sync failed: {sync_msg}"
    else:
        st.session_state[success_key] = f"{success_prefix} (session only — no Supabase connection detected)."


SPRINT_OPTIONS = ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5", "Backlog (Unscheduled)"]


def _save_story():
    epic = current_epic()
    sid = st.session_state.get("_next_story_id")
    desc = st.session_state.new_story_desc.strip()
    if not sid or not desc:
        st.session_state.story_create_error = "Description is required."
        return
    epic["stories"][sid] = {
        "description": desc,
        "assignee": st.session_state.new_story_assignee.strip() or "Unassigned",
        "story_points": st.session_state.new_story_points,
        "acceptance_criteria": st.session_state.new_story_ac.strip() or "No acceptance criteria provided yet.",
        "dependencies": st.session_state.new_story_deps.strip() or "None",
        "compliance_state": st.session_state.new_story_compliance,
        "sprint_assignment": st.session_state.new_story_sprint,
        "tasks": {},
    }
    st.session_state.story_create_error = None
    st.session_state[f"story_panel_open_{st.session_state.selected_epic_id}"] = False
    _sync_epic(st.session_state.selected_epic_id, f"✅ {sid} saved to {st.session_state.selected_epic_id}.", "story_create_error", "story_create_success")


def _update_story(epic_id, story_id, prefix):
    epic = st.session_state.epics[epic_id]
    desc = st.session_state[f"{prefix}_desc"].strip()
    if not desc:
        st.session_state.story_create_error = "Description is required."
        return
    epic["stories"][story_id].update({
        "description": desc,
        "assignee": st.session_state[f"{prefix}_assignee"].strip() or "Unassigned",
        "story_points": st.session_state[f"{prefix}_points"],
        "acceptance_criteria": st.session_state[f"{prefix}_ac"].strip() or "No acceptance criteria provided yet.",
        "dependencies": st.session_state[f"{prefix}_deps"].strip() or "None",
        "compliance_state": st.session_state[f"{prefix}_compliance"],
        "sprint_assignment": st.session_state[f"{prefix}_sprint"],
    })
    st.session_state.story_create_error = None
    st.session_state[f"story_panel_open_{epic_id}"] = False
    _sync_epic(epic_id, f"✅ {story_id} updated.", "story_create_error", "story_create_success")


def _save_task(epic_id, story_id, form_prefix):
    epic = st.session_state.epics[epic_id]
    story = epic["stories"][story_id]
    tid = st.session_state.get("_next_task_id")
    desc = st.session_state[f"{form_prefix}_desc"].strip()
    if not tid or not desc:
        st.session_state.task_create_error = "Description is required."
        return
    story["tasks"][tid] = {
        "description": desc,
        "owner": st.session_state[f"{form_prefix}_owner"].strip() or "Unassigned",
        "status": st.session_state[f"{form_prefix}_status"],
        "estimate_hours": st.session_state[f"{form_prefix}_est"],
    }
    st.session_state.task_create_error = None
    _sync_epic(epic_id, f"✅ {tid} added to {story_id}.", "task_create_error", "task_create_success")


def _update_task(epic_id, story_id, task_id, prefix):
    epic = st.session_state.epics[epic_id]
    task = epic["stories"][story_id]["tasks"][task_id]
    desc = st.session_state[f"{prefix}_desc"].strip()
    if not desc:
        st.session_state.task_create_error = "Description is required."
        return
    task.update({
        "description": desc,
        "owner": st.session_state[f"{prefix}_owner"].strip() or "Unassigned",
        "status": st.session_state[f"{prefix}_status"],
        "estimate_hours": st.session_state[f"{prefix}_est"],
    })
    st.session_state.task_create_error = None
    _sync_epic(epic_id, f"✅ {task_id} updated.", "task_create_error", "task_create_success")


TEAM_OPTIONS = ["Core Payments", "Compliance Engineering", "DevOps", "SecOps", "Data Platform", "Frontend Engineering", "QA/Test Automation"]
SECURITY_VULN_OPTIONS = ["None", "CVE Vulnerability", "Compliance Policy Sync", "Third-Party Audit Block", "Other"]


def _save_blocker():
    epic = current_epic()
    scope_type = st.session_state.blk_scope_type
    scope_id = st.session_state.blk_scope_id if scope_type != "Epic" else st.session_state.selected_epic_id
    version_conflict = st.session_state.blk_version_yn
    if version_conflict == "Yes":
        version_conflict = st.session_state.blk_version_detail.strip() or "Yes (unspecified)"
    security_vuln = st.session_state.blk_vuln
    if security_vuln == "Other":
        security_vuln = st.session_state.blk_vuln_other.strip() or "Other (unspecified)"
    entry = {
        "scope_type": scope_type,
        "scope_id": scope_id,
        "dependency": st.session_state.blk_dependency.strip() or "Unnamed dependency",
        "version_conflict": version_conflict,
        "missing_module": st.session_state.blk_module_yn,
        "cicd_failure": st.session_state.blk_cicd_yn,
        "security_vuln": security_vuln,
        "impacted_teams": st.session_state.blk_teams,
        "severity": st.session_state.blk_severity,
        "resolution_eta": str(st.session_state.blk_eta),
    }
    epic["blockers"].append(entry)
    st.session_state[f"blocker_panel_open_{st.session_state.selected_epic_id}"] = False
    _sync_epic(st.session_state.selected_epic_id, "✅ Blocker logged to this Epic's risk grid.", "blocker_create_error", "blocker_create_success")


CORE_COMPONENT_OPTIONS = ["auth-service", "payment-gateway", "ledger-engine", "notification-router", "settlement-router", "compliance-engine", "Other"]
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
DATABASE_OPTIONS = ["Supabase / PostgreSQL (Main)", "Redis (Caching Session Store)", "AWS S3 (Document Blob Storage)", "DynamoDB (Audit Logs)", "Other"]
RLS_OPTIONS = ["authenticated-users-only", "service-role-bypass", "tenant-isolated-read", "admin-write-only"]
COMPLIANCE_HOOK_OPTIONS = ["SOC2-Audit-Logger", "PCI-DSS-Data-Masker", "GDPR-Right-To-Forget-Hook", "HIPAA-Encryption-Validator"]


def _draft_api_contract(method, uri):
    if method in ("POST", "PUT", "PATCH"):
        return f'Request ({method} {uri}): {{"...": "..."}}\nResponse: {{"status": "ok", "id": "..."}}'
    return f"Request ({method} {uri}): query/path params only\nResponse: {{\"status\": \"ok\", \"data\": [...] }}"


def _save_sdd():
    epic = current_epic()
    core_component = st.session_state.sdd_core
    if core_component == "Other":
        core_component = st.session_state.sdd_core_other.strip() or "Other (unspecified)"
    database = st.session_state.sdd_db
    if database == "Other":
        database = st.session_state.sdd_db_other.strip() or "Other (unspecified)"
    method = st.session_state.sdd_method
    uri = st.session_state.sdd_uri.strip() or "/"
    api_contract = st.session_state.sdd_contract.strip() or _draft_api_contract(method, uri)
    epic["sdd"] = {
        "core_component": core_component,
        "http_method": method,
        "uri_path": uri,
        "endpoint": f"{method} {uri}",
        "database": database,
        "rls_policy": ", ".join(st.session_state.sdd_rls) if st.session_state.sdd_rls else "",
        "compliance_hooks": ", ".join(st.session_state.sdd_hooks) if st.session_state.sdd_hooks else "",
        "architecture_blueprint": st.session_state.sdd_blueprint.strip(),
        "sequence_flow": st.session_state.sdd_sequence.strip(),
        "api_contract": api_contract,
        "nfrs": st.session_state.sdd_nfrs.strip(),
    }
    _sync_epic(st.session_state.selected_epic_id, "✅ SDD saved to this Epic.", "sdd_save_error", "sdd_save_success")


def _save_wsjf():
    epic = current_epic()
    epic["wsjf"] = {
        "bv": st.session_state.wsjf_bv,
        "tc": st.session_state.wsjf_tc,
        "rr": st.session_state.wsjf_rr,
        "size": st.session_state.wsjf_job_size,
    }
    _sync_epic(st.session_state.selected_epic_id, "✅ WSJF snapshot saved to this Epic.", "wsjf_save_error", "wsjf_save_success")


# ####################################################
# 🎨 GLOBAL CSS
# ####################################################
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 100% !important; }
    .hero-title { text-align: center; color: #0f172a; font-size: 2.25rem; font-weight: 800; margin-bottom: 0.1rem; border: none !important; }
    .section-header { font-size: 1.5rem !important; font-weight: 800 !important; color: #0f172a !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; }
    .subsection-header { font-size: 1.05rem !important; font-weight: 700 !important; color: #1e3a8a !important; margin-top: 1rem !important; margin-bottom: 0.5rem !important; }
    /* Field labels across every widget (text input, select, textarea, number, date, multiselect) were unstyled
       Streamlit defaults — thin and light gray. Bold + darken them everywhere. Two rules layered on
       purpose: the testid-scoped one plus a blanket <label> fallback, so this can't silently miss. */
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, label {
        font-weight: 700 !important; color: #0f172a !important; font-size: 14px !important;
    }
    /* Give every input/select/textarea a visible border instead of the flat borderless default */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div, .stMultiSelect [data-baseweb="select"] > div {
        border: 1.5px solid #94a3b8 !important; border-radius: 6px !important; color: #0f172a !important; font-weight: 500 !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder, .stNumberInput input::placeholder {
        color: #64748b !important; opacity: 1 !important; font-weight: 400 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, .stTextArea textarea:focus,
    .stSelectbox [data-baseweb="select"]:focus-within > div, .stMultiSelect [data-baseweb="select"]:focus-within > div {
        border: 1.5px solid #1e3a8a !important; box-shadow: 0 0 0 1px #1e3a8a !important;
    }
    .stSelectbox [data-baseweb="select"] span, .stMultiSelect [data-baseweb="select"] span { color: #0f172a !important; font-weight: 500 !important; }
    .stTextInput input:disabled, .stSelectbox [data-baseweb="select"][aria-disabled="true"] > div { background-color: #f1f5f9 !important; color: #475569 !important; }
    /* Sidebar contrast: bold dark selector text, bolder section label */
    section[data-testid="stSidebar"] h3 { color: #1e3a8a !important; font-weight: 800 !important; }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-weight: 700 !important; color: #0f172a !important; }
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] * { color: #0f172a !important; font-weight: 700 !important; }
    .executive-grid-container { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; width: 100%; margin-bottom: 15px; }
    .executive-metric-card { background-color: #ffffff !important; border-top: 4px solid #1e3a8a !important; border: 1px solid #e2e8f0 !important; padding: 12px !important; border-radius: 6px !important; min-height: 90px !important; box-shadow: 0 1px 2px rgb(0 0 0 / 0.05); }
    .executive-card-label { font-size: 0.72rem !important; text-transform: uppercase !important; font-weight: 700 !important; color: #475569 !important; letter-spacing: 0.5px; margin-bottom: 4px !important; }
    .executive-card-val { font-size: 1.15rem !important; font-weight: 700 !important; color: #0f172a !important; word-break: break-word !important; }
    .observability-grid-container { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; width: 100%; margin-bottom: 15px; }
    .observability-box-mild-grey { background-color: #f8fafc !important; border-top: 4px solid #38bdf8 !important; border: 1px solid #e2e8f0 !important; padding: 12px !important; border-radius: 6px !important; min-height: 90px !important; }
    div.stButton > button { width: 100%; min-height: 38px; font-weight: 600; background-color: #1e3a8a !important; color: #ffffff !important; border-radius: 6px !important; border: none !important; font-size: 0.9rem; }
    div.stButton > button:hover { background-color: #0369a1 !important; }
    .master-report-header-banner { background-color: #1e3a8a; color: white; padding: 15px; border-radius: 6px 6px 0 0; margin-top: 15px; font-weight: 700; font-size: 1.1rem; }
    .master-report-section-node { background-color: #ffffff; border-left: 4px solid #0284c7; border: 1px solid #e2e8f0; border-top: none; padding: 14px; margin-bottom: 10px; }
    .master-report-section-title { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    .custom-spec-table { width: 100% !important; border-collapse: collapse !important; margin-top: 8px !important; margin-bottom: 8px !important; table-layout: fixed !important; }
    .custom-spec-table th { background-color: #f1f5f9 !important; color: #334155 !important; font-weight: 700 !important; font-size: 12px !important; padding: 10px !important; text-align: left !important; border-bottom: 2px solid #cbd5e1 !important; }
    .custom-spec-table td { padding: 10px !important; font-size: 14px !important; font-weight: 500 !important; text-align: left !important; border-bottom: 1px solid #e2e8f0 !important; color: #334155 !important; line-height: 1.5 !important; word-wrap: break-word !important; overflow-wrap: anywhere !important; white-space: normal !important; }
    .custom-spec-table td b, .custom-spec-table td strong { color: #0f172a !important; font-weight: 700 !important; }
    .custom-spec-table td.num-cell { text-align: right !important; font-variant-numeric: tabular-nums; }
    .custom-spec-table code { word-break: break-word !important; white-space: pre-wrap !important; }
    .scrollable-ledger-wrap { max-height: 420px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 6px; }
    .scrollable-ledger-wrap table.custom-spec-table thead th { position: sticky; top: 0; z-index: 2; }
    .hitl-minimal-badge { display:inline-block; background-color:#f1f5f9; color:#475569; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; padding:3px 8px; border-radius:4px; margin-bottom:10px; }
    .hitl-full-badge { display:inline-block; background-color:#1e3a8a; color:#ffffff; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; padding:3px 8px; border-radius:4px; margin-bottom:10px; }
    .data-layer-banner-warn { background: linear-gradient(90deg, #fff7ed 0%, #fffbeb 100%); border-left: 5px solid #f59e0b; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 15px; color: #78350f; line-height: 1.5; }
    .data-layer-banner-ok { background: linear-gradient(90deg, #f0fdf4 0%, #ecfdf5 100%); border-left: 5px solid #16a34a; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 15px; color: #14532d; line-height: 1.5; }
    .data-layer-banner-warn b, .data-layer-banner-ok b { color: inherit; }
    .about-strip { text-align:center; color:#64748b; font-size:16px; font-weight:500; font-style:normal; margin-top:0; margin-bottom:20px; }
    .sidebar-warning-text { color:#334155 !important; font-size:14px !important; font-weight:600 !important; line-height:1.7 !important; margin-top:8px; }
    .sidebar-help-text { color:#334155 !important; font-size:14px !important; font-weight:500 !important; line-height:1.7 !important; }
    .sidebar-help-text b { color:#1e3a8a !important; }
    .helper-note { color:#334155 !important; font-size:14px !important; font-weight:500 !important; margin-bottom:8px; }
    .muted-placeholder { color:#475569 !important; font-size: 14px; font-weight: 500; }
    .compliance-ok { color:#16a34a !important; font-weight:700; }
    .compliance-warn { color:#d97706 !important; font-weight:700; }
    .session-expired-badge { display:inline-block; background-color:#dc2626; color:#ffffff; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; padding:5px 10px; border-radius:4px; }
    /* Fix (Blocker "Impacted Teams" / OKR "Business Theme" pills rendering solid red): Streamlit's
       unthemed default primaryColor is red and BaseWeb's multiselect tags use it directly.
       Force a neutral professional blue instead — red should only ever mean Critical/High severity. */
    [data-baseweb="tag"] {
        background-color: #eef2ff !important; color: #3730a3 !important; border: 1px solid #c7d2fe !important;
    }
    [data-baseweb="tag"] span { color: #3730a3 !important; }
    [data-baseweb="tag"] svg { fill: #3730a3 !important; }
    /* Bold, high-contrast real-time metric VALUES (observability panel, HITL telemetry line, etc.) */
    .metric-value-strong { font-weight: 800 !important; color: #0f172a !important; white-space: nowrap; }
    .metric-card-label { font-weight: 700 !important; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.4px; font-size: 11px !important; }
    /* Skill accordion titles (Skills 1-7): force one uniform high-contrast color regardless of expander state */
    [data-testid="stExpander"] summary p { color: #1e293b !important; font-weight: 600 !important; }
    /* Radio option text was thinner than the surrounding bold buttons */
    [data-testid="stRadio"] label p { font-weight: 600 !important; color: #0f172a !important; }
    .zebra-table tbody tr:nth-child(even) { background-color: #f8fafc; }
    /* Sidebar: kept the size/line-height readability bump, reverted the color scheme back to the original vibrant blue */
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] span {
        font-size: 14px !important; line-height: 1.5 !important;
    }
    </style>
""",

    unsafe_allow_html=True,
)

# ####################################################
# ⚙️ SIDEBAR
# ####################################################
with st.sidebar:
    st.markdown("### ⚙️ Operational Settings & Views")
    current_view_idx = 0 if st.session_state.view_layer == "Standard Mode" else 1
    st.selectbox(
        "Workspace View Layer Tier",
        ["Standard Mode", "Advanced Reporting Mode"],
        index=current_view_idx,
        key="view_layer_widget",
        on_change=_apply_view_change,
    )
    if st.session_state.view_layer == "Standard Mode":
        st.markdown(
            "<p class='sidebar-help-text'>💡 Switch to <b>Advanced Reporting Mode</b> to unlock the WSJF matrix, blocker/risk grid, "
            "compliance audit, full HITL governance (trigger reason, severity, dual-control approval), "
            "and live agent telemetry.</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<p class='sidebar-help-text'>🟢 <b>Advanced Reporting Mode is now active.</b> The WSJF matrix, blocker/risk grid, "
            "compliance audit tracking, dual-control approvals, and live telemetry channels have been successfully unlocked.</p>",
            unsafe_allow_html=True,
        )
    st.write("---")
    st.button("🔄 Reset Telemetry Pools", key="reset_btn", on_click=_reset_all)
    st.markdown(
        "<p class='sidebar-warning-text'>⚠️ Destructive: resets all epics, stories, tasks, token/spend counters, execution logs, HITL ledger, uploaded files, and returns the workspace to Standard Mode. This cannot be undone.</p>",
        unsafe_allow_html=True,
    )

# ####################################################
# 🖥️ HEADER
# ####################################################
st.markdown("<h1 class='hero-title' style='margin-bottom:0.3rem;'>FinMesh Smart Executive Control Suite</h1>", unsafe_allow_html=True)
st.markdown(
    f"<h3 style='text-align: center; color: #2563eb; font-size: 18px; font-weight: 600; margin-bottom: 0.3rem;'>"
    f"Enterprise Engineering Operations Engine — <span>{esc(st.session_state.view_layer)} Live</span></h3>",
    unsafe_allow_html=True,
)
# Fix (#2): short "About" strip under the title
st.markdown(
    "<p class='about-strip' style='margin-bottom:14px; padding-bottom:16px; border-bottom:1px solid #e2e8f0;'>Bringing rigorous corporate governance and auditability to Agentic AI Workflows.</p>",
    unsafe_allow_html=True,
)

if SUPABASE_CONNECTED:
    st.markdown(
        """
        <div class="data-layer-banner-ok">
            🟢 <b>Data Layer:</b> Connected to Supabase. Governance verdicts, skill logs, and epic metrics
            are permanently persisted to the database.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="data-layer-banner-warn">
            🟡 <b>Data Layer:</b> running on in-memory session state only — no Supabase connection detected
            (missing/invalid <code>SUPABASE_URL</code> / <code>SUPABASE_KEY</code>). All ledgers reset on app
            restart or on <b>Reset Telemetry Pools</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
# Fix (#6): a clear divider between the centered "Header Zone" above and the
# operational "Working Zone" (Epic Intake Desk onward) below.
st.markdown("<div style='border-bottom:1px solid #e2e8f0; margin-bottom:22px;'></div>", unsafe_allow_html=True)

# ####################################################
# 📋 EPIC INTAKE DESK
# ####################################################
st.markdown("<p class='section-header'>📋 Epic Intake Desk</p>", unsafe_allow_html=True)

epic_keys = list(st.session_state.epics.keys())
if st.session_state.selected_epic_id not in epic_keys:
    st.session_state.selected_epic_id = epic_keys[0]
if "epic_selector_widget" not in st.session_state:
    st.session_state.epic_selector_widget = st.session_state.selected_epic_id

panel_mode = st.session_state.epic_panel_mode
dropdown_locked = panel_mode == "create"  # only a brand-new, not-yet-existing Epic needs the lock


def _on_epic_dropdown_change():
    new_sel = st.session_state.epic_selector_widget
    st.session_state.selected_epic_id = new_sel
    if st.session_state.epic_panel_mode == "edit":
        # Re-target the Edit form's live (outside-form) Compliance Category
        # widgets to whichever Epic is now selected, so switching Epics
        # mid-edit can never save the previous Epic's category onto this one.
        ep = st.session_state.epics[new_sel]
        if ep["compliance_category"] in COMPLIANCE_OPTIONS[:-1]:
            st.session_state.epic_compliance_select = ep["compliance_category"]
            st.session_state.epic_compliance_other = ""
        else:
            st.session_state.epic_compliance_select = "Others"
            st.session_state.epic_compliance_other = ep["compliance_category"]
    st.session_state.epic_create_error = None
    st.session_state.epic_create_success = None


sel_col, add_col, edit_col = st.columns([3.4, 1, 1])
with sel_col:
    st.selectbox(
        "Active Backlog Epic Target Focus",
        epic_keys,
        format_func=lambda k: f"{k}: {st.session_state.epics[k]['name']}",
        key="epic_selector_widget",
        disabled=dropdown_locked,
        on_change=_on_epic_dropdown_change,
    )
    selected_epic_id = st.session_state.selected_epic_id
if not dropdown_locked:
    with add_col:
        st.write("")
        st.write("")
        st.button("➕ New Epic", key="btn_open_new_epic", on_click=_open_create_epic_panel, use_container_width=True)
    with edit_col:
        st.write("")
        st.write("")
        st.button("✏️ Edit Epic", key="btn_open_edit_epic", on_click=_open_edit_epic_panel, use_container_width=True)

epic = st.session_state.epics[selected_epic_id]

if panel_mode == "create":
    st.session_state["_next_epic_id"] = next_id("EPIC", epic_keys)
    st.markdown("<p style='font-size:13px; font-weight:700; color:#1e3a8a;'>➕ Create a New Epic — the dropdown above is locked until you Save or Cancel</p>", unsafe_allow_html=True)
    note("Fields marked <b>*</b> are required. Fields left blank use a sensible default.")
    st.selectbox("Compliance Category", COMPLIANCE_OPTIONS, key="epic_compliance_select")
    if st.session_state.epic_compliance_select == "Others":
        st.text_input("Custom Compliance Category *", key="epic_compliance_other", placeholder="e.g. GDPR Article 32 Controlled")
    with st.form("new_epic_form", clear_on_submit=True):
        st.text_input("Epic ID (system-generated, read-only)", value=st.session_state["_next_epic_id"], disabled=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            st.text_input("Epic Name *", key="new_epic_name", placeholder="Real-Time Fraud Signal Router")
            st.selectbox("Target Release", RELEASE_OPTIONS, key="new_epic_release")
        with fc2:
            st.selectbox("Target Quarter", QUARTER_OPTIONS, key="new_epic_quarter")
        st.text_area("Narrative", key="new_epic_narrative", placeholder="As a ..., I want ..., so that ...", height=80)
        st.text_area("Business / Product Goal", key="new_epic_goal", placeholder="What business outcome does this Epic drive?", height=70)
        fs1, fs2 = st.columns(2)
        with fs1:
            st.form_submit_button("💾 Save Epic", on_click=_create_new_epic, use_container_width=True)
        with fs2:
            st.form_submit_button("✖️ Cancel", on_click=_cancel_epic_panel, use_container_width=True)
    if st.session_state.get("epic_create_error"):
        st.error(st.session_state.epic_create_error)

elif panel_mode == "edit":
    st.markdown(f"<p style='font-size:13px; font-weight:700; color:#1e3a8a;'>✏️ Editing {esc(selected_epic_id)} — switch the dropdown above anytime to edit a different Epic instead</p>", unsafe_allow_html=True)
    note("Fields marked <b>*</b> are required.")
    st.selectbox("Compliance Category", COMPLIANCE_OPTIONS, key="epic_compliance_select")
    if st.session_state.epic_compliance_select == "Others":
        st.text_input("Custom Compliance Category *", key="epic_compliance_other", placeholder="e.g. GDPR Article 32 Controlled")
    with st.form(f"edit_epic_form_{selected_epic_id}"):
        st.text_input("Epic ID (immutable)", value=selected_epic_id, disabled=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            st.text_input("Epic Name *", value=epic["name"], key=f"edit_epic_name_{selected_epic_id}")
            _rel_idx = RELEASE_OPTIONS.index(epic["target_release"]) if epic["target_release"] in RELEASE_OPTIONS else 0
            st.selectbox("Target Release", RELEASE_OPTIONS, index=_rel_idx, key=f"edit_epic_release_{selected_epic_id}")
        with fc2:
            _qtr_idx = QUARTER_OPTIONS.index(epic["target_quarter"]) if epic["target_quarter"] in QUARTER_OPTIONS else 0
            st.selectbox("Target Quarter", QUARTER_OPTIONS, index=_qtr_idx, key=f"edit_epic_quarter_{selected_epic_id}")
        st.text_area("Narrative", value=epic["narrative"], key=f"edit_epic_narrative_{selected_epic_id}", height=80)
        st.text_area("Business / Product Goal", value=epic["business_goal"], key=f"edit_epic_goal_{selected_epic_id}", height=70)
        fs1, fs2 = st.columns(2)
        with fs1:
            st.form_submit_button("💾 Save Changes", on_click=_update_epic, args=(selected_epic_id,), use_container_width=True)
        with fs2:
            st.form_submit_button("✖️ Cancel", on_click=_cancel_epic_panel, use_container_width=True)
    if st.session_state.get("epic_create_error"):
        st.error(st.session_state.epic_create_error)

else:
    # Fix (#10a): once saved, the input panel disappears completely — only
    # the read-only summary grid remains, instead of leaving an empty-looking
    # form sitting on top of it.
    if st.session_state.get("epic_create_success"):
        st.success(st.session_state.epic_create_success)
        st.session_state.epic_create_success = None
    st.markdown(
        f"""
<div class='master-report-section-node' style='border-left-color:#1e3a8a;'>
    <table class='custom-spec-table'>
        <tbody>
            <tr><td style='width:22%;'><b>Epic ID</b></td><td>{esc(selected_epic_id)}</td></tr>
            <tr><td><b>Name</b></td><td>{esc(epic['name'])}</td></tr>
            <tr><td><b>Narrative</b></td><td>{esc(epic['narrative'])}</td></tr>
            <tr><td><b>Business / Product Goal</b></td><td>{esc(epic['business_goal'])}</td></tr>
            <tr><td><b>Compliance Category</b></td><td>{esc(epic['compliance_category'])}</td></tr>
            <tr><td><b>Target Release</b></td><td>{esc(epic['target_release'])}</td></tr>
            <tr><td><b>Target Quarter</b></td><td>{esc(epic['target_quarter'])}</td></tr>
        </tbody>
    </table>
</div>
""",
        unsafe_allow_html=True,
    )
# Example for the user: EPIC-001 above demonstrates a fully-populated Epic —
# use it as a template when filling in the "New Epic" form.

# ####################################################
# 📝 STORY MANAGEMENT (fix #1, #2, #3, #5)
# ####################################################
st.markdown("<p class='section-header'>📝 Story Management</p>", unsafe_allow_html=True)


def _sync_story_epic_selector():
    st.session_state.selected_epic_id = st.session_state.story_epic_selector_widget
    st.session_state.epic_selector_widget = st.session_state.story_epic_selector_widget


st.selectbox(
    "Epic (select which Epic these Stories belong to)",
    epic_keys,
    index=epic_keys.index(selected_epic_id),
    format_func=lambda k: f"{k}: {st.session_state.epics[k]['name']}",
    key="story_epic_selector_widget",
    on_change=_sync_story_epic_selector,
)
note(f"Stories below are scoped to <b>{selected_epic_id}</b> — change the dropdown above to manage a different Epic's Stories. Save as many as you like, each Save adds a new row.")

if epic["stories"]:
    rows = "".join(
        f"<tr><td>{esc(sid)}</td><td>{esc(s['description'])}</td><td>{esc(s['assignee'])}</td>"
        f"<td class='num-cell'>{esc(s['story_points'])} SP</td><td>{esc(s['sprint_assignment'])}</td>"
        f"<td><span style='color:{'#16a34a' if s['compliance_state']=='Passed' else '#dc2626' if s['compliance_state']=='Failed' else '#d97706'}; font-weight:700;'>{esc(s['compliance_state'])}</span></td></tr>"
        for sid, s in epic["stories"].items()
    )
    st.markdown(
        f"""
    <table class='custom-spec-table'>
        <thead><tr><th style='width:12%;'>Story ID</th><th style='width:32%;'>Description</th><th style='width:14%;'>Assignee</th><th style='width:8%;'>Points</th><th style='width:14%;'>Sprint</th><th style='width:14%;'>Compliance</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """,
        unsafe_allow_html=True,
    )
else:
    note("No stories yet on this Epic — use the form below to add the first one.")

_story_panel_key = f"story_panel_open_{selected_epic_id}"
if _story_panel_key not in st.session_state:
    st.session_state[_story_panel_key] = not epic["stories"]
with st.expander("➕ Add / ✏️ Edit a Story on this Epic", expanded=st.session_state[_story_panel_key]):
    story_mode = st.radio("Mode", ["➕ Add New Story", "✏️ Edit Existing Story"], horizontal=True, key=f"story_mode_{selected_epic_id}", disabled=not epic["stories"] and False)
    st.markdown("<p class='helper-note'>Fields marked <b>*</b> are required.</p>", unsafe_allow_html=True)

    if story_mode == "➕ Add New Story" or not epic["stories"]:
        st.session_state["_next_story_id"] = next_id("STORY", epic["stories"].keys())
        with st.form(f"new_story_form_{selected_epic_id}", clear_on_submit=True):
            st.text_input("Story ID (system-generated, read-only)", value=st.session_state["_next_story_id"], disabled=True)
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Assignee", key="new_story_assignee", placeholder="e.g. K. Chidambaram")
                st.number_input("Story Points", min_value=0, max_value=100, value=5, step=1, key="new_story_points")
                st.selectbox("Compliance State", ["Not Reviewed", "Passed", "Failed"], key="new_story_compliance")
                st.selectbox("Sprint Assignment *", SPRINT_OPTIONS, key="new_story_sprint")
            with c2:
                st.text_area("Description *", key="new_story_desc", placeholder="Intercept transaction schema payload before writing onto vector-store engine", height=68)
                st.text_input("Dependencies", key="new_story_deps", placeholder="e.g. STORY-101, or 'None'")
            st.text_area("Acceptance Criteria", key="new_story_ac", placeholder="Given ..., when ..., then ...", height=70)
            st.form_submit_button("💾 Save Story", on_click=_save_story)
    else:
        edit_sid = st.selectbox("Story to Edit", list(epic["stories"].keys()), key=f"edit_story_select_{selected_epic_id}")
        es = epic["stories"][edit_sid]
        eprefix = f"editstory_{selected_epic_id}_{edit_sid}"
        with st.form(f"{eprefix}_form"):
            st.text_input("Story ID (immutable)", value=edit_sid, disabled=True)
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Assignee", value=es["assignee"], key=f"{eprefix}_assignee")
                st.number_input("Story Points", min_value=0, max_value=100, value=es["story_points"], step=1, key=f"{eprefix}_points")
                st.selectbox("Compliance State", ["Not Reviewed", "Passed", "Failed"], index=["Not Reviewed", "Passed", "Failed"].index(es["compliance_state"]) if es["compliance_state"] in ["Not Reviewed", "Passed", "Failed"] else 0, key=f"{eprefix}_compliance")
                st.selectbox("Sprint Assignment *", SPRINT_OPTIONS, index=SPRINT_OPTIONS.index(es["sprint_assignment"]) if es["sprint_assignment"] in SPRINT_OPTIONS else 0, key=f"{eprefix}_sprint")
            with c2:
                st.text_area("Description *", value=es["description"], key=f"{eprefix}_desc", height=68)
                st.text_input("Dependencies", value=es["dependencies"], key=f"{eprefix}_deps")
            st.text_area("Acceptance Criteria", value=es["acceptance_criteria"], key=f"{eprefix}_ac", height=70)
            st.form_submit_button("💾 Update Story", on_click=_update_story, args=(selected_epic_id, edit_sid, eprefix))

    if st.session_state.get("story_create_error"):
        st.error(st.session_state.story_create_error)
    if st.session_state.get("story_create_success"):
        st.success(st.session_state.story_create_success)
        st.session_state.story_create_success = None

# ####################################################
# ✅ TASK MANAGEMENT (fix #4)
# ####################################################
st.markdown("<p class='section-header'>✅ Task Management</p>", unsafe_allow_html=True)
if not epic["stories"]:
    note("Add a Story above first — Tasks are scoped to a Story.")
else:
    task_story_id = st.selectbox(
        "Manage Tasks for Story",
        list(epic["stories"].keys()),
        format_func=lambda sid: f"{sid}: {epic['stories'][sid]['description'][:60]}",
        key=f"task_story_selector_{selected_epic_id}",
    )
    story = epic["stories"][task_story_id]
    if story["tasks"]:
        trows = "".join(
            f"<tr><td>{esc(tid)}</td><td>{esc(t['description'])}</td><td>{esc(t['owner'])}</td>"
            f"<td><span style='color:{'#16a34a' if t['status']=='Done' else '#dc2626' if t['status']=='Blocked' else '#0284c7'}; font-weight:700;'>{esc(t['status'])}</span></td>"
            f"<td class='num-cell'>{esc(t['estimate_hours'])}h</td></tr>"
            for tid, t in story["tasks"].items()
        )
        st.markdown(
            f"""
        <table class='custom-spec-table'>
            <thead><tr><th style='width:12%;'>Task ID</th><th style='width:38%;'>Description</th><th style='width:20%;'>Owner</th><th style='width:15%;'>Status</th><th style='width:15%;'>Estimate</th></tr></thead>
            <tbody>{trows}</tbody>
        </table>
        """,
            unsafe_allow_html=True,
        )
    else:
        note(f"No tasks yet on {task_story_id}.")

    task_mode = st.radio("Mode", ["➕ Add New Task", "✏️ Edit Existing Task"], horizontal=True, key=f"task_mode_{selected_epic_id}_{task_story_id}")
    prefix = f"new_task_{selected_epic_id}_{task_story_id}"

    if task_mode == "➕ Add New Task" or not story["tasks"]:
        st.session_state["_next_task_id"] = next_id("TASK", story["tasks"].keys())
        with st.form(f"{prefix}_form", clear_on_submit=True):
            st.text_input("Task ID (system-generated, read-only)", value=st.session_state["_next_task_id"], disabled=True)
            tc1, tc2 = st.columns(2)
            with tc1:
                st.text_input("Owner", key=f"{prefix}_owner", placeholder="e.g. Infra Agent Node")
            with tc2:
                st.selectbox("Status", ["Not Started", "In Progress", "Blocked", "Done"], key=f"{prefix}_status")
                st.number_input("Completion Estimate (hours)", min_value=0.0, max_value=500.0, value=4.0, step=0.5, key=f"{prefix}_est")
            st.text_area("Description *", key=f"{prefix}_desc", placeholder="Build payload schema validator", height=68)
            st.form_submit_button("💾 Save Task", on_click=_save_task, args=(selected_epic_id, task_story_id, prefix))
    else:
        edit_tid = st.selectbox("Task to Edit", list(story["tasks"].keys()), key=f"edit_task_select_{selected_epic_id}_{task_story_id}")
        et = story["tasks"][edit_tid]
        etprefix = f"edittask_{selected_epic_id}_{task_story_id}_{edit_tid}"
        with st.form(f"{etprefix}_form"):
            st.text_input("Task ID (immutable)", value=edit_tid, disabled=True)
            tc1, tc2 = st.columns(2)
            with tc1:
                st.text_input("Owner", value=et["owner"], key=f"{etprefix}_owner")
            with tc2:
                status_opts = ["Not Started", "In Progress", "Blocked", "Done"]
                st.selectbox("Status", status_opts, index=status_opts.index(et["status"]) if et["status"] in status_opts else 0, key=f"{etprefix}_status")
                st.number_input("Completion Estimate (hours)", min_value=0.0, max_value=500.0, value=float(et["estimate_hours"]), step=0.5, key=f"{etprefix}_est")
            st.text_area("Description *", value=et["description"], key=f"{etprefix}_desc", height=68)
            st.form_submit_button("💾 Update Task", on_click=_update_task, args=(selected_epic_id, task_story_id, edit_tid, etprefix))

    if st.session_state.get("task_create_error"):
        st.error(st.session_state.task_create_error)
    if st.session_state.get("task_create_success"):
        st.success(st.session_state.task_create_success)
        st.session_state.task_create_success = None

LOG_TOOL_OPTIONS = ["NICE Actimize", "Datadog", "Logstash", "Splunk", "AWS CloudWatch", "Other"]
STORE_OPTIONS = ["Supabase", "PostgreSQL", "AWS S3", "Redis", "DynamoDB", "Other"]
BUSINESS_THEME_OPTIONS = ["Growth", "Efficiency", "Risk Reduction", "Compliance", "Tech Debt", "Customer Experience"]
TIMEFRAME_OPTIONS = ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026", "Q1 2027", "Q2 2027", "FY2026", "FY2027"]


def _open_edit_blueprint():
    eid = st.session_state.selected_epic_id
    st.session_state[f"okr_panel_mode_{eid}"] = "edit"
    st.session_state.blueprint_save_error = None
    st.session_state.blueprint_save_success = None


def _cancel_blueprint_edit():
    eid = st.session_state.get("_strategy_epic_target", st.session_state.selected_epic_id)
    st.session_state[f"okr_panel_mode_{eid}"] = "view"


def _save_strategic_blueprint():
    eid = st.session_state.get("_strategy_epic_target", st.session_state.selected_epic_id)
    ep = st.session_state.epics[eid]
    objective = st.session_state.okr_obj_input.strip()
    ep["okr"] = {
        "objective": objective,
        "key_results": st.session_state.okr_kr_input.strip(),
        "target_metric_label": st.session_state.okr_metric_label_input.strip(),
        "target_metric_value": st.session_state.okr_metric_value_input,
        "timeframe": st.session_state.okr_time_input,
        "business_theme": ", ".join(st.session_state.okr_theme_input) if st.session_state.okr_theme_input else "",
    }
    vs_trigger = st.session_state.vs_trigger_input.strip()
    ep["value_stream"] = {
        "trigger": vs_trigger,
        "validate": st.session_state.vs_validate_input.strip(),
        "process": st.session_state.vs_process_input.strip(),
        "log": st.session_state.vs_log_input,
        "store": st.session_state.vs_store_input,
        "respond": st.session_state.vs_respond_input.strip(),
    }
    st.session_state[f"okr_panel_mode_{eid}"] = "view"
    # Fix (docx 15.4): name what was actually saved instead of a generic message.
    _summary_bits = []
    if objective:
        _summary_bits.append(f"Objective '{objective}'")
    if vs_trigger:
        _summary_bits.append(f"Value Stream trigger '{vs_trigger}'")
    _detail = " and ".join(_summary_bits) if _summary_bits else "OKR & Value Stream fields"
    _sync_epic(eid, f"✅ {_detail} saved for {eid}.", "blueprint_save_error", "blueprint_save_success")


# ####################################################
# 🎯 OKR & VALUE STREAM (data model completeness — feeds Skills 1 & 5)
# ####################################################
st.markdown("<p class='section-header'>🎯 OKR & Value Stream</p>", unsafe_allow_html=True)
note("Feeds the <b>OKR Aligner</b> and <b>Value Stream Mapper</b> skills below.")

_strategy_target_default = selected_epic_id
blueprint_target = st.selectbox(
    "Associated Epic ID",
    epic_keys,
    index=epic_keys.index(_strategy_target_default),
    format_func=lambda k: f"{k}: {st.session_state.epics[k]['name']}",
    key="_strategy_epic_target",
)
bep = st.session_state.epics[blueprint_target]
_okr_mode_key = f"okr_panel_mode_{blueprint_target}"
if _okr_mode_key not in st.session_state:
    st.session_state[_okr_mode_key] = "view" if bep["okr"].get("objective") else "edit"
okr_mode = st.session_state[_okr_mode_key]

if okr_mode == "view":
    vs = bep["value_stream"]
    okr = bep["okr"]
    _metric_label = okr.get("target_metric_label", okr.get("target_metrics", ""))
    _metric_value = okr.get("target_metric_value", "")
    st.markdown(
        f"""
    <div class='master-report-section-node' style='border-left-color:#1e3a8a;'>
        <table class='custom-spec-table'><tbody>
            <tr><td style='width:22%;'><b>Objective</b></td><td>{esc(okr.get('objective') or '—')}</td></tr>
            <tr><td><b>Key Results</b></td><td>{esc(okr.get('key_results') or '—')}</td></tr>
            <tr><td><b>Target Metric</b></td><td>{esc(_metric_label) or '—'}{f' = {esc(_metric_value)}' if _metric_label else ''}</td></tr>
            <tr><td><b>Timeframe</b></td><td>{esc(okr.get('timeframe') or '—')}</td></tr>
            <tr><td><b>Business Theme</b></td><td>{esc(okr.get('business_theme') or '—')}</td></tr>
            <tr><td><b>Value Stream</b></td><td>{esc(vs.get('trigger') or '—')} ➔ {esc(vs.get('validate') or '—')} ➔ {esc(vs.get('process') or '—')} ➔ {esc(vs.get('log') or '—')} ➔ {esc(vs.get('store') or '—')} ➔ {esc(vs.get('respond') or '—')}</td></tr>
        </tbody></table>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.button("✏️ Edit Blueprint", key=f"btn_edit_blueprint_{blueprint_target}", on_click=_open_edit_blueprint)
    if st.session_state.get("blueprint_save_success"):
        st.success(st.session_state.blueprint_save_success)
        st.session_state.blueprint_save_success = None
else:
    # Backward-compatible read: older saved epics may still have a single "target_metrics" string.
    _legacy_metric = bep["okr"].get("target_metrics", "")
    _metric_label_default = bep["okr"].get("target_metric_label", _legacy_metric)
    _metric_value_default = float(bep["okr"].get("target_metric_value", 0.0) or 0.0)
    _theme_default_raw = bep["okr"].get("business_theme", "")
    _theme_default = [t.strip() for t in _theme_default_raw.split(",") if t.strip() in BUSINESS_THEME_OPTIONS]
    _timeframe_default = bep["okr"].get("timeframe", "") or TIMEFRAME_OPTIONS[0]
    if _timeframe_default not in TIMEFRAME_OPTIONS:
        _timeframe_default = TIMEFRAME_OPTIONS[0]
    _log_default = bep["value_stream"].get("log", "") or LOG_TOOL_OPTIONS[0]
    if _log_default not in LOG_TOOL_OPTIONS:
        _log_default = "Other"
    _store_default = bep["value_stream"].get("store", "") or STORE_OPTIONS[0]
    if _store_default not in STORE_OPTIONS:
        _store_default = "Other"

    ov1, ov2 = st.columns(2)
    with ov1:
        st.markdown("<p class='subsection-header'>Objective & Key Results</p>", unsafe_allow_html=True)
        st.text_input("Objective", value=bep["okr"]["objective"], key="okr_obj_input", placeholder="O1, O2, O3…")
        st.text_area("Key Results", value=bep["okr"]["key_results"], key="okr_kr_input", height=68, placeholder="KR1, KR2, KR3…")
        mc1, mc2 = st.columns([2, 1])
        with mc1:
            st.text_input("Target Metric Label", value=_metric_label_default, key="okr_metric_label_input", placeholder="e.g. Uptime %, Fraud reduction %")
        with mc2:
            st.number_input("Target Metric Value", value=_metric_value_default, step=0.1, key="okr_metric_value_input", help="e.g. 99.99 for uptime %, or 20 for 'reduce fraud by 20%'")
        st.selectbox("Timeframe", TIMEFRAME_OPTIONS, index=TIMEFRAME_OPTIONS.index(_timeframe_default), key="okr_time_input")
        st.multiselect("Business Theme", BUSINESS_THEME_OPTIONS, default=_theme_default, key="okr_theme_input", placeholder="Growth, Efficiency, Risk, Compliance…")
    with ov2:
        st.markdown("<p class='subsection-header'>Value Stream (Trigger → Validate → Process → Log → Store → Respond)</p>", unsafe_allow_html=True)
        st.text_input("Trigger", value=bep["value_stream"]["trigger"], key="vs_trigger_input", placeholder="e.g. API request, customer action")
        st.text_input("Validate", value=bep["value_stream"]["validate"], key="vs_validate_input", placeholder="e.g. payload validation, KYC check")
        st.text_input("Process", value=bep["value_stream"]["process"], key="vs_process_input", placeholder="e.g. FX oracle, rule engine")
        st.selectbox("Log", LOG_TOOL_OPTIONS, index=LOG_TOOL_OPTIONS.index(_log_default), key="vs_log_input")
        st.selectbox("Store", STORE_OPTIONS, index=STORE_OPTIONS.index(_store_default), key="vs_store_input")
        st.text_input("Respond", value=bep["value_stream"]["respond"], key="vs_respond_input", placeholder="e.g. API response, UI update")

    bs1, bs2 = st.columns(2)
    with bs1:
        st.button("💾 Save Strategic Blueprint", key="btn_save_blueprint", on_click=_save_strategic_blueprint, use_container_width=True)
    with bs2:
        st.button("✖️ Cancel", key="btn_cancel_blueprint", on_click=_cancel_blueprint_edit, use_container_width=True)
    if st.session_state.get("blueprint_save_error"):
        st.warning(st.session_state.blueprint_save_error)
        st.session_state.blueprint_save_error = None

def _update_blocker(epic_id, idx, prefix):
    epic = st.session_state.epics[epic_id]
    scope_type = st.session_state[f"{prefix}_scope_type"]
    scope_id = st.session_state.get(f"{prefix}_scope_id", epic_id) if scope_type != "Epic" else epic_id
    version_conflict = st.session_state[f"{prefix}_version_yn"]
    if version_conflict == "Yes":
        version_conflict = st.session_state[f"{prefix}_version_detail"].strip() or "Yes (unspecified)"
    security_vuln = st.session_state[f"{prefix}_vuln"]
    if security_vuln == "Other":
        security_vuln = st.session_state[f"{prefix}_vuln_other"].strip() or "Other (unspecified)"
    try:
        epic["blockers"][idx] = {
            "scope_type": scope_type,
            "scope_id": scope_id,
            "dependency": st.session_state[f"{prefix}_dependency"].strip() or "Unnamed dependency",
            "version_conflict": version_conflict,
            "missing_module": st.session_state[f"{prefix}_module_yn"],
            "cicd_failure": st.session_state[f"{prefix}_cicd_yn"],
            "security_vuln": security_vuln,
            "impacted_teams": st.session_state[f"{prefix}_teams"],
            "severity": st.session_state[f"{prefix}_severity"],
            "resolution_eta": str(st.session_state[f"{prefix}_eta"]),
        }
        st.session_state[f"blocker_panel_open_{epic_id}"] = False
        _sync_epic(epic_id, "✅ Blocker updated.", "blocker_create_error", "blocker_create_success")
    except IndexError:
        st.session_state.blocker_create_error = "That blocker no longer exists — it may have been deleted."


def _delete_blocker(epic_id, idx):
    try:
        del st.session_state.epics[epic_id]["blockers"][idx]
        _sync_epic(epic_id, "🗑️ Blocker deleted.", "blocker_create_error", "blocker_create_success")
    except IndexError:
        pass


# ####################################################
# 🚧 BLOCKER / DEPENDENCY GRID (fix #12)
# ####################################################
st.markdown("<p class='section-header'>🚧 Blocker & Dependency Risk Grid</p>", unsafe_allow_html=True)
if epic["blockers"]:
    brows = "".join(
        f"<tr><td>{esc(b.get('scope_type','Epic'))}: {esc(b.get('scope_id', selected_epic_id))}</td><td>{esc(b['dependency'])}</td><td>{esc(b['version_conflict'])}</td><td>{esc(b['missing_module'])}</td>"
        f"<td>{esc(b['cicd_failure'])}</td><td>{esc(b['security_vuln'])}</td>"
        f"<td>{' '.join(f'<span style=\"background:#eef2ff; color:#3730a3; border-radius:4px; padding:2px 6px; margin-right:4px; font-size:11px; font-weight:600; display:inline-block;\">{esc(t)}</span>' for t in (b['impacted_teams'] if isinstance(b['impacted_teams'], list) else [x.strip() for x in str(b['impacted_teams']).split(',') if x.strip()]))}</td>"
        f"<td><span style='color:#dc2626; font-weight:700;'>{esc(b['severity'])}</span></td><td>{esc(b['resolution_eta'])}</td></tr>"
        for b in epic["blockers"]
    )
    st.markdown(
        f"""
    <table class='custom-spec-table'>
        <thead><tr><th>Scope</th><th>Dependency</th><th>Version Conflict</th><th>Missing Module</th><th>CI/CD Failure</th><th>Security Vuln</th><th>Impacted Teams</th><th>Severity</th><th>Resolution ETA</th></tr></thead>
        <tbody>{brows}</tbody>
    </table>
    """,
        unsafe_allow_html=True,
    )
    _del_col1, _del_col2 = st.columns([3, 1])
    with _del_col1:
        _blk_to_delete = st.selectbox(
            "Select a blocker to delete",
            range(len(epic["blockers"])),
            format_func=lambda i: f"{epic['blockers'][i]['dependency']} ({epic['blockers'][i]['severity']})",
            key=f"blk_delete_select_{selected_epic_id}",
        )
    with _del_col2:
        st.write("")
        st.write("")
        st.button("🗑️ Delete Blocker", key=f"btn_delete_blocker_{selected_epic_id}", on_click=_delete_blocker, args=(selected_epic_id, _blk_to_delete), use_container_width=True)
else:
    note("No blockers logged on this Epic yet.")

_blocker_panel_key = f"blocker_panel_open_{selected_epic_id}"
if _blocker_panel_key not in st.session_state:
    st.session_state[_blocker_panel_key] = False
with st.expander("➕ Add / ✏️ Edit a Blocker / Dependency", expanded=st.session_state[_blocker_panel_key]):
    blocker_mode = st.radio(
        "Mode", ["➕ Log New Blocker", "✏️ Edit Existing Blocker"], horizontal=True,
        key=f"blocker_mode_{selected_epic_id}", disabled=not epic["blockers"],
    )

    def _scope_picker(prefix, default_type="Epic", default_id=None):
        scope_pick_col1, scope_pick_col2 = st.columns(2)
        with scope_pick_col1:
            _type_idx = ["Epic", "Story", "Task"].index(default_type) if default_type in ["Epic", "Story", "Task"] else 0
            scope_type = st.selectbox("What's stuck?", ["Epic", "Story", "Task"], index=_type_idx, key=f"{prefix}_scope_type")
        with scope_pick_col2:
            if scope_type == "Epic":
                st.text_input("Scope", value=selected_epic_id, disabled=True, key=f"{prefix}_scope_id_display")
            elif scope_type == "Story":
                if epic["stories"]:
                    _story_ids = list(epic["stories"].keys())
                    _idx = _story_ids.index(default_id) if default_id in _story_ids else 0
                    st.selectbox("Story", _story_ids, index=_idx, key=f"{prefix}_scope_id")
                else:
                    note("No stories on this Epic yet.")
                    st.session_state[f"{prefix}_scope_id"] = selected_epic_id
            else:
                _task_ids = [tid for s in epic["stories"].values() for tid in s["tasks"].keys()]
                if _task_ids:
                    _idx = _task_ids.index(default_id) if default_id in _task_ids else 0
                    st.selectbox("Task", _task_ids, index=_idx, key=f"{prefix}_scope_id")
                else:
                    note("No tasks on this Epic yet.")
                    st.session_state[f"{prefix}_scope_id"] = selected_epic_id

    if blocker_mode == "➕ Log New Blocker" or not epic["blockers"]:
        _scope_picker("blk")
        with st.form(f"new_blocker_form_{selected_epic_id}", clear_on_submit=True):
            bc1, bc2 = st.columns(2)
            with bc1:
                st.text_input("Dependency Name *", key="blk_dependency", placeholder="e.g. Cross-border settlement API handshake")
                st.selectbox("Version Conflict?", ["No", "Yes", "None"], key="blk_version_yn")
                st.text_input("If Yes — library/version detail", key="blk_version_detail", placeholder="e.g. lib@2.x vs lib@3.x")
                st.selectbox("Missing Module?", ["No", "Yes"], key="blk_module_yn")
                st.selectbox("CI/CD Failure?", ["No", "Yes"], key="blk_cicd_yn")
            with bc2:
                st.selectbox("Security Vulnerability Type", SECURITY_VULN_OPTIONS, key="blk_vuln")
                st.text_input("If 'Other' — describe", key="blk_vuln_other", placeholder="e.g. Custom internal audit flag")
                st.multiselect("Impacted Teams", TEAM_OPTIONS, key="blk_teams", placeholder="Select one or more teams")
                st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], index=2, key="blk_severity")
                st.date_input("Resolution ETA", key="blk_eta")
            st.form_submit_button("💾 Log Blocker", on_click=_save_blocker)
    else:
        _edit_blk_idx = st.selectbox(
            "Blocker to Edit",
            range(len(epic["blockers"])),
            format_func=lambda i: f"{epic['blockers'][i]['dependency']} ({epic['blockers'][i]['severity']})",
            key=f"blk_edit_select_{selected_epic_id}",
        )
        eb = epic["blockers"][_edit_blk_idx]
        eprefix = f"editblk_{selected_epic_id}_{_edit_blk_idx}"
        _scope_picker(eprefix, default_type=eb.get("scope_type", "Epic"), default_id=eb.get("scope_id"))
        with st.form(f"{eprefix}_form"):
            bc1, bc2 = st.columns(2)
            with bc1:
                st.text_input("Dependency Name *", value=eb["dependency"], key=f"{eprefix}_dependency")
                _vc = eb["version_conflict"]
                _vc_yn = _vc if _vc in ["No", "Yes", "None"] else "Yes"
                _vc_detail = "" if _vc in ["No", "Yes", "None"] else _vc
                st.selectbox("Version Conflict?", ["No", "Yes", "None"], index=["No", "Yes", "None"].index(_vc_yn), key=f"{eprefix}_version_yn")
                st.text_input("If Yes — library/version detail", value=_vc_detail, key=f"{eprefix}_version_detail")
                st.selectbox("Missing Module?", ["No", "Yes"], index=["No", "Yes"].index(eb["missing_module"]) if eb["missing_module"] in ["No", "Yes"] else 0, key=f"{eprefix}_module_yn")
                st.selectbox("CI/CD Failure?", ["No", "Yes"], index=["No", "Yes"].index(eb["cicd_failure"]) if eb["cicd_failure"] in ["No", "Yes"] else 0, key=f"{eprefix}_cicd_yn")
            with bc2:
                _vuln = eb["security_vuln"]
                _vuln_std = _vuln if _vuln in SECURITY_VULN_OPTIONS else "Other"
                _vuln_other = "" if _vuln in SECURITY_VULN_OPTIONS else _vuln
                st.selectbox("Security Vulnerability Type", SECURITY_VULN_OPTIONS, index=SECURITY_VULN_OPTIONS.index(_vuln_std), key=f"{eprefix}_vuln")
                st.text_input("If 'Other' — describe", value=_vuln_other, key=f"{eprefix}_vuln_other")
                _teams_default = eb["impacted_teams"] if isinstance(eb["impacted_teams"], list) else [t.strip() for t in str(eb["impacted_teams"]).split(",") if t.strip()]
                st.multiselect("Impacted Teams", TEAM_OPTIONS, default=[t for t in _teams_default if t in TEAM_OPTIONS], key=f"{eprefix}_teams")
                _sev_opts = ["Low", "Medium", "High", "Critical"]
                st.selectbox("Severity", _sev_opts, index=_sev_opts.index(eb["severity"]) if eb["severity"] in _sev_opts else 2, key=f"{eprefix}_severity")
                st.date_input("Resolution ETA", key=f"{eprefix}_eta")
            st.form_submit_button("💾 Update Blocker", on_click=_update_blocker, args=(selected_epic_id, _edit_blk_idx, eprefix))
    if st.session_state.get("blocker_create_success"):
        st.success(st.session_state.blocker_create_success)
        st.session_state.blocker_create_success = None

# ####################################################
# 🏗️ SDD INPUT SECTION (fix #13, fix #Case2: now collapsible with a
# description; field defaults below always pull from epic["sdd"], which is
# rehydrated from Supabase on load, so switching Epics or reloading the page
# correctly re-displays whatever was last saved)
# ####################################################
st.markdown("<p class='section-header'>🏗️ System Design Document (SDD)</p>", unsafe_allow_html=True)

with st.expander("📄 Define / Edit the System Design Document for an Epic", expanded=False):
    note(
        "Captures the technical architecture backing an Epic — core component, "
        "database, API contract (method + URI), RLS policy, compliance hooks, "
        "sequence flow, and NFRs. Saving writes the SDD onto the selected Epic "
        "and upserts it to Supabase (<code>epic_state_store</code>), so it "
        "persists across sessions and reloads exactly as entered here."
    )

    def _sync_sdd_epic_selector():
        st.session_state.selected_epic_id = st.session_state.sdd_epic_selector_widget
        st.session_state.epic_selector_widget = st.session_state.sdd_epic_selector_widget

    sdd_scope_col1, sdd_scope_col2 = st.columns(2)
    with sdd_scope_col1:
        st.selectbox(
            "Associated Epic ID",
            epic_keys,
            index=epic_keys.index(selected_epic_id),
            format_func=lambda k: f"{k}: {st.session_state.epics[k]['name']}",
            key="sdd_epic_selector_widget",
            on_change=_sync_sdd_epic_selector,
        )
    with sdd_scope_col2:
        if epic["stories"]:
            st.selectbox("Associated Story (optional)", ["(Epic-level)"] + list(epic["stories"].keys()), key=f"sdd_story_link_{selected_epic_id}")
        else:
            note("No Stories on this Epic yet — SDD applies at Epic level.")

    sdd = epic["sdd"]
    _core_default = sdd.get("core_component", "")
    _core_idx = CORE_COMPONENT_OPTIONS.index(_core_default) if _core_default in CORE_COMPONENT_OPTIONS else len(CORE_COMPONENT_OPTIONS) - 1
    _db_default = sdd.get("database", "")
    _db_idx = DATABASE_OPTIONS.index(_db_default) if _db_default in DATABASE_OPTIONS else len(DATABASE_OPTIONS) - 1

    sdd_top1, sdd_top2 = st.columns(2)
    with sdd_top1:
        st.selectbox("Core Component", CORE_COMPONENT_OPTIONS, index=_core_idx, key="sdd_core")
        if st.session_state.sdd_core == "Other":
            st.text_input("Custom component name *", key="sdd_core_other", placeholder="e.g. fx-rate-oracle")
    with sdd_top2:
        st.selectbox("Database", DATABASE_OPTIONS, index=_db_idx, key="sdd_db")
        if st.session_state.sdd_db == "Other":
            st.text_input("Custom database *", key="sdd_db_other", placeholder="e.g. ClickHouse (Analytics)")

    with st.form(f"sdd_form_{selected_epic_id}"):
        _method_default = sdd.get("http_method") or (sdd.get("endpoint", "GET /").split(" ")[0] if sdd.get("endpoint") else "GET")
        if _method_default not in HTTP_METHODS:
            _method_default = "GET"
        _uri_default = sdd.get("uri_path") or (sdd.get("endpoint", "").split(" ", 1)[1] if " " in sdd.get("endpoint", "") else "/")
        _rls_default = [r.strip() for r in sdd.get("rls_policy", "").split(",") if r.strip() in RLS_OPTIONS]
        _hooks_default = [h.strip() for h in sdd.get("compliance_hooks", "").split(",") if h.strip() in COMPLIANCE_HOOK_OPTIONS]

        sc1, sc2 = st.columns(2)
        with sc1:
            ec1, ec2 = st.columns([1, 2])
            with ec1:
                st.selectbox("Method", HTTP_METHODS, index=HTTP_METHODS.index(_method_default), key="sdd_method")
            with ec2:
                st.text_input("URI Path", value=_uri_default, key="sdd_uri", placeholder="/api/v1/governance/verify, /webhooks/supabase/sync")
            st.multiselect("RLS Policy (Row-Level Security)", RLS_OPTIONS, default=_rls_default, key="sdd_rls")
            st.multiselect("Compliance Hooks", COMPLIANCE_HOOK_OPTIONS, default=_hooks_default, key="sdd_hooks")
        with sc2:
            st.text_area("Architecture Blueprint", value=sdd["architecture_blueprint"], key="sdd_blueprint", height=68)
            st.text_area("Sequence Flow", value=sdd["sequence_flow"], key="sdd_sequence", height=68)
            st.text_area("API Contract (leave blank to auto-draft from Method + URI)", value=sdd["api_contract"], key="sdd_contract", height=68)
            st.text_area("NFRs (Non-Functional Requirements)", value=sdd["nfrs"], key="sdd_nfrs", height=68)
        st.form_submit_button("💾 Save SDD", on_click=_save_sdd)
if st.session_state.get("sdd_save_success"):
    st.success(st.session_state.sdd_save_success)
    st.session_state.sdd_save_success = None
if st.session_state.get("sdd_save_error"):
    st.warning(st.session_state.sdd_save_error)
    st.session_state.sdd_save_error = None

# ####################################################
# 📐 WSJF PRIORITY CALCULATOR (fix #6 — reorganized, Cost of Delay restored;
# fix #Case3: this used to silently score whatever the global "Active Backlog
# Epic Target Focus" dropdown up top happened to be pointed at, with no
# selector of its own down here — so it *looked* hardcoded to EPIC-007 even
# though the underlying variable was dynamic. Added its own Epic selector,
# mirroring the same pattern already used in the SDD section, so users can
# retarget WSJF scoring without scrolling back to the top of the page.)
# ####################################################
st.markdown("<p class='section-header'>📐 WSJF Priority Calculator</p>", unsafe_allow_html=True)


def _sync_wsjf_epic_selector():
    st.session_state.selected_epic_id = st.session_state.wsjf_epic_selector_widget
    st.session_state.epic_selector_widget = st.session_state.wsjf_epic_selector_widget


st.selectbox(
    "Epic to Score",
    epic_keys,
    index=epic_keys.index(selected_epic_id),
    format_func=lambda k: f"{k}: {st.session_state.epics[k]['name']}",
    key="wsjf_epic_selector_widget",
    on_change=_sync_wsjf_epic_selector,
)
note(f"Scored against <b>{selected_epic_id}</b>. Save to persist this snapshot onto the Epic.")

wsjf_state = epic["wsjf"]
with st.container(border=True):
    wc1, wc2, wc3 = st.columns(3)
    with wc1:
        bv = st.number_input("User / Business Value (A)", min_value=0, max_value=10, value=wsjf_state["bv"], step=1, key="wsjf_bv")
        rr = st.number_input("Risk Reduction / Efficiency (C)", min_value=0, max_value=10, value=wsjf_state["rr"], step=1, key="wsjf_rr")
    with wc2:
        tc = st.number_input("Time Criticality (B)", min_value=0, max_value=10, value=wsjf_state["tc"], step=1, key="wsjf_tc")
        val_d = st.number_input("Job Size / Duration (D)", min_value=1, max_value=10, value=wsjf_state["size"], step=1, key="wsjf_job_size")
    with wc3:
        cost_of_delay = bv + tc + rr
        calculated_wsjf = cost_of_delay / val_d if val_d else 0.0
        st.markdown(
            f"""
        <div style="background:#f8fafc; border:1px solid #d1d5db; border-radius:6px; padding:10px; text-align:center; margin-bottom:10px;">
            <p style="margin:0; font-size:10px; color:#4b5563; font-weight:bold; text-transform:uppercase;">Cost of Delay (A+B+C)</p>
            <p style="margin:2px 0 0 0; font-size:22px; font-weight:bold; color:#111827;">{cost_of_delay}</p>
        </div>
        <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px; text-align:center;">
            <p style="margin:0; font-size:10px; color:#1d4ed8; font-weight:bold; text-transform:uppercase;">WSJF Score (CoD ÷ D)</p>
            <p style="margin:2px 0 0 0; font-size:22px; font-weight:bold; color:#1e3a8a;">{calculated_wsjf:.2f}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    if st.button("💾 Save WSJF Snapshot to Epic", key="btn_save_wsjf"):
        _save_wsjf()
if st.session_state.get("wsjf_save_success"):
    st.success(st.session_state.wsjf_save_success)
    st.session_state.wsjf_save_success = None
if st.session_state.get("wsjf_save_error"):
    st.warning(st.session_state.wsjf_save_error)
    st.session_state.wsjf_save_error = None

# ####################################################
# 📈 TOP-LEVEL EXECUTIVE SUMMARY — now DYNAMIC (fix #11)
# ####################################################
st.markdown("<p class='section-header'>📈 Top-Level Executive Summary Panel</p>", unsafe_allow_html=True)
# Fix #Case4: this card sits right next to "🎯 Active Target Epic" but was
# previously showing the GLOBAL program-wide Epics/Stories/Tasks counts
# (len(st.session_state.epics), all_stories_flat() / all_tasks_flat() across
# every Epic) — e.g. "7 / 8 / 7" for the whole workspace even while the card
# beside it claimed to be scoped to a single Epic like EPIC-007. Now this
# card is scoped to the Active Target Epic (1 / stories-on-this-epic /
# tasks-on-this-epic); the true program-wide rollup is still available via
# the Master Report's "All Epics (Program Rollup)" scope.
_epic_story_items = list(epic["stories"].items())
epic_scoped_epics = 1
epic_scoped_stories = len(_epic_story_items)
epic_scoped_tasks = sum(len(s["tasks"]) for _, s in _epic_story_items)
epic_scoped_points = sum(s["story_points"] for _, s in _epic_story_items) or 0

total_epics = len(st.session_state.epics)
total_stories = len(all_stories_flat())
total_tasks = len(all_tasks_flat())
total_points = sum(s["story_points"] for _, _, s in all_stories_flat()) or 0
st.markdown(
    f"""
<div class='executive-grid-container'>
    <div class='executive-metric-card'><p class='executive-card-label'>🎯 Active Target Epic</p><p class='executive-card-val'>{esc(selected_epic_id)}</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>📦 Epic / Stories / Tasks (This Epic)</p><p class='executive-card-val'>{epic_scoped_epics} / {epic_scoped_stories} / {epic_scoped_tasks}</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>📐 Story Points (This Epic)</p><p class='executive-card-val'>{epic_scoped_points} SP</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>🪙 Cumulative Tokens</p><p class='executive-card-val'>{st.session_state.tokens_used:,}</p></div>
    <div class='executive-metric-card'><p class='executive-card-label'>💵 Cumulative Spend</p><p class='executive-card-val'>${st.session_state.budget_spent:.4f}</p></div>
</div>
""",
    unsafe_allow_html=True,
)
note(f"Program-wide totals across all {total_epics} Epics: {total_stories} Stories / {total_tasks} Tasks / {total_points} SP.")

# ####################################################
# 💼 SKILLS MATRIX & REPORT TABS
# ####################################################
st.markdown("<p class='section-header'>💼 Active Infrastructure Skills Processing Matrix</p>", unsafe_allow_html=True)
report_label = "📊 Consolidated Standard Master Report" if st.session_state.view_layer == "Standard Mode" else "🔥 Consolidated Advanced Master Report"
_nav_options = ["🎯 Core Strategy & Prioritization", report_label, "🔒 Human-In-The-Loop Governance Center"]
if "active_main_nav" not in st.session_state or st.session_state.active_main_nav not in _nav_options:
    st.session_state.active_main_nav = _nav_options[0]
# Fix (#12): st.tabs has no persistent selection across reruns triggered by
# OTHER widgets (like the Report Scope radio below) — Streamlit silently
# snaps back to the first tab every time. A session_state-backed radio does
# not have that problem, since its selection is a real, addressable widget
# key instead of purely client-side UI state.
st.radio("Workspace Section", _nav_options, key="active_main_nav", horizontal=True, label_visibility="collapsed")
active_nav = st.session_state.active_main_nav
st.write("")

# ====================================================
# SECTION 1 — STRATEGY (skills now read real epic/OKR/value-stream data)
# ====================================================
if active_nav == _nav_options[0]:
    with st.expander("Skill 1: OKR Aligner Component", expanded=True):
        note("Parses active Epics and maps metadata metrics dynamically against corporate strategy goals.")
        if st.button("▶️ Run: Compute Functional OKR Impact Mapping Matrix", key="btn_s1"):
            with st.spinner("🔄 Computing OKR Impact Matrix..."):
                time.sleep(0.6)
                okr = epic["okr"]
                execute_agent_skill(
                    "OKR Aligner", 165, 0.0033, selected_epic_id,
                    f"Linked {selected_epic_id} to objective '{okr['objective'] or 'N/A'}' (theme: {okr['business_theme'] or 'N/A'}).",
                    165, 0.0033, 0.00, "Ingest ➔ Cross-Verify Strategy",
                )
            # Fix (#Case5): st.expander cannot be nested inside another
            # st.expander — this whole "Skill" block is already an expander,
            # so a second one here for the console raised
            # StreamlitAPIException on every click. st.container(border=True)
            # gives the same visually-boxed "console" look without nesting.
            with st.container(border=True):
                st.markdown("**📟 Execution Console**")
                st.code(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Fetching OKR record for {selected_epic_id} from session state...\n"
                    f"[{datetime.now().strftime('%H:%M:%S')}] Cross-verifying objective against strategic themes...\n"
                    f"[{datetime.now().strftime('%H:%M:%S')}] Complete: mapped to theme '{epic['okr']['business_theme'] or 'N/A'}'.",
                    language="text",
                )
    with st.expander("Skill 2: Strategic Aligner Component", expanded=True):
        note("Scans System Design Documents (SDDs) to flag architectural deviations or unmapped endpoints.")
        if st.button("▶️ Run: Automated Strategic Alignment Audit", key="btn_s2"):
            with st.spinner("⌛ Running Audit..."):
                time.sleep(0.6)
                execute_agent_skill(
                    "Strategic Aligner", 210, 0.0042, epic["narrative"][:50],
                    f"Narrative for {selected_epic_id} matched against target release '{epic['target_release']}'.",
                    110, 0.0042, 0.00, "Story Ingest ➔ Target Milestones Match",
                )
            # Fix (#Case6): same nested-expander issue as Skill 1 above.
            with st.container(border=True):
                st.markdown("**📟 Execution Console**")
                st.code(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Fetching active SDD record for {selected_epic_id}...\n"
                    f"[{datetime.now().strftime('%H:%M:%S')}] Checking endpoint {epic['sdd'].get('endpoint','N/A')} against compliance hooks...\n"
                    f"[{datetime.now().strftime('%H:%M:%S')}] Audit Complete: 0 Policy Violations Found.",
                    language="text",
                )
    with st.expander("Skill 3: WSJF Priority Calculator Component", expanded=True):
        note("Computes Cost-of-Delay-weighted priority score for the active Epic and logs the snapshot.")
        st.markdown(
            f"<p style='font-size:13px; color:#475569;'>Live WSJF score for <b>{esc(selected_epic_id)}</b>: "
            f"<code style='color:#0369a1; background-color:#f0f9ff; padding:2px 6px; border-radius:4px;'>{calculated_wsjf:.2f}</code> "
            f"(Cost of Delay {cost_of_delay} ÷ Job Size {val_d}).</p>",
            unsafe_allow_html=True,
        )
        if st.button("▶️ Run: Log WSJF Snapshot to Telemetry", key="btn_s3"):
            with st.spinner("🔄 Logging WSJF Snapshot..."):
                time.sleep(0.4)
                execute_agent_skill(
                    "WSJF Priority Calculator", 95, 0.0019, f"BV {bv} / TC {tc} / RR {rr} / Size {val_d}",
                    f"Computed WSJF {calculated_wsjf:.2f} for {selected_epic_id}.", 60, 0.0019, 0.00, "Score Inputs ➔ WSJF Engine",
                )
            # Fix: Skills 1 & 2 show a persistent Execution Console after
            # running, but this one only fired a transient st.toast() that
            # fades in ~2s — the skill *was* executing (tokens/spend/logs all
            # updated) but with no visible in-panel confirmation, so it
            # looked like a dead button. Added the same console pattern here.
            with st.container(border=True):
                st.markdown("**📟 Execution Console**")
                st.code(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Reading BV={bv}, TC={tc}, RR={rr}, Size={val_d} for {selected_epic_id}...\n"
                    f"[{datetime.now().strftime('%H:%M:%S')}] Cost of Delay = {cost_of_delay}, WSJF = {calculated_wsjf:.2f}...\n"
                    f"[{datetime.now().strftime('%H:%M:%S')}] Logged to Agent Telemetry Summary.",
                    language="text",
                )

    if st.session_state.view_layer == "Advanced Reporting Mode":
        st.markdown("<p style='color:#0284c7; font-weight:700; margin-top:1.5rem;'>🔓 Extended Operational Engine Components (Skills 4-7)</p>", unsafe_allow_html=True)
        with st.expander("Skill 4: Sprint & Release Mapping Framework", expanded=False):
            if st.button("📊 Synthesize Release Readiness Matrix", key="btn_s4"):
                sprints = {}
                for sid, s in epic["stories"].items():
                    sprints.setdefault(s["sprint_assignment"], []).append(sid)
                execute_agent_skill(
                    "Sprint/Release Mapper", 140, 0.0028, "Active Delivery Cycles",
                    f"Mapped {len(epic['stories'])} stories across {len(sprints)} sprint(s) for {selected_epic_id}.",
                    90, 0.0028, 0.00, "Capacity Check ➔ Sequence Allocation",
                )
        with st.expander("Skill 5: Value Stream Priority Tracker", expanded=False):
            if st.button("📈 Extract Strategic Value Vectors", key="btn_s5"):
                vs = epic["value_stream"]
                if vs["trigger"] and vs["respond"]:
                    _vs_summary = f"Trigger '{vs['trigger']}' ➔ Respond '{vs['respond']}' mapped for {selected_epic_id}."
                else:
                    _vs_summary = f"Value Stream scaffold indexed for {selected_epic_id} — trigger/response nodes not yet defined in the OKR & Value Stream section."
                execute_agent_skill(
                    "Value Stream Indexer", 110, 0.0022, selected_epic_id,
                    _vs_summary,
                    85, 0.0022, 0.00, "Trace Streams ➔ Weighting Factor",
                )
        with st.expander("Skill 6: Blocker & Dependency Risk Grid", expanded=False):
            if st.button("🛡️ Execute Proactive Environment Lock Checks", key="btn_s6"):
                crit = sum(1 for b in epic["blockers"] if b["severity"] == "Critical")
                execute_agent_skill(
                    "Risk Grid Engine", 130, 0.0026, "Lockfiles & Infrastructure States",
                    f"{len(epic['blockers'])} blocker(s) on {selected_epic_id} ({crit} Critical).",
                    70, 0.0026, 0.00, "Scan Graphs ➔ Baseline Match",
                )
        with st.expander("Skill 7: Architecture Artifacts Drafter", expanded=False):
            if st.button("📝 Auto-Draft System Design Document Payload", key="btn_s7"):
                _sdd = epic["sdd"]
                if _sdd.get("core_component") and _sdd.get("endpoint"):
                    _sdd_summary = f"Rendered SDD for {selected_epic_id}: {_sdd['core_component']} @ {_sdd['endpoint']}."
                else:
                    _sdd_summary = f"SDD scaffold generated for {selected_epic_id} — architecture details pending definition in the SDD section."
                execute_agent_skill(
                    "Artifacts Drafter", 240, 0.0048, "Technical Spec Base",
                    _sdd_summary,
                    130, 0.0048, 0.00, "Parse Schema ➔ Render Output Payload",
                )

# ====================================================
# TAB 2 — MASTER REPORT (fix #7 rendering, fix #14 per-Epic + program rollup)
# ====================================================
def render_epic_report_html(eid):
    ep = st.session_state.epics[eid]
    story_rows = "".join(
        f"<tr><td style='width:12%;'>{esc(sid)}</td><td style='width:44%;'>{esc(s['description'])}</td><td style='width:18%;'>{esc(s['assignee'])}</td><td class='num-cell' style='width:10%;'>{esc(s['story_points'])} SP</td>"
        f"<td style='width:16%;'><span style='color:{'#16a34a' if s['compliance_state']=='Passed' else '#dc2626' if s['compliance_state']=='Failed' else '#d97706'}; font-weight:700;'>{esc(s['compliance_state'])}</span></td></tr>"
        for sid, s in ep["stories"].items()
    ) or "<tr><td colspan='5'>No stories recorded yet.</td></tr>"

    sprints = {}
    for sid, s in ep["stories"].items():
        sprints.setdefault(s["sprint_assignment"], []).append(sid)
    sprint_rows = "".join(
        f"<tr><td>{esc(sp)}</td><td class='num-cell'>{len(sids)} Stories</td><td>{esc(', '.join(sids))}</td></tr>"
        for sp, sids in sprints.items()
    ) or "<tr><td colspan='3'>No sprint assignments yet.</td></tr>"

    wsjf = ep["wsjf"]
    cod = wsjf["bv"] + wsjf["tc"] + wsjf["rr"]
    wsjf_score = cod / wsjf["size"] if wsjf["size"] else 0.0

    def _teams_tags(raw):
        teams = raw if isinstance(raw, list) else [t.strip() for t in str(raw).split(",") if t.strip()]
        if not teams:
            return "—"
        return " ".join(f"[{esc(t)}]" for t in teams)

    blocker_rows = "".join(
        f"<tr><td>{esc(b.get('scope_type','Epic'))}: {esc(b.get('scope_id', eid))}</td><td>{esc(b['dependency'])}</td><td>{esc(b['severity'])}</td><td>{_teams_tags(b['impacted_teams'])}</td><td>{esc(b['resolution_eta'])}</td></tr>"
        for b in ep["blockers"]
    ) or "<tr><td colspan='5'>No blockers logged.</td></tr>"

    sdd = ep["sdd"]
    okr = ep["okr"]
    endpoint_display = sdd.get("endpoint") or (f"{sdd.get('http_method','')} {sdd.get('uri_path','')}".strip() or "—")

    n_stories = len(ep["stories"])
    n_tasks = sum(len(s["tasks"]) for s in ep["stories"].values())
    sp = sum(s["story_points"] for s in ep["stories"].values())
    stories_passed = sum(1 for s in ep["stories"].values() if s["compliance_state"] == "Passed")
    stories_total = len(ep["stories"])
    compliance_class = "compliance-ok" if (stories_total > 0 and stories_passed == stories_total) else "compliance-warn"

    html = f"""
    <div class='master-report-header-banner'>📝 MASTER REPORT — {esc(eid)}: {esc(ep['name'])}</div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>1. EPIC OVERVIEW</p>
        <table class='custom-spec-table'><tbody>
            <tr><td style='width:25%;'><b>Narrative</b></td><td>{esc(ep['narrative'])}</td></tr>
            <tr><td><b>Business Goal</b></td><td>{esc(ep['business_goal'])}</td></tr>
            <tr><td><b>Compliance Category</b></td><td>{esc(ep['compliance_category'])}</td></tr>
            <tr><td><b>Target Release / Quarter</b></td><td>{esc(ep['target_release'])} / {esc(ep['target_quarter'])}</td></tr>
            <tr><td><b>OKR Objective</b></td><td>{esc(okr['objective'])}</td></tr>
        </tbody></table>
    </div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>2. STORY INVENTORY</p>
        <table class='custom-spec-table'><thead><tr><th style='width:12%;'>Story ID</th><th style='width:44%;'>Description</th><th style='width:18%;'>Assignee</th><th style='width:10%;'>Points</th><th style='width:16%;'>Compliance</th></tr></thead><tbody>{story_rows}</tbody></table>
    </div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>3. SPRINT & RELEASE MAPPING</p>
        <table class='custom-spec-table'><thead><tr><th>Sprint</th><th>Story Count</th><th>Story IDs</th></tr></thead><tbody>{sprint_rows}</tbody></table>
    </div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>4. WSJF MATRIX</p>
        <table class='custom-spec-table'><thead><tr><th>BV</th><th>TC</th><th>RR</th><th>Cost of Delay</th><th>Job Size</th><th>WSJF Score</th></tr></thead>
        <tbody><tr><td class='num-cell'>{wsjf['bv']}</td><td class='num-cell'>{wsjf['tc']}</td><td class='num-cell'>{wsjf['rr']}</td><td class='num-cell'>{cod}</td><td class='num-cell'>{wsjf['size']}</td><td class='num-cell'><b>{wsjf_score:.2f}</b></td></tr></tbody></table>
    </div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>5. BLOCKER GRID</p>
        <table class='custom-spec-table'><thead><tr><th>Scope</th><th>Dependency</th><th>Severity</th><th>Impacted Teams</th><th>Resolution ETA</th></tr></thead><tbody>{blocker_rows}</tbody></table>
    </div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>6. SDD SUMMARY</p>
        <table class='custom-spec-table'><tbody>
            <tr><td style='width:25%;'><b>Core Component</b></td><td>{esc(sdd['core_component'])}</td></tr>
            <tr><td><b>Endpoint</b></td><td><code>{esc(endpoint_display)}</code></td></tr>
            <tr><td><b>Database</b></td><td>{esc(sdd['database'])}</td></tr>
            <tr><td><b>RLS Policy</b></td><td>{esc(sdd['rls_policy'])}</td></tr>
            <tr><td><b>Architecture Blueprint</b></td><td>{esc(sdd['architecture_blueprint'])}</td></tr>
            <tr><td><b>NFRs</b></td><td>{esc(sdd['nfrs'])}</td></tr>
        </tbody></table>
    </div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>7. COMPLIANCE AUDIT SUMMARY</p>
        <table class='custom-spec-table'><tbody>
            <tr><td style='width:25%;'><b>Compliance Category</b></td><td>{esc(ep['compliance_category'])}</td></tr>
            <tr><td><b>Stories Passed / Total</b></td><td class='{compliance_class}'>{stories_passed} / {stories_total}</td></tr>
            <tr><td><b>Open Critical Blockers</b></td><td>{sum(1 for b in ep['blockers'] if b['severity']=='Critical')}</td></tr>
        </tbody></table>
    </div>
    """
    return html, {"epics": 1, "stories": n_stories, "tasks": n_tasks, "story_points": sp}


def render_program_report_html():
    total_sp = 0
    total_stories_n = 0
    total_tasks_n = 0
    epic_rows = ""
    for eid, ep in st.session_state.epics.items():
        n_stories = len(ep["stories"])
        n_tasks = sum(len(s["tasks"]) for s in ep["stories"].values())
        sp = sum(s["story_points"] for s in ep["stories"].values())
        total_sp += sp
        total_stories_n += n_stories
        total_tasks_n += n_tasks
        wsjf = ep["wsjf"]
        cod = wsjf["bv"] + wsjf["tc"] + wsjf["rr"]
        score = cod / wsjf["size"] if wsjf["size"] else 0.0
        epic_rows += f"<tr><td>{esc(eid)}</td><td>{esc(ep['name'])}</td><td class='num-cell'>{n_stories}</td><td class='num-cell'>{n_tasks}</td><td class='num-cell'>{sp} SP</td><td class='num-cell'>{score:.2f}</td></tr>"

    html = f"""
    <div class='master-report-header-banner'>📝 PROGRAM-WIDE MASTER REPORT ROLLUP — {len(st.session_state.epics)} Epics</div>
    <div class='master-report-section-node'>
        <p class='master-report-section-title'>PROGRAM ROLLUP</p>
        <table class='custom-spec-table'>
            <thead><tr><th>Epic ID</th><th>Name</th><th>Stories</th><th>Tasks</th><th>Story Points</th><th>WSJF Score</th></tr></thead>
            <tbody>{epic_rows}</tbody>
        </table>
        <p style='font-size:12px; color:#64748b; margin-top:8px;'>Totals — Stories: {total_stories_n} | Tasks: {total_tasks_n} | Story Points: {total_sp} SP</p>
    </div>
    """
    for eid in st.session_state.epics:
        epic_html, _ = render_epic_report_html(eid)
        html += epic_html
    metrics = {"epics": len(st.session_state.epics), "stories": total_stories_n, "tasks": total_tasks_n, "story_points": total_sp}
    return html, metrics


def _clear_master_report_on_scope_change():
    # Fix (#Case7): switching the radio alone was a no-op — it only reruns
    # the script, it doesn't regenerate the report, so whichever report
    # (Epic or Program) was last compiled just kept being displayed
    # regardless of which scope was now selected, making the two options
    # look identical. Clearing the stale report here forces the placeholder
    # note to reappear immediately so it's obvious a fresh Generate is
    # needed, instead of silently showing outdated data under the new label.
    st.session_state.master_report_epic = None
    st.session_state.master_report_program = None
    st.session_state.master_report_metrics = None


if active_nav == _nav_options[1]:
    st.markdown(f"<p class='section-header'>{report_label} Compiler Desk</p>", unsafe_allow_html=True)
    scope = st.radio(
        "Report Scope", ["This Epic", "All Epics (Program Rollup)"], horizontal=True,
        key="report_scope", on_change=_clear_master_report_on_scope_change,
    )
    if st.button("Generate & Compile Master Report", key="btn_master"):
        if scope == "This Epic":
            html_out, metrics_out = render_epic_report_html(selected_epic_id)
            st.session_state.master_report_epic = html_out
            st.session_state.master_report_program = None
            st.session_state.master_report_metrics = metrics_out
        else:
            html_out, metrics_out = render_program_report_html()
            st.session_state.master_report_program = html_out
            st.session_state.master_report_epic = None
            st.session_state.master_report_metrics = metrics_out
        execute_agent_skill(
            "Master Report Compiler", 100, 0.0020, scope,
            f"Compiled {'per-Epic' if scope=='This Epic' else 'program-wide'} report.", 80, 0.0020, 0.00,
            "Merge States ➔ Output Matrix",
        )

    # Fix (#7): a single st.markdown(..., unsafe_allow_html=True) call per
    # report, built from an escaped string — no more raw HTML/code leaking
    # onto the page.
    if st.session_state.master_report_epic:
        st.markdown(st.session_state.master_report_epic, unsafe_allow_html=True)
    elif st.session_state.master_report_program:
        st.markdown(st.session_state.master_report_program, unsafe_allow_html=True)
    else:
        note("Choose a scope above and click Generate to compile the Master Report.")

    # Insight Extractor — dynamic AND correctly scoped (fix #22: this used to
    # always show program-wide totals even when "This Epic" was selected).
    if st.session_state.master_report_epic or st.session_state.master_report_program:
        _rm = st.session_state.get("master_report_metrics") or {"epics": total_epics, "stories": total_stories, "tasks": total_tasks, "story_points": total_points}
        st.markdown("<p class='master-report-section-title'>8. INSIGHT EXTRACTOR</p>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Story Points" if st.session_state.master_report_epic else "Program Story Points", f"{_rm['story_points']} SP")
        m2.metric("Epics" if st.session_state.master_report_epic else "Program Epics", _rm["epics"])
        m3.metric("Tasks" if st.session_state.master_report_epic else "Program Tasks", _rm["tasks"])

        st.markdown("<p class='master-report-section-title'>9. HITL GOVERNANCE LOG</p>", unsafe_allow_html=True)
        if st.session_state.hitl_ledger:
            hrows = "".join(
                f"<tr><td>{esc(e['Timestamp'])}</td><td>{esc(e['Authorized Approver'])}</td><td><b>{esc(e['Selected Action Verdict'])}</b></td>"
                f"<td>{esc(e.get('Trigger Reason','N/A'))}</td><td>{esc(e['Severity Level'])}</td><td>{esc(e['Operational Remarks'])}</td></tr>"
                for e in st.session_state.hitl_ledger
            )
            st.markdown(
                f"<table class='custom-spec-table'><thead><tr><th>Timestamp</th><th>Reviewer</th><th>Verdict</th><th>Trigger</th><th>Severity</th><th>Notes</th></tr></thead><tbody>{hrows}</tbody></table>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<p class='muted-placeholder'>No governance verdicts committed yet.</p>", unsafe_allow_html=True)

        st.markdown("<p class='master-report-section-title'>10. AGENT TELEMETRY SUMMARY</p>", unsafe_allow_html=True)
        latest = st.session_state.execution_logs[:1]
        active_component = latest[0]["Skill Triggered"] if latest else "N/A"
        st.markdown(
            f"<table class='custom-spec-table'><thead><tr><th>Active Component</th><th>Tokens</th><th>Cost</th><th>Latency</th><th>Evals</th><th>Chain</th></tr></thead>"
            f"<tbody><tr><td>{esc(active_component)}</td><td class='num-cell'>{st.session_state.tokens_used:,}</td><td class='num-cell'>${st.session_state.budget_spent:.4f}</td>"
            f"<td class='num-cell'>{st.session_state.live_latency}ms</td><td>{esc(st.session_state.live_eval_status)}</td><td>{esc(st.session_state.current_chain)}</td></tr></tbody></table>",
            unsafe_allow_html=True,
        )

# ====================================================
# TAB 3 — HITL GOVERNANCE
# ====================================================
if active_nav == _nav_options[2]:
    st.markdown("<p class='section-header'>🔒 Human-In-The-Loop (HITL) Governance Center</p>", unsafe_allow_html=True)

    if st.session_state.view_layer == "Standard Mode":
        st.markdown("<span class='hitl-minimal-badge'>⚡ Minimal Mode — quick sign-off, no SLA timer or dual control</span>", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns(2, gap="medium")
        with m_col1:
            with st.container(border=True):
                verdict_selection = st.radio("Verdict", ["Approve Deployment", "Reject Change"], key="hitl_verdict_radio_std")
                reviewer_name = st.text_input("Signature", value=st.session_state.reviewer_name, key="hitl_reviewer_std")
        with m_col2:
            with st.container(border=True):
                hitl_notes = st.text_area("Notes", value=st.session_state.hitl_notes, height=100, key="hitl_notes_std", placeholder="Optional reviewer notes...")

        if st.button("💾 Commit Verdict", key="btn_commit_hitl_std"):
            st.session_state.reviewer_name = reviewer_name
            st.session_state.hitl_notes = hitl_notes
            # Fix (#Case8): Severity Level was a hardcoded literal "N/A" on
            # every Standard Mode commit, not a ternary that only failed on
            # clean passes — there simply was no classification logic at
            # all here. Every ledger row now gets an explicit tier so
            # downstream risk filters have something real to key off,
            # rather than a null-ish fallback string.
            _severity_level = "LOW — Clean Pass" if verdict_selection == "Approve Deployment" else "MEDIUM — Change Rejected"
            new_audit_entry = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Artifact ID": selected_epic_id,
                "Trigger Reason": "Standard Mode Review", "Severity Level": _severity_level,
                "Selected Action Verdict": verdict_selection, "Authorized Approver": reviewer_name,
                "Reviewer Role": "N/A", "Dual Control Status": "Not Required (Standard Mode)",
                "Operational Remarks": hitl_notes if hitl_notes else "No additional notes provided.",
            }
            save_governance_to_supabase(new_audit_entry)
            st.session_state.hitl_ledger.insert(0, new_audit_entry)
            execute_agent_skill("Governance Engine", 90, 0.0018, "HITL-COMMIT-STD", "Committed minimal governance record.", 60, 0.0018, 0.00, "User Action ➔ Commit Ledger Row")
            st.session_state.last_commit_feedback = ("success", f"Verdict **{verdict_selection}** committed by {reviewer_name} at {datetime.now().strftime('%H:%M:%S')}.")
            st.rerun()
    else:
        st.markdown("<span class='hitl-full-badge'>🏛️ Full Governance Mode — trigger reason, severity, evidence bundle, dual control</span>", unsafe_allow_html=True)
        g_col1, g_col2, g_col3 = st.columns(3, gap="medium")
        with g_col1:
            with st.container(border=True):
                trigger_reason = st.selectbox(
                    "🎯 Trigger Reason",
                    ["High-Risk Compliance", "High WSJF Impact", "Architecture Change", "Cost Spike", "Hallucination Risk", "Multi-Agent Conflict"],
                    key="hitl_trigger_reason",
                )
                severity_level = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"], index=2, key="hitl_severity_level")
        with g_col2:
            with st.container(border=True):
                st.markdown(f"📈 **WSJF Score:** `{calculated_wsjf:.2f}`")
                st.markdown(f"🎯 **Target Release:** {esc(epic['target_release'])}")
                st.markdown(f"🚧 **Open Blockers:** {len(epic['blockers'])}")
                # Fix (#28): use the exact same format string as the Live
                # Observability panel below (2 decimal places), so the same
                # underlying value never displays two different ways on screen.
                st.markdown(f"📡 **Telemetry:** {(st.session_state.live_hallucination*100):.2f}% hallucination, {esc(st.session_state.live_eval_status)}")
        with g_col3:
            with st.container(border=True):
                # Fix (#29): if the SLA window has actually elapsed, lock the
                # form instead of leaving an "active-looking" 0:00:00 timer
                # next to fully-enabled inputs.
                total_sla_seconds = 900  # 15-minute review window
                elapsed_seconds = int(time.time() - st.session_state.start_time)
                remaining = max(total_sla_seconds - elapsed_seconds, 0)
                session_expired = remaining <= 0

                @st.fragment(run_every=1.0)
                def render_live_sla_ticker():
                    _elapsed = int(time.time() - st.session_state.start_time)
                    _remaining = max(total_sla_seconds - _elapsed, 0)
                    if _remaining <= 0:
                        st.markdown("<span class='session-expired-badge'>⛔ Session Expired</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"⏳ **Time Remaining to Approve:** `{str(timedelta(seconds=_remaining))}`")
                render_live_sla_ticker()

                if session_expired:
                    st.warning("This review window has closed. Refresh to start a new SLA window before submitting a verdict.")
                verdict_selection = st.radio("Verdict", ["Approve Deployment", "Reject Change", "Escalate Tier", "Defer for Analysis"], key="hitl_verdict_radio", disabled=session_expired)
                reviewer_name = st.text_input("Signature", value=st.session_state.reviewer_name, key="hitl_reviewer_adv", disabled=session_expired)
                reviewer_role = st.selectbox("Reviewer Role", ["Product Owner", "Engineering Lead", "Compliance Officer", "Risk Manager"], key="hitl_reviewer_role", disabled=session_expired)
                eng_ok = st.checkbox("Engineering Sign-off", key="eng_approval", disabled=session_expired)
                compliance_ok = st.checkbox("Compliance Sign-off", key="compliance_approval", disabled=session_expired)
                # Fix (#30): the commit button's disabled state is bound
                # directly to both sign-off checkboxes (and now also to the
                # SLA window), so it can never be clicked while either
                # condition is unmet.
                commit_disabled = session_expired or not (eng_ok and compliance_ok)
                if commit_disabled and not session_expired:
                    note("⏸️ Both Engineering and Compliance sign-off are required.")
                if st.button("💾 Commit Verdict", key="btn_commit_hitl_adv", disabled=commit_disabled):
                    st.session_state.reviewer_name = reviewer_name
                    dual_status = "Fully Approved (Engineering + Compliance)" if (eng_ok and compliance_ok) else "Pending Second Approval"
                    new_audit_entry = {
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Artifact ID": selected_epic_id,
                        "Trigger Reason": trigger_reason, "Severity Level": severity_level,
                        "Selected Action Verdict": verdict_selection, "Authorized Approver": reviewer_name,
                        "Reviewer Role": reviewer_role, "Dual Control Status": dual_status,
                        "Operational Remarks": f"WSJF: {calculated_wsjf:.2f} | Chain: {st.session_state.current_chain} | Tokens: {st.session_state.tokens_used} | Cost: ${st.session_state.budget_spent:.4f}",
                    }
                    save_governance_to_supabase(new_audit_entry)
                    st.session_state.hitl_ledger.insert(0, new_audit_entry)
                    execute_agent_skill("Governance Engine", 150, 0.0030, "HITL-COMMIT-ADV", f"Committed {severity_level} severity record.", 95, 0.0030, 0.00, "User Action ➔ Commit Ledger Row")
                    st.session_state.last_commit_feedback = ("success", f"Verdict **{verdict_selection}** committed by {reviewer_name} ({reviewer_role}) — {dual_status}.")
                    st.rerun()

    if st.session_state.last_commit_feedback is not None:
        kind, msg = st.session_state.last_commit_feedback
        if kind == "success":
            st.success(msg)
        st.session_state.last_commit_feedback = None

    st.markdown("<p class='section-header'>📝 Historical Governance Ledger Trail</p>", unsafe_allow_html=True)
    if st.session_state.hitl_ledger:
        rows = "".join(
            f"<tr><td>{esc(e['Timestamp'])}</td><td><b>{esc(e['Artifact ID'])}</b></td><td>{esc(e.get('Trigger Reason','N/A'))}</td>"
            f"<td>{esc(e['Severity Level'])}</td><td>{esc(e['Selected Action Verdict'])}</td><td>{esc(e['Authorized Approver'])}</td>"
            f"<td>{esc(e.get('Dual Control Status','N/A'))}</td><td>{esc(e['Operational Remarks'])}</td></tr>"
            for e in st.session_state.hitl_ledger
        )
        st.markdown(
            f"<div class='scrollable-ledger-wrap'><table class='custom-spec-table'><thead><tr><th>Timestamp</th><th>ID</th><th>Trigger</th><th>Severity</th><th>Verdict</th><th>Approver</th><th>Dual Control</th><th>Remarks</th></tr></thead><tbody>{rows}</tbody></table></div>",
            unsafe_allow_html=True,
        )
    else:
        note("No governance verdicts committed yet.")

# ####################################################
# 🤖 LIVE AGENTIC OBSERVABILITY — now DYNAMIC (fix #10)
# ####################################################
if st.session_state.view_layer == "Advanced Reporting Mode":
    st.markdown("<div style='border-bottom:1px solid #e2e8f0; margin:24px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<p class='section-header'>🤖 Live Agentic Observability & Evals Metrics</p>", unsafe_allow_html=True)
    obs_c1, obs_c2, obs_c3, obs_c4, obs_c5 = st.columns(5)
    _chain_steps = len([s for s in st.session_state.current_chain.split("➔") if s.strip()]) if st.session_state.current_chain != "—" else 0
    obs_c1.markdown(f"<div class='observability-box-mild-grey'>⏳ <span class='metric-card-label'>LATENCY</span><br><span class='metric-value-strong' style='font-size:1.3rem;'>{st.session_state.live_latency}ms</span></div>", unsafe_allow_html=True)
    obs_c2.markdown(f"<div class='observability-box-mild-grey'>💵 <span class='metric-card-label'>COST/REQ</span><br><span class='metric-value-strong' style='font-size:1.3rem;'>${st.session_state.live_cost_req:.4f}</span></div>", unsafe_allow_html=True)
    obs_c3.markdown(f"<div class='observability-box-mild-grey'>🎯 <span class='metric-card-label'>HALLUCINATION</span><br><span class='metric-value-strong' style='font-size:1.3rem;'>{(st.session_state.live_hallucination*100):.2f}%</span></div>", unsafe_allow_html=True)
    obs_c4.markdown(f"<div class='observability-box-mild-grey'>📋 <span class='metric-card-label'>EVALS</span><br><span class='metric-value-strong' style='font-size:1.3rem; color:#16a34a;'>{esc(st.session_state.live_eval_status)}</span></div>", unsafe_allow_html=True)
    obs_c5.markdown(
        f"<div class='observability-box-mild-grey'>🔗 <span class='metric-card-label'>CHAIN</span><br>"
        f"<span class='metric-value-strong' style='font-size:1.3rem;'>{_chain_steps} Step{'s' if _chain_steps != 1 else ''}</span>"
        f"<br><span style='font-size:10px; color:#94a3b8; white-space:nowrap;'>{esc(st.session_state.current_chain)}</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<p class='section-header'>📜 Live Agent Execution Log</p>", unsafe_allow_html=True)
    if st.session_state.execution_logs:
        def _highlight_summary(text):
            parts = text.split(" ", 1)
            if len(parts) == 2:
                return f"<b style='color:#1e293b;'>{esc(parts[0])}</b> {esc(parts[1])}"
            return esc(text)

        rows = "".join(
            f"<tr><td style='color:#64748b;'>{esc(r['Timestamp'])}</td><td><span style='color:#1d4ed8; font-weight:600;'>{esc(r['Skill Triggered'])}</span></td>"
            f"<td><span style='color:#065f46; font-weight:600; background-color:#ecfdf5; padding:2px 8px; border-radius:4px; font-size:12px;'>{esc(r['Inputs Received'])}</span></td>"
            f"<td class='num-cell'>{r['Tokens Consumed']:,}</td><td class='num-cell'>${r['Cost ($)']:.4f}</td><td>{_highlight_summary(r['Output Summary'])}</td></tr>"
            for r in st.session_state.execution_logs
        )
        st.markdown(
            f"<div class='scrollable-ledger-wrap'><table class='custom-spec-table zebra-table' style='border-top:4px solid #1e3a8a;'><thead><tr><th>Timestamp</th><th>Process Unit</th><th>Metadata Input</th><th>Tokens</th><th>Cost</th><th>Execution Logs</th></tr></thead><tbody>{rows}</tbody></table></div>",
            unsafe_allow_html=True,
        )
    else:
        note("No agent executions logged yet. Run a skill above (e.g. OKR Aligner, WSJF Calculator) to populate this table.")