"""Tests for assemble_context and strategies."""

import httpx

from hippodid.models import AssembledContext, Character, SearchResult
from hippodid._strategies import (
    STRATEGIES,
    assemble_conversational,
    assemble_default,
    assemble_task_focused,
    assemble_concierge,
    assemble_matching,
)
from tests.conftest import CHARACTER_JSON, SEARCH_RESULT_JSON


CID = "c1000000-0000-0000-0000-000000000001"


def _make_character() -> Character:
    return Character.model_validate(CHARACTER_JSON)


def _make_results() -> list:
    return [
        SearchResult.model_validate(SEARCH_RESULT_JSON),
        SearchResult.model_validate(
            {**SEARCH_RESULT_JSON, "content": "Ada also enjoys Haskell", "category": "preferences"}
        ),
    ]


def test_assemble_context_default(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(200, json=CHARACTER_JSON)
    )
    mock_api.post(f"/v1/characters/{CID}/memories/search").mock(
        return_value=httpx.Response(200, json={"results": [SEARCH_RESULT_JSON], "count": 1})
    )
    ctx = client.assemble_context(CID, "programming", strategy="default")
    assert isinstance(ctx, AssembledContext)
    assert ctx.system_prompt == "You are Ada, a helpful AI assistant."
    assert "Ada loves Python" in ctx.memories
    assert ctx.formatted_prompt != ""
    assert ctx.token_estimate > 0


def test_each_strategy_produces_different_output():
    character = _make_character()
    results = _make_results()

    outputs = {}
    for name, fn in STRATEGIES.items():
        ctx = fn(character, results, 4000, 0.5)
        outputs[name] = ctx.formatted_prompt

    # Each strategy should produce different formatted output
    unique_outputs = set(outputs.values())
    assert len(unique_outputs) == len(STRATEGIES), (
        f"Expected {len(STRATEGIES)} unique outputs, got {len(unique_outputs)}"
    )


def test_assemble_context_token_budget():
    character = _make_character()
    # Create many results to exceed budget
    results = [
        SearchResult.model_validate({
            **SEARCH_RESULT_JSON,
            "content": f"Memory fact number {i} with some extra text to increase size " * 5,
        })
        for i in range(50)
    ]

    ctx_small = assemble_default(character, results, max_context_tokens=100, recency_weight=0.5)
    ctx_large = assemble_default(character, results, max_context_tokens=10000, recency_weight=0.5)

    # Smaller budget should produce shorter output
    assert len(ctx_small.memories) < len(ctx_large.memories)


def test_assemble_context_recency_weight():
    character = _make_character()
    results = [
        SearchResult.model_validate({
            **SEARCH_RESULT_JSON,
            "content": f"Memory {i}",
            "relevanceScore": 0.5 + (i * 0.05),
        })
        for i in range(10)
    ]

    ctx_low = assemble_conversational(character, results, 4000, recency_weight=0.0)
    ctx_high = assemble_conversational(character, results, 4000, recency_weight=1.0)

    # Both should produce non-empty memories
    assert ctx_low.memories != ""
    assert ctx_high.memories != ""
    # Different recency weights should change memory ordering
    assert ctx_low.memories != ctx_high.memories, (
        "recency_weight=0.0 and recency_weight=1.0 should produce different memory orderings"
    )


def test_conversational_strategy_has_personality_emphasis():
    character = _make_character()
    results = _make_results()
    ctx = assemble_conversational(character, results, 4000, 0.5)
    assert "Who You Are" in ctx.formatted_prompt
    assert "personality" in ctx.formatted_prompt.lower() or "tone" in ctx.formatted_prompt.lower()


def test_task_focused_strategy_has_rules():
    character = _make_character()
    results = _make_results()
    ctx = assemble_task_focused(character, results, 4000, 0.5)
    assert "Operating Rules" in ctx.formatted_prompt
    assert "Be helpful" in ctx.formatted_prompt


def test_concierge_strategy_has_warmth():
    character = _make_character()
    results = _make_results()
    ctx = assemble_concierge(character, results, 4000, 0.5)
    assert "Guest Profile" in ctx.formatted_prompt or "concierge" in ctx.formatted_prompt.lower()


def test_matching_strategy_is_profile_heavy():
    character = _make_character()
    results = _make_results()
    ctx = assemble_matching(character, results, 4000, 0.5)
    assert "Character Summary" in ctx.formatted_prompt
    # Matching uses minimal memories
    assert ctx.profile != ""


def test_unknown_strategy_raises(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(200, json=CHARACTER_JSON)
    )
    mock_api.post(f"/v1/characters/{CID}/memories/search").mock(
        return_value=httpx.Response(200, json={"results": [], "count": 0})
    )
    import pytest
    with pytest.raises(ValueError, match="Unknown strategy"):
        client.assemble_context(CID, "test", strategy="nonexistent")
