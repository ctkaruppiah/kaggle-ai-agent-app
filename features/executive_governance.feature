Feature: FinMesh Executive Governance Routing
  As an Enterprise Compliance Officer
  I want high-risk code deltas and WSJF metrics verified under dual control
  So that malicious payload risks or code drift are completely mitigated before live execution

  Background:
    Given a valid connection layer to the Supabase database instance is established

  Scenario: Standard governance record logging
    Given the target epic focus is set to "EPIC-001"
    When a user commits a standard mode review verdict
    Then the system must process the transaction through the Governance Engine
    And save the audit entry row securely to the Supabase ledger

  Scenario: Advanced dual-control verification
    Given the compliance review process is running in Advanced Reporting Mode
    When the engineering and compliance sign-offs are both validated
    And a compliance officer commits the final ledger entry
    Then the application must broadcast the payload securely to the live database
