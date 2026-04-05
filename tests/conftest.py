"""Shared test fixtures."""

import pytest
import respx

from hippodid import HippoDid

BASE_URL = "https://api.hippodid.com"
API_KEY = "hd_test_key_123"


@pytest.fixture
def mock_api():
    with respx.mock(base_url=BASE_URL) as api:
        yield api


@pytest.fixture
def client():
    return HippoDid(api_key=API_KEY, base_url=BASE_URL, max_retries=0)


# ── Shared response fixtures ─────────────────────────────────────────────────

CHARACTER_JSON = {
    "id": "c1000000-0000-0000-0000-000000000001",
    "name": "Ada",
    "description": "A test character",
    "externalId": "ext-ada",
    "visibility": "PRIVATE",
    "createdBy": "m1000000-0000-0000-0000-000000000001",
    "profile": {
        "systemPrompt": "You are Ada, a helpful AI assistant.",
        "personality": "Curious and analytical",
        "background": "Created for testing",
        "rules": ["Be helpful", "Be concise"],
        "customFields": {},
    },
    "aliases": [],
    "categories": [
        {
            "name": "general",
            "description": "General memories",
            "extractionHints": [],
            "importance": "NORMAL",
            "halfLifeDays": 0,
            "effectiveHalfLifeDays": 365,
            "retrievalBoost": 1.0,
            "isDefault": True,
            "isEvergreen": False,
            "memoryCount": 5,
        }
    ],
    "agentConfig": {
        "systemPrompt": "You are Ada.",
        "preferredModel": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "maxTokens": 4096,
        "tools": [],
        "responseFormat": "TEXT",
        "metadata": {},
    },
    "memoryMode": "EXTRACTED",
    "memoryCount": 5,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-02T00:00:00Z",
}

MEMORY_JSON = {
    "id": "m2000000-0000-0000-0000-000000000001",
    "characterId": "c1000000-0000-0000-0000-000000000001",
    "createdBy": "m1000000-0000-0000-0000-000000000001",
    "content": "Ada loves Python and functional programming",
    "category": "general",
    "salience": 0.8,
    "contentHash": "abc123",
    "visibility": "PRIVATE",
    "state": "ACTIVE",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

SEARCH_RESULT_JSON = {
    "memoryId": "m2000000-0000-0000-0000-000000000001",
    "content": "Ada loves Python and functional programming",
    "category": "general",
    "relevanceScore": 0.95,
    "salience": 0.8,
    "decayWeight": 1.0,
    "occurrenceCount": 1,
    "occurrenceBoost": 0.0,
    "finalScore": 0.95,
}

TEMPLATE_JSON = {
    "id": "t3000000-0000-0000-0000-000000000001",
    "name": "Sales Rep Template",
    "description": "Template for sales reps",
    "categories": [],
    "defaultValues": {"role": "Sales Rep"},
    "fieldMappings": [
        {"sourceColumn": "name", "targetCategory": "", "targetField": "name"},
    ],
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

BATCH_JOB_JSON = {
    "jobId": "j4000000-0000-0000-0000-000000000001",
    "type": "CREATE_CHARACTERS",
    "status": "COMPLETED",
    "progress": {"total": 10, "processed": 10, "succeeded": 10, "failed": 0, "skipped": 0},
    "errors": [],
    "dryRun": False,
    "createdAt": "2025-01-01T00:00:00Z",
    "completedAt": "2025-01-01T00:01:00Z",
}
