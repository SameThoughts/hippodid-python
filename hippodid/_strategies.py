"""Assembly strategies for building LLM prompts from character context."""

from __future__ import annotations

from typing import List, Optional

from hippodid.models import AgentConfig, AssembledContext, Character, SearchResult


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return max(1, len(text) // 4)


def _format_memories_by_relevance(
    results: List[SearchResult],
    max_tokens: int,
) -> str:
    """Format memories ordered by relevance, respecting token budget."""
    if not results:
        return ""

    lines: list[str] = []
    budget = max_tokens
    for r in results:
        line = f"- [{r.category}] {r.content}"
        cost = _estimate_tokens(line)
        if cost > budget:
            break
        lines.append(line)
        budget -= cost

    return "\n".join(lines)


def _format_profile(character: Character) -> str:
    """Build a profile string from character data."""
    parts: list[str] = []
    p = character.profile

    if p.personality:
        parts.append(f"Personality: {p.personality}")
    if p.background:
        parts.append(f"Background: {p.background}")
    if p.rules:
        rules_str = "\n".join(f"  - {r}" for r in p.rules)
        parts.append(f"Rules:\n{rules_str}")
    if p.custom_fields:
        for k, v in p.custom_fields.items():
            parts.append(f"{k}: {v}")

    return "\n\n".join(parts)


def _get_system_prompt(character: Character) -> str:
    return character.profile.system_prompt or ""


def _get_agent_config(character: Character) -> Optional[AgentConfig]:
    return character.agent_config


# ── Strategy implementations ─────────────────────────────────────────────────


def assemble_default(
    character: Character,
    results: List[SearchResult],
    max_context_tokens: int,
    recency_weight: float,
) -> AssembledContext:
    """Default strategy: system_prompt + profile + memories ordered by relevance."""
    system_prompt = _get_system_prompt(character)
    profile = _format_profile(character)
    memories = _format_memories_by_relevance(results, max_context_tokens)
    config = _get_agent_config(character)

    prompt_parts = []
    if system_prompt:
        prompt_parts.append(system_prompt)
    if profile:
        prompt_parts.append(f"\n## Character Profile\n{profile}")
    if memories:
        prompt_parts.append(f"\n## Relevant Memories\n{memories}")

    formatted = "\n".join(prompt_parts)

    return AssembledContext(
        system_prompt=system_prompt,
        profile=profile,
        memories=memories,
        config=config,
        formatted_prompt=formatted,
        token_estimate=_estimate_tokens(formatted),
    )


def assemble_conversational(
    character: Character,
    results: List[SearchResult],
    max_context_tokens: int,
    recency_weight: float,
) -> AssembledContext:
    """Conversational strategy: emphasizes personality/tone, interleaves recent episodic memories."""
    system_prompt = _get_system_prompt(character)
    profile = _format_profile(character)
    config = _get_agent_config(character)

    # Boost recency by reordering: blend relevance with position-based recency.
    # Results from the API are ordered by relevance; we treat earlier positions
    # as "more recent" and use the index as a recency proxy (0 = most recent).
    n = len(results) if results else 1
    sorted_results = sorted(
        enumerate(results),
        key=lambda pair: (
            pair[1].relevance_score * (1.0 - recency_weight)
            + (1.0 - pair[0] / n) * recency_weight
        ),
        reverse=True,
    )
    memories = _format_memories_by_relevance(
        [r for _, r in sorted_results], max_context_tokens
    )

    prompt_parts = []
    if system_prompt:
        prompt_parts.append(system_prompt)
    if profile:
        prompt_parts.append(
            f"\n## Who You Are\n"
            f"Speak naturally in character. Your personality and tone matter most.\n\n{profile}"
        )
    if memories:
        prompt_parts.append(
            f"\n## Recent Context & Memories\n"
            f"Draw on these naturally in conversation:\n{memories}"
        )

    formatted = "\n".join(prompt_parts)

    return AssembledContext(
        system_prompt=system_prompt,
        profile=profile,
        memories=memories,
        config=config,
        formatted_prompt=formatted,
        token_estimate=_estimate_tokens(formatted),
    )


def assemble_task_focused(
    character: Character,
    results: List[SearchResult],
    max_context_tokens: int,
    recency_weight: float,
) -> AssembledContext:
    """Task-focused strategy: emphasizes rules/constraints, prioritizes project context."""
    system_prompt = _get_system_prompt(character)
    profile = _format_profile(character)
    config = _get_agent_config(character)

    # Filter for task-relevant categories
    priority_categories = {"decisions", "project_context", "rules", "constraints", "preferences"}
    prioritized = sorted(
        results,
        key=lambda r: (0 if r.category.lower() in priority_categories else 1, -r.relevance_score),
    )
    memories = _format_memories_by_relevance(prioritized, max_context_tokens)

    prompt_parts = []
    if system_prompt:
        prompt_parts.append(system_prompt)

    # Rules first
    p = character.profile
    if p.rules:
        rules_str = "\n".join(f"  - {r}" for r in p.rules)
        prompt_parts.append(f"\n## Operating Rules\nFollow these strictly:\n{rules_str}")

    if memories:
        prompt_parts.append(
            f"\n## Relevant Context\n"
            f"Use these facts to inform your work:\n{memories}"
        )

    formatted = "\n".join(prompt_parts)

    return AssembledContext(
        system_prompt=system_prompt,
        profile=profile,
        memories=memories,
        config=config,
        formatted_prompt=formatted,
        token_estimate=_estimate_tokens(formatted),
    )


def assemble_concierge(
    character: Character,
    results: List[SearchResult],
    max_context_tokens: int,
    recency_weight: float,
) -> AssembledContext:
    """Concierge strategy: emphasizes preferences/history, proactive suggestions, warm tone."""
    system_prompt = _get_system_prompt(character)
    profile = _format_profile(character)
    config = _get_agent_config(character)

    # Preference-heavy ordering
    preference_categories = {"preferences", "history", "personal", "favorites", "lifestyle"}
    prioritized = sorted(
        results,
        key=lambda r: (0 if r.category.lower() in preference_categories else 1, -r.relevance_score),
    )
    memories = _format_memories_by_relevance(prioritized, max_context_tokens)

    prompt_parts = [
        system_prompt or "You are a thoughtful, proactive concierge.",
        "\n## Guest Profile\n"
        "You know this person well. Be warm, anticipate needs, "
        "and reference their preferences naturally.\n\n" + profile,
    ]
    if memories:
        prompt_parts.append(
            f"\n## What You Know About Them\n"
            f"Use these to personalize your response and proactively suggest:\n{memories}"
        )

    formatted = "\n".join(prompt_parts)

    return AssembledContext(
        system_prompt=system_prompt,
        profile=profile,
        memories=memories,
        config=config,
        formatted_prompt=formatted,
        token_estimate=_estimate_tokens(formatted),
    )


def assemble_matching(
    character: Character,
    results: List[SearchResult],
    max_context_tokens: int,
    recency_weight: float,
) -> AssembledContext:
    """Matching strategy: profile-heavy, minimal memories. For cross-character explanation."""
    system_prompt = _get_system_prompt(character)
    profile = _format_profile(character)
    config = _get_agent_config(character)

    # Only include a handful of highest-relevance memories
    top_results = results[:3] if results else []
    memories = _format_memories_by_relevance(top_results, max_context_tokens // 4)

    prompt_parts = [
        system_prompt or "",
        f"\n## Character Summary\n{profile}",
    ]
    if memories:
        prompt_parts.append(f"\n## Key Facts\n{memories}")

    formatted = "\n".join(prompt_parts)

    return AssembledContext(
        system_prompt=system_prompt,
        profile=profile,
        memories=memories,
        config=config,
        formatted_prompt=formatted,
        token_estimate=_estimate_tokens(formatted),
    )


STRATEGIES = {
    "default": assemble_default,
    "conversational": assemble_conversational,
    "task_focused": assemble_task_focused,
    "concierge": assemble_concierge,
    "matching": assemble_matching,
}
