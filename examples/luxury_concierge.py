"""
Assembly Strategy Showcase: Same character, different behaviors.

Demonstrates how strategy="concierge" vs strategy="task_focused"
produces dramatically different agent behavior from the SAME character data.

Requirements: pip install hippodid anthropic
"""

import anthropic
from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")
claude = anthropic.Anthropic()
CHAR_ID = "your-character-uuid"  # a character with rich profile + memories

USER_MSG = "I need to book a dinner for tomorrow"


def ask_with_strategy(strategy: str) -> str:
    """Ask the same question using different assembly strategies."""
    context = hd.assemble_context(
        CHAR_ID,
        USER_MSG,
        strategy=strategy,
        max_context_tokens=4000,
    )

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=context.formatted_prompt,
        messages=[{"role": "user", "content": USER_MSG}],
    )
    return response.content[0].text


if __name__ == "__main__":
    # Concierge: warm, proactive, preference-heavy
    print("=" * 60)
    print("CONCIERGE STRATEGY")
    print("=" * 60)
    print(ask_with_strategy("concierge"))
    # Expected: "Based on your love of Italian food and preference for quiet
    # restaurants, I'd suggest Osteria Francescana. Shall I book your usual
    # corner table for 7:30pm? I remember you prefer the tasting menu."

    print()

    # Task-focused: direct, rules-heavy, action-oriented
    print("=" * 60)
    print("TASK-FOCUSED STRATEGY")
    print("=" * 60)
    print(ask_with_strategy("task_focused"))
    # Expected: "To book dinner for tomorrow, I need:
    # 1. Number of guests
    # 2. Preferred cuisine
    # 3. Time
    # 4. Budget range
    # Please provide these details."
