import streamlit as st
from datetime import datetime
from supabase import create_client

# 🔌 Pulling live credentials automatically from your secrets.toml file
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

print("🔌 Initializing Supabase Connection using secrets.toml keys...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

mock_governance_data = {
    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Artifact ID": "EPIC-TEST-IDE",
    "Trigger Reason": "Antigravity IDE Script Database Test",
    "Severity Level": "Low Risk",
    "Selected Action Verdict": "Approved Live",
    "Authorized Approver": "Antigravity Terminal Execution",
    "Reviewer Role": "Quality Assurance Engineer",
    "Dual Control Status": "Validated Via Script Payload",
    "Operational Remarks": "Testing live telemetry data pipes before Streamlit integration setup."
}

try:
    print("📤 Pushing test payload row into public.governance_ledger...")
    response = supabase.table("governance_ledger").insert(mock_governance_data).execute()
    print("\n✅ Target insert executed perfectly! Verification Output payload details:")
    print(response.data)
except Exception as error:
    print(f"\n❌ Database insert execution crashed. Debug error logs:\n{error}")
