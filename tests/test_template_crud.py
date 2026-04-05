"""Tests for character template CRUD operations."""

import httpx

from tests.conftest import TEMPLATE_JSON, CHARACTER_JSON


TID = "t3000000-0000-0000-0000-000000000001"


def test_create_character_template(client, mock_api):
    mock_api.post("/v1/templates/characters").mock(
        return_value=httpx.Response(201, json=TEMPLATE_JSON)
    )
    template = client.create_character_template(
        name="Sales Rep Template",
        description="Template for sales reps",
    )
    assert template.name == "Sales Rep Template"
    assert template.id == TID


def test_list_character_templates(client, mock_api):
    mock_api.get("/v1/templates/characters").mock(
        return_value=httpx.Response(200, json=[TEMPLATE_JSON])
    )
    templates = client.list_character_templates()
    assert len(templates) == 1


def test_get_character_template(client, mock_api):
    mock_api.get(f"/v1/templates/characters/{TID}").mock(
        return_value=httpx.Response(200, json=TEMPLATE_JSON)
    )
    template = client.get_character_template(TID)
    assert template.name == "Sales Rep Template"


def test_update_character_template(client, mock_api):
    updated = {**TEMPLATE_JSON, "name": "Updated Template"}
    mock_api.put(f"/v1/templates/characters/{TID}").mock(
        return_value=httpx.Response(200, json=updated)
    )
    template = client.update_character_template(TID, name="Updated Template")
    assert template.name == "Updated Template"


def test_delete_character_template(client, mock_api):
    mock_api.delete(f"/v1/templates/characters/{TID}").mock(
        return_value=httpx.Response(204)
    )
    client.delete_character_template(TID)


def test_preview_character_template(client, mock_api):
    mock_api.post(f"/v1/templates/characters/{TID}/preview").mock(
        return_value=httpx.Response(200, json=CHARACTER_JSON)
    )
    char = client.preview_character_template(TID, {"name": "Test"})
    assert char.name == "Ada"


def test_clone_character_template(client, mock_api):
    cloned = {**TEMPLATE_JSON, "name": "Sales Rep Template (copy)"}
    mock_api.post(f"/v1/templates/characters/{TID}/clone").mock(
        return_value=httpx.Response(201, json=cloned)
    )
    template = client.clone_character_template(TID)
    assert "copy" in template.name
