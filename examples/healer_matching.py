"""
Cross-character search for healer matching.

NOTE: Requires Sprint 19 cross-character search API (not yet available).
This example shows the intended usage pattern.

Requirements: pip install hippodid
"""

from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")


def match_healer(patient_query: str) -> None:
    """Find the best healer match for a patient's needs.

    Uses the 'matching' assembly strategy which is profile-heavy
    with minimal memories -- optimized for cross-character comparison.

    NOTE: This example requires Sprint 19's cross-character search API.
    Currently, you would need to iterate over healers manually.
    """
    # Sprint 19 will add: hd.search_characters(query=patient_query, tag="healer")
    # For now, list healers by tag and compare manually
    healers = hd.list_characters(tag="healer", limit=50)

    matches = []
    for healer in healers:
        ctx = hd.assemble_context(
            healer.id,
            patient_query,
            strategy="matching",
            max_context_tokens=1000,
        )
        matches.append(
            {
                "character": healer,
                "context": ctx,
                "token_estimate": ctx.token_estimate,
            }
        )

    # Sort by context richness (more relevant profile = better match)
    matches.sort(key=lambda m: m["token_estimate"], reverse=True)

    print(f"Top matches for: '{patient_query}'")
    for i, m in enumerate(matches[:5], 1):
        char = m["character"]
        print(f"  {i}. {char.name} (memories: {char.memory_count})")
        print(f"     Profile preview: {m['context'].profile[:100]}...")


if __name__ == "__main__":
    match_healer("chronic back pain, prefers holistic approaches")
