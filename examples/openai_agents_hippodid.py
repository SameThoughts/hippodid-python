"""
OpenAI Agents SDK + HippoDid: Agent with memory tool.

Shows how to give an OpenAI agent access to HippoDid memories
via a tool function.

Requirements: pip install hippodid openai-agents
"""

from agents import Agent, Runner, function_tool

from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")
CHAR_ID = "your-character-uuid"


@function_tool
def recall_memories(query: str, top_k: int = 5) -> str:
    """Search character memories for relevant information."""
    results = hd.search_memories(CHAR_ID, query, top_k=top_k)
    if not results:
        return "No relevant memories found."
    return "\n".join(f"- [{r.category}] {r.content}" for r in results)


@function_tool
def save_memory(content: str) -> str:
    """Save new information as a memory."""
    memories = hd.add_memory(CHAR_ID, content)
    return f"Saved {len(memories)} memory(ies)."


@function_tool
def get_character_profile() -> str:
    """Get the character's profile and identity."""
    char = hd.get_character(CHAR_ID)
    parts = []
    if char.profile.personality:
        parts.append(f"Personality: {char.profile.personality}")
    if char.profile.background:
        parts.append(f"Background: {char.profile.background}")
    if char.profile.rules:
        parts.append("Rules: " + ", ".join(char.profile.rules))
    return "\n".join(parts) if parts else "No profile set."


# Build the agent with HippoDid context
context = hd.assemble_context(CHAR_ID, "general context", strategy="conversational")

agent = Agent(
    name="HippoDid Agent",
    instructions=context.formatted_prompt,
    tools=[recall_memories, save_memory, get_character_profile],
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "What do you remember about my preferences?")
    print(result.final_output)
