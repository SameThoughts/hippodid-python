"""Tests for agent config operations."""

import httpx


CID = "c1000000-0000-0000-0000-000000000001"

AGENT_CONFIG_JSON = {
    "systemPrompt": "You are Ada.",
    "preferredModel": "claude-sonnet-4-20250514",
    "temperature": 0.7,
    "maxTokens": 4096,
    "tools": [],
    "responseFormat": "TEXT",
    "metadata": {},
}

ACT_JSON = {
    "id": "act-0000-0000-0000-000000000001",
    "name": "Friendly Bot",
    "config": AGENT_CONFIG_JSON,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}


def test_get_agent_config(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}/agent-config").mock(
        return_value=httpx.Response(200, json=AGENT_CONFIG_JSON)
    )
    config = client.get_agent_config(CID)
    assert config.system_prompt == "You are Ada."
    assert config.preferred_model == "claude-sonnet-4-20250514"
    assert config.temperature == 0.7


def test_set_agent_config(client, mock_api):
    mock_api.put(f"/v1/characters/{CID}/agent-config").mock(
        return_value=httpx.Response(200, json=AGENT_CONFIG_JSON)
    )
    config = client.set_agent_config(
        CID,
        system_prompt="You are Ada.",
        temperature=0.7,
    )
    assert config.system_prompt == "You are Ada."


def test_delete_agent_config(client, mock_api):
    mock_api.delete(f"/v1/characters/{CID}/agent-config").mock(return_value=httpx.Response(204))
    client.delete_agent_config(CID)


def test_create_agent_config_template(client, mock_api):
    mock_api.post("/v1/templates/agent-configs").mock(
        return_value=httpx.Response(201, json=ACT_JSON)
    )
    template = client.create_agent_config_template(
        "Friendly Bot",
        system_prompt="You are friendly.",
    )
    assert template.name == "Friendly Bot"
    assert template.config.preferred_model == "claude-sonnet-4-20250514"


def test_list_agent_config_templates(client, mock_api):
    mock_api.get("/v1/templates/agent-configs").mock(
        return_value=httpx.Response(200, json=[ACT_JSON])
    )
    templates = client.list_agent_config_templates()
    assert len(templates) == 1
    assert templates[0].name == "Friendly Bot"
