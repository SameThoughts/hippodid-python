"""Tests for memory operations."""

import httpx

from tests.conftest import MEMORY_JSON, SEARCH_RESULT_JSON


CID = "c1000000-0000-0000-0000-000000000001"


def test_add_memory(client, mock_api):
    mock_api.post(f"/v1/characters/{CID}/memories").mock(
        return_value=httpx.Response(201, json=[MEMORY_JSON])
    )
    memories = client.add_memory(CID, "Ada loves Python and functional programming")
    assert len(memories) == 1
    assert memories[0].content == "Ada loves Python and functional programming"
    assert memories[0].salience == 0.8


def test_add_memory_direct(client, mock_api):
    mock_api.post(f"/v1/characters/{CID}/memories/direct").mock(
        return_value=httpx.Response(201, json=MEMORY_JSON)
    )
    memory = client.add_memory_direct(CID, "Test content", "general", salience=0.9)
    assert memory.category == "general"


def test_search_memories(client, mock_api):
    mock_api.post(f"/v1/characters/{CID}/memories/search").mock(
        return_value=httpx.Response(200, json={"results": [SEARCH_RESULT_JSON], "count": 1})
    )
    results = client.search_memories(CID, "programming")
    assert len(results) == 1
    assert results[0].relevance_score == 0.95
    assert results[0].category == "general"


def test_get_memories(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}/memories").mock(
        return_value=httpx.Response(200, json={"memories": [MEMORY_JSON], "total": 1})
    )
    memories = client.get_memories(CID)
    assert len(memories) == 1


def test_get_single_memory(client, mock_api):
    mid = "m2000000-0000-0000-0000-000000000001"
    mock_api.get(f"/v1/characters/{CID}/memories/{mid}").mock(
        return_value=httpx.Response(200, json=MEMORY_JSON)
    )
    memory = client.get_memory(CID, mid)
    assert memory.id == mid


def test_update_memory(client, mock_api):
    mid = "m2000000-0000-0000-0000-000000000001"
    updated = {**MEMORY_JSON, "content": "Updated content"}
    mock_api.put(f"/v1/characters/{CID}/memories/{mid}").mock(
        return_value=httpx.Response(200, json=updated)
    )
    memory = client.update_memory(CID, mid, "Updated content", salience=0.9)
    assert memory.content == "Updated content"


def test_delete_memory(client, mock_api):
    mid = "m2000000-0000-0000-0000-000000000001"
    mock_api.delete(f"/v1/characters/{CID}/memories/{mid}").mock(return_value=httpx.Response(204))
    client.delete_memory(CID, mid)
