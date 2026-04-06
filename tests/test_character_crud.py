"""Tests for character CRUD operations."""

import httpx

from tests.conftest import CHARACTER_JSON


def test_create_character(client, mock_api):
    mock_api.post("/v1/characters").mock(return_value=httpx.Response(201, json=CHARACTER_JSON))
    char = client.create_character(name="Ada", description="A test character")
    assert char.name == "Ada"
    assert char.id == "c1000000-0000-0000-0000-000000000001"
    assert char.profile.system_prompt == "You are Ada, a helpful AI assistant."


def test_get_character(client, mock_api):
    cid = "c1000000-0000-0000-0000-000000000001"
    mock_api.get(f"/v1/characters/{cid}").mock(
        return_value=httpx.Response(200, json=CHARACTER_JSON)
    )
    char = client.get_character(cid)
    assert char.name == "Ada"
    assert char.memory_mode == "EXTRACTED"


def test_get_character_by_external_id(client, mock_api):
    mock_api.get("/v1/characters/external/ext-ada").mock(
        return_value=httpx.Response(200, json=CHARACTER_JSON)
    )
    char = client.get_character_by_external_id("ext-ada")
    assert char.external_id == "ext-ada"


def test_list_characters(client, mock_api):
    mock_api.get("/v1/characters").mock(
        return_value=httpx.Response(200, json={"characters": [CHARACTER_JSON], "total": 1})
    )
    chars = client.list_characters()
    assert len(chars) == 1
    assert chars[0].name == "Ada"


def test_update_character(client, mock_api):
    cid = "c1000000-0000-0000-0000-000000000001"
    updated = {**CHARACTER_JSON, "name": "Ada v2"}
    mock_api.put(f"/v1/characters/{cid}").mock(return_value=httpx.Response(200, json=updated))
    char = client.update_character(cid, name="Ada v2")
    assert char.name == "Ada v2"


def test_delete_character(client, mock_api):
    cid = "c1000000-0000-0000-0000-000000000001"
    mock_api.delete(f"/v1/characters/{cid}").mock(return_value=httpx.Response(204))
    client.delete_character(cid)  # should not raise


def test_update_profile(client, mock_api):
    cid = "c1000000-0000-0000-0000-000000000001"
    mock_api.patch(f"/v1/characters/{cid}/profile").mock(
        return_value=httpx.Response(200, json=CHARACTER_JSON)
    )
    char = client.update_profile(
        cid,
        system_prompt="New prompt",
        personality="Bold",
        rules=["Rule 1"],
    )
    assert char.id == cid
