"""Tests for character clone operations."""

import httpx

from tests.conftest import CHARACTER_JSON


CID = "c1000000-0000-0000-0000-000000000001"

CLONE_RESPONSE_JSON = {
    "character": CHARACTER_JSON,
    "memoriesCopied": 5,
}


def test_clone_character(client, mock_api):
    mock_api.post(f"/v1/characters/{CID}/clone").mock(
        return_value=httpx.Response(201, json=CLONE_RESPONSE_JSON)
    )
    result = client.clone_character(
        CID,
        "Ada Clone",
        copy_memories=True,
        copy_tags=True,
    )
    assert result.character.name == "Ada"
    assert result.memories_copied == 5


def test_clone_character_minimal(client, mock_api):
    mock_api.post(f"/v1/characters/{CID}/clone").mock(
        return_value=httpx.Response(201, json=CLONE_RESPONSE_JSON)
    )
    result = client.clone_character(CID, "Ada Clone")
    assert result.character.id == CID


def test_clone_character_with_override(client, mock_api):
    mock_api.post(f"/v1/characters/{CID}/clone").mock(
        return_value=httpx.Response(201, json=CLONE_RESPONSE_JSON)
    )
    result = client.clone_character(
        CID,
        "Ada Clone",
        agent_config_override={
            "systemPrompt": "Custom override",
            "temperature": 0.3,
        },
    )
    assert result.memories_copied == 5
