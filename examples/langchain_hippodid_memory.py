"""
LangChain + HippoDid: Drop-in BaseChatMemory subclass.

Replace ConversationBufferMemory with persistent character memory.
HippoDid provides the FULL agent identity -- not just memories:
  - system_prompt (role definition)
  - personality + background (tone + context)
  - rules (operating guardrails)
  - structured memories (categorized recall)
  - agent config (model preferences)

Requirements: pip install hippodid langchain langchain-anthropic
"""

from typing import Any, Dict, List

from langchain.memory import BaseChatMemory
from langchain.schema import BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationChain

from hippodid import HippoDid


class HippoDidMemory(BaseChatMemory):
    """LangChain memory backed by HippoDid character identity.

    Loads the complete character context on each turn:
    system prompt, profile, relevant memories, and agent config.
    Saves each exchange as a new memory for future recall.
    """

    hd: Any  # HippoDid client
    character_id: str
    strategy: str = "conversational"
    max_context_tokens: int = 4000
    human_prefix: str = "Human"
    ai_prefix: str = "AI"

    @property
    def memory_variables(self) -> List[str]:
        return ["system", "profile", "history", "agent_config"]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("input", inputs.get("question", ""))
        context = self.hd.assemble_context(
            self.character_id,
            query,
            strategy=self.strategy,
            max_context_tokens=self.max_context_tokens,
        )
        return {
            "system": context.system_prompt,
            "profile": context.profile,
            "history": context.memories,
            "agent_config": context.config,
        }

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        human_input = inputs.get("input", "")
        ai_output = outputs.get("output", outputs.get("response", ""))
        exchange = f"{self.human_prefix}: {human_input}\n{self.ai_prefix}: {ai_output}"
        self.hd.add_memory(self.character_id, exchange, source_type="langchain")

    def clear(self) -> None:
        pass  # HippoDid memories are persistent by design


# ── Usage ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    hd = HippoDid(api_key="hd_your_key")
    CHAR_ID = "your-character-uuid"

    memory = HippoDidMemory(hd=hd, character_id=CHAR_ID, strategy="conversational")

    # Load context to get model preference
    ctx = memory.load_memory_variables({"input": "hello"})
    model_name = "claude-sonnet-4-20250514"
    if ctx["agent_config"]:
        model_name = ctx["agent_config"].preferred_model

    llm = ChatAnthropic(model=model_name, temperature=0.7)
    chain = ConversationChain(llm=llm, memory=memory, verbose=True)

    response = chain.predict(input="What do you know about me?")
    print(response)
