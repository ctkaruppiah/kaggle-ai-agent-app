-- Simulate an AI Agent Writing an Epic with Nested Stories to your table
INSERT INTO epic_state_store (workspace_key, state_json, updated_at)
VALUES (
  'WORKSPACE-PROD-001',
  '{
    "epic_id": "EPIC-001",
    "title": "Face Match Engine Implementation",
    "stories": [
      {
        "story_id": "STORY-001",
        "description": "OCR Document Extraction",
        "points": 5,
        "compliance": "Passed",
        "tasks": ["TASK-101", "TASK-102"]
      },
      {
        "story_id": "STORY-002",
        "description": "Biometric Liveness Check",
        "points": 8,
        "compliance": "Not Reviewed",
        "tasks": ["TASK-201"]
      }
    ]
  }'::jsonb,
  now()
);

-- Verify the nested payload works
SELECT workspace_key, state_json->>'epic_id' AS extracted_epic_id 
FROM epic_state_store;
