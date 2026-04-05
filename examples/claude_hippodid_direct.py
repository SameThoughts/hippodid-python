"""
Simplest Claude + HippoDid integration (10 lines).

Shows: assemble_context -> Claude messages API -> save exchange as memory.

Requirements: pip install hippodid anthropic
"""

import anthropic
from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")
claude = anthropic.Anthropic()

CHAR_ID = "your-character-uuid"  # replace with your character ID
USER_MSG = "What projects am I working on?"

# 1. Assemble context from character profile + memories
context = hd.assemble_context(CHAR_ID, USER_MSG, strategy="conversational")

# 2. Call Claude with the assembled prompt
response = claude.messages.create(
    model=context.config.preferred_model if context.config else "claude-sonnet-4-20250514",
    max_tokens=1024,
    system=context.formatted_prompt,
    messages=[{"role": "user", "content": USER_MSG}],
)

answer = response.content[0].text
print(answer)

# 3. Save the exchange as a new memory
hd.add_memory(CHAR_ID, f"User asked: {USER_MSG}\nAssistant answered: {answer}")
