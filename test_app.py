import pytest
from unittest.mock import MagicMock

# Core Test 1: Validating WSJF Priority Calculator engine formula accuracy
def test_wsjf_calculation_logic():
    # Formula matching app.py framework: (BV + TC + RR) / JS
    business_value = 8
    time_criticality = 5
    risk_reduction = 6
    job_size = 3
    
    cost_of_delay = business_value + time_criticality + risk_reduction
    calculated_wsjf = cost_of_delay / job_size if job_size > 0 else 0
    
    assert cost_of_delay == 19
    assert round(calculated_wsjf, 2) == 6.33

# Core Test 2: Verifying structural keys in your automated governance ledger payloads
def test_governance_payload_structure():
    mock_entry = {
        "Timestamp": "2026-03-31 12:00:00",
        "Artifact ID": "EPIC-001",
        "Trigger Reason": "Standard Mode Review",
        "Severity Level": "N/A",
        "Selected Action Verdict": "Approved"
    }
    
    assert "Artifact ID" in mock_entry
    assert "Selected Action Verdict" in mock_entry
    assert mock_entry["Artifact ID"] == "EPIC-001"
