# hippodid

Python SDK for [HippoDid](https://hippodid.com) -- character memory for AI agents.

HippoDid gives your AI agents persistent identity: personality, background, rules, structured memories, and agent configuration. This SDK wraps the REST API and adds client-side context assembly for any LLM framework.

```bash
pip install hippodid
```

## Quick Start

```python
from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")

# Create a character
char = hd.create_character(name="Ada", description="Senior engineer")

# Set up her profile
hd.update_profile(
    char.id,
    system_prompt="You are Ada, a senior software engineer.",
    personality="Analytical, thorough, loves clean architecture",
    rules=["Always suggest tests", "Prefer functional patterns"],
)

# Add memories
hd.add_memory(char.id, "Ada led the migration from REST to GraphQL in Q3")
hd.add_memory(char.id, "Ada prefers Rust for systems work, Python for scripting")

# Search memories
results = hd.search_memories(char.id, "programming languages")
```

## Context Assembly

The killer feature: `assemble_context` builds a complete LLM prompt from character profile + memories in one call.

```python
import anthropic
from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")
claude = anthropic.Anthropic()

# One call: fetch profile + search memories + format prompt
context = hd.assemble_context(char_id, "What should we refactor?", strategy="task_focused")

response = claude.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=context.formatted_prompt,
    messages=[{"role": "user", "content": "What should we refactor?"}],
)

# Save the exchange
hd.add_memory(char_id, f"Discussed refactoring: {response.content[0].text}")
```

### Assembly Strategies

Same character data, different prompt formatting:

| Strategy | Best For | Emphasis |
|---|---|---|
| `default` | General use | system_prompt + profile + memories by relevance |
| `conversational` | Chat agents | Personality/tone, recent episodic memories |
| `task_focused` | Work agents | Rules/constraints, project context, decisions |
| `concierge` | Service agents | Preferences/history, proactive suggestions |
| `matching` | Cross-character | Profile-heavy, minimal memories |

## Async Support

```python
from hippodid import AsyncHippoDid

async with AsyncHippoDid(api_key="hd_your_key") as hd:
    char = await hd.create_character(name="Ada")
    await hd.add_memory(char.id, "Ada loves async Python")
    context = await hd.assemble_context(char.id, "async patterns")
```

## Character Templates & Batch Create

```python
# Create a template for batch character creation
template = hd.create_character_template(
    name="Sales Rep",
    field_mappings=[
        {"sourceColumn": "name", "targetField": "name"},
        {"sourceColumn": "crm_id", "targetField": "externalId"},
    ],
)

# Batch create from a list of dicts (also accepts pandas DataFrames or file paths)
job = hd.batch_create_characters(
    template_id=template.id,
    data=[
        {"name": "Alice", "crm_id": "SF-001"},
        {"name": "Bob", "crm_id": "SF-002"},
    ],
    external_id_column="crm_id",
)

# Poll for completion
status = hd.get_batch_job_status(job.job_id)
```

## Agent Config

Store LLM preferences per character:

```python
hd.set_agent_config(
    char_id,
    system_prompt="You are Ada, a senior engineer.",
    preferred_model="claude-sonnet-4-20250514",
    temperature=0.3,
    tools=["code_search", "run_tests"],
)

# RAG: ask a question using character's memories + stored agent config
result = hd.ask(char_id, "What patterns should we use?", use_agent_config=True)
print(result.answer)
```

## Memory Modes

Control how `add_memory` processes content:

```python
hd.set_memory_mode(char_id, "VERBATIM")   # Store exact content, zero LLM cost
hd.set_memory_mode(char_id, "EXTRACTED")   # AI extracts structured facts (default)
hd.set_memory_mode(char_id, "HYBRID")      # Both extraction + verbatim (Business+)
```

## Clone Characters

```python
clone = hd.clone_character(
    char_id,
    "Ada-Staging",
    copy_memories=True,
    copy_tags=True,
)
print(f"Cloned: {clone.character.id}, {clone.memories_copied} memories copied")
```

## Framework Examples

See the `examples/` directory:

- **[claude_hippodid_direct.py](examples/claude_hippodid_direct.py)** -- 10-line Claude integration
- **[langchain_hippodid_memory.py](examples/langchain_hippodid_memory.py)** -- Drop-in BaseChatMemory subclass
- **[crewai_hippodid_memory.py](examples/crewai_hippodid_memory.py)** -- CrewAI agents with HippoDid identity
- **[openai_agents_hippodid.py](examples/openai_agents_hippodid.py)** -- OpenAI Agents SDK with memory tools
- **[luxury_concierge.py](examples/luxury_concierge.py)** -- Assembly strategy showcase
- **[salesforce_to_hippodid.py](examples/salesforce_to_hippodid.py)** -- End-to-end batch pipeline
- **[healer_matching.py](examples/healer_matching.py)** -- Cross-character matching

## API Reference

Full documentation at [docs.hippodid.com](https://docs.hippodid.com).

## License

MIT
