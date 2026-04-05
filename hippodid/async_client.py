"""Asynchronous HippoDid client."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional, Union

from hippodid._http import AsyncTransport
from hippodid._strategies import STRATEGIES
from hippodid.models import (
    AgentConfig,
    AgentConfigTemplate,
    AskResult,
    AssembledContext,
    BatchJob,
    Category,
    Character,
    CharacterTemplate,
    CloneResult,
    Memory,
    SearchResult,
    Tag,
)


class AsyncHippoDid:
    """Asynchronous client for the HippoDid API.

    Usage::

        async with AsyncHippoDid(api_key="hd_...") as hd:
            char = await hd.create_character(name="Ada")
            await hd.add_memory(char.id, "Ada loves Python")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.hippodid.com",
        tenant_id: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self._transport = AsyncTransport(
            base_url=base_url,
            api_key=api_key,
            tenant_id=tenant_id,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> "AsyncHippoDid":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ── helpers ───────────────────────────────────────────────────────────────

    async def _get(self, path: str, **kwargs: Any) -> Any:
        resp = await self._transport.request("GET", path, **kwargs)
        return resp.json()

    async def _post(self, path: str, **kwargs: Any) -> Any:
        resp = await self._transport.request("POST", path, **kwargs)
        return resp.json()

    async def _put(self, path: str, **kwargs: Any) -> Any:
        resp = await self._transport.request("PUT", path, **kwargs)
        return resp.json()

    async def _patch(self, path: str, **kwargs: Any) -> Any:
        resp = await self._transport.request("PATCH", path, **kwargs)
        return resp.json()

    async def _delete(self, path: str, **kwargs: Any) -> None:
        await self._transport.request("DELETE", path, **kwargs)

    # ═════════════════════════════════════════════════════════════════════════
    # Characters
    # ═════════════════════════════════════════════════════════════════════════

    async def create_character(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        visibility: str = "PRIVATE",
        external_id: Optional[str] = None,
        memory_mode: Optional[str] = None,
    ) -> Character:
        body: Dict[str, Any] = {"name": name, "visibility": visibility}
        if description is not None:
            body["description"] = description
        if external_id is not None:
            body["externalId"] = external_id
        if memory_mode is not None:
            body["memoryMode"] = memory_mode
        return Character.model_validate(await self._post("/v1/characters", json=body))

    async def get_character(self, character_id: str) -> Character:
        return Character.model_validate(await self._get(f"/v1/characters/{character_id}"))

    async def get_character_by_external_id(self, external_id: str) -> Character:
        return Character.model_validate(
            await self._get(f"/v1/characters/external/{external_id}")
        )

    async def list_characters(
        self,
        *,
        page: int = 0,
        limit: int = 20,
        tag: Optional[str] = None,
        sort_by: str = "CREATED_AT",
        sort_order: str = "DESC",
    ) -> List[Character]:
        data = await self._get(
            "/v1/characters",
            params={
                "page": page,
                "limit": limit,
                "tag": tag,
                "sortBy": sort_by,
                "sortOrder": sort_order,
            },
        )
        items = data.get("characters", data.get("items", []))
        return [Character.model_validate(c) for c in items]

    async def update_character(
        self,
        character_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        memory_mode: Optional[str] = None,
    ) -> Character:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if memory_mode is not None:
            body["memoryMode"] = memory_mode
        return Character.model_validate(
            await self._put(f"/v1/characters/{character_id}", json=body)
        )

    async def delete_character(self, character_id: str) -> None:
        await self._delete(f"/v1/characters/{character_id}")

    # ── Profile ───────────────────────────────────────────────────────────────

    async def get_profile(self, character_id: str) -> Character:
        return await self.get_character(character_id)

    async def update_profile(
        self,
        character_id: str,
        *,
        system_prompt: Optional[str] = None,
        personality: Optional[str] = None,
        background: Optional[str] = None,
        rules: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, str]] = None,
    ) -> Character:
        body: Dict[str, Any] = {}
        if system_prompt is not None:
            body["systemPrompt"] = system_prompt
        if personality is not None:
            body["personality"] = personality
        if background is not None:
            body["background"] = background
        if rules is not None:
            body["rules"] = rules
        if custom_fields is not None:
            body["customFields"] = custom_fields
        return Character.model_validate(
            await self._patch(f"/v1/characters/{character_id}/profile", json=body)
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Memories
    # ═════════════════════════════════════════════════════════════════════════

    async def add_memory(
        self,
        character_id: str,
        content: str,
        *,
        source_type: str = "manual",
    ) -> List[Memory]:
        data = await self._post(
            f"/v1/characters/{character_id}/memories",
            json={"content": content, "sourceType": source_type},
        )
        if isinstance(data, list):
            return [Memory.model_validate(m) for m in data]
        return [Memory.model_validate(data)]

    async def search_memories(
        self,
        character_id: str,
        query: str,
        *,
        top_k: int = 10,
        categories: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        body: Dict[str, Any] = {"query": query, "topK": top_k}
        if categories:
            body["categories"] = categories
        data = await self._post(
            f"/v1/characters/{character_id}/memories/search", json=body
        )
        return [SearchResult.model_validate(r) for r in data.get("results", [])]

    async def get_memories(
        self,
        character_id: str,
        *,
        page: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
    ) -> List[Memory]:
        data = await self._get(
            f"/v1/characters/{character_id}/memories",
            params={"page": page, "limit": limit, "category": category},
        )
        return [Memory.model_validate(m) for m in data.get("memories", data.get("items", []))]

    async def add_memory_direct(
        self,
        character_id: str,
        content: str,
        category: str,
        *,
        salience: float = 0.5,
        visibility: str = "PRIVATE",
    ) -> Memory:
        return Memory.model_validate(
            await self._post(
                f"/v1/characters/{character_id}/memories/direct",
                json={
                    "content": content,
                    "category": category,
                    "salience": salience,
                    "visibility": visibility,
                },
            )
        )

    async def get_memory(self, character_id: str, memory_id: str) -> Memory:
        return Memory.model_validate(
            await self._get(f"/v1/characters/{character_id}/memories/{memory_id}")
        )

    async def update_memory(
        self,
        character_id: str,
        memory_id: str,
        content: str,
        *,
        salience: Optional[float] = None,
    ) -> Memory:
        body: Dict[str, Any] = {"content": content}
        if salience is not None:
            body["salience"] = salience
        return Memory.model_validate(
            await self._put(f"/v1/characters/{character_id}/memories/{memory_id}", json=body)
        )

    async def delete_memory(self, character_id: str, memory_id: str) -> None:
        await self._delete(f"/v1/characters/{character_id}/memories/{memory_id}")

    # ═════════════════════════════════════════════════════════════════════════
    # Categories & Tags
    # ═════════════════════════════════════════════════════════════════════════

    async def list_categories(self, character_id: str) -> List[Category]:
        data = await self._get(f"/v1/characters/{character_id}/categories")
        if isinstance(data, list):
            return [Category.model_validate(c) for c in data]
        return [Category.model_validate(c) for c in data.get("categories", [])]

    async def add_category(
        self, character_id: str, name: str, *, description: str = "", importance: str = "NORMAL"
    ) -> Category:
        return Category.model_validate(
            await self._post(
                f"/v1/characters/{character_id}/categories",
                json={"name": name, "description": description, "importance": importance},
            )
        )

    async def list_tags(self, character_id: str) -> Tag:
        return Tag.model_validate(await self._get(f"/v1/characters/{character_id}/tags"))

    async def add_tags(self, character_id: str, tags: List[str]) -> Tag:
        return Tag.model_validate(
            await self._post(f"/v1/characters/{character_id}/tags", json={"tags": tags})
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Templates (Sprint 15)
    # ═════════════════════════════════════════════════════════════════════════

    async def create_character_template(
        self,
        name: str,
        *,
        description: str = "",
        categories: Optional[List[Dict[str, Any]]] = None,
        default_values: Optional[Dict[str, str]] = None,
        field_mappings: Optional[List[Dict[str, str]]] = None,
    ) -> CharacterTemplate:
        body: Dict[str, Any] = {"name": name, "description": description}
        if categories is not None:
            body["categories"] = categories
        if default_values is not None:
            body["defaultValues"] = default_values
        if field_mappings is not None:
            body["fieldMappings"] = field_mappings
        return CharacterTemplate.model_validate(
            await self._post("/v1/templates/characters", json=body)
        )

    async def list_character_templates(self) -> List[CharacterTemplate]:
        data = await self._get("/v1/templates/characters")
        if isinstance(data, list):
            return [CharacterTemplate.model_validate(t) for t in data]
        return [CharacterTemplate.model_validate(t) for t in data.get("templates", [])]

    async def get_character_template(self, template_id: str) -> CharacterTemplate:
        return CharacterTemplate.model_validate(
            await self._get(f"/v1/templates/characters/{template_id}")
        )

    async def delete_character_template(self, template_id: str) -> None:
        await self._delete(f"/v1/templates/characters/{template_id}")

    async def update_character_template(
        self,
        template_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        categories: Optional[List[Dict[str, Any]]] = None,
        default_values: Optional[Dict[str, str]] = None,
        field_mappings: Optional[List[Dict[str, str]]] = None,
    ) -> CharacterTemplate:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if categories is not None:
            body["categories"] = categories
        if default_values is not None:
            body["defaultValues"] = default_values
        if field_mappings is not None:
            body["fieldMappings"] = field_mappings
        return CharacterTemplate.model_validate(
            await self._put(f"/v1/templates/characters/{template_id}", json=body)
        )

    async def preview_character_template(
        self, template_id: str, sample_row: Dict[str, str]
    ) -> Character:
        return Character.model_validate(
            await self._post(
                f"/v1/templates/characters/{template_id}/preview",
                json={"sampleRow": sample_row},
            )
        )

    async def clone_character_template(self, template_id: str) -> CharacterTemplate:
        return CharacterTemplate.model_validate(
            await self._post(f"/v1/templates/characters/{template_id}/clone", json={})
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Tags (full parity)
    # ═════════════════════════════════════════════════════════════════════════

    async def replace_tags(self, character_id: str, tags: List[str]) -> Tag:
        return Tag.model_validate(
            await self._put(f"/v1/characters/{character_id}/tags", json={"tags": tags})
        )

    async def remove_tag(self, character_id: str, tag: str) -> None:
        await self._delete(f"/v1/characters/{character_id}/tags/{tag}")

    # ═════════════════════════════════════════════════════════════════════════
    # Batch (Sprint 16)
    # ═════════════════════════════════════════════════════════════════════════

    async def batch_create_characters(
        self,
        template_id: str,
        data: Union[List[Dict[str, str]], Any],
        external_id_column: str,
        *,
        on_conflict: str = "ERROR",
        dry_run: bool = False,
    ) -> BatchJob:
        rows: List[Dict[str, str]]
        if hasattr(data, "to_dict"):
            rows = data.to_dict(orient="records")  # type: ignore[union-attr]
        elif isinstance(data, list):
            rows = data
        else:
            raise TypeError(f"data must be list of dicts or DataFrame, got {type(data)}")

        csv_bytes = _rows_to_csv(rows)
        resp = await self._transport.request_multipart(
            "/v1/characters/batch",
            files={"file": ("data.csv", csv_bytes)},
            data={
                "templateId": template_id,
                "externalIdColumn": external_id_column,
                "onConflict": on_conflict,
                "dryRun": str(dry_run).lower(),
            },
        )
        return BatchJob.model_validate(resp.json())

    async def batch_create_from_file(
        self,
        template_id: str,
        file_path: str,
        external_id_column: str,
        *,
        on_conflict: str = "ERROR",
        dry_run: bool = False,
    ) -> BatchJob:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        filename = file_path.rsplit("/", 1)[-1] if "/" in file_path else file_path
        resp = await self._transport.request_multipart(
            "/v1/characters/batch",
            files={"file": (filename, file_bytes)},
            data={
                "templateId": template_id,
                "externalIdColumn": external_id_column,
                "onConflict": on_conflict,
                "dryRun": str(dry_run).lower(),
            },
        )
        return BatchJob.model_validate(resp.json())

    async def get_batch_job_status(self, job_id: str) -> BatchJob:
        return BatchJob.model_validate(await self._get(f"/v1/jobs/{job_id}"))

    # ═════════════════════════════════════════════════════════════════════════
    # Agent Config (Sprint 17)
    # ═════════════════════════════════════════════════════════════════════════

    async def get_agent_config(self, character_id: str) -> AgentConfig:
        return AgentConfig.model_validate(
            await self._get(f"/v1/characters/{character_id}/agent-config")
        )

    async def set_agent_config(
        self,
        character_id: str,
        *,
        system_prompt: str = "",
        preferred_model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: Optional[List[str]] = None,
        response_format: str = "TEXT",
        metadata: Optional[Dict[str, str]] = None,
    ) -> AgentConfig:
        body = {
            "systemPrompt": system_prompt,
            "preferredModel": preferred_model,
            "temperature": temperature,
            "maxTokens": max_tokens,
            "tools": tools or [],
            "responseFormat": response_format,
            "metadata": metadata or {},
        }
        return AgentConfig.model_validate(
            await self._put(f"/v1/characters/{character_id}/agent-config", json=body)
        )

    async def delete_agent_config(self, character_id: str) -> None:
        await self._delete(f"/v1/characters/{character_id}/agent-config")

    async def create_agent_config_template(
        self, name: str, **kwargs: Any
    ) -> AgentConfigTemplate:
        body = {
            "name": name,
            "config": {
                "systemPrompt": kwargs.get("system_prompt", ""),
                "preferredModel": kwargs.get("preferred_model", "claude-sonnet-4-20250514"),
                "temperature": kwargs.get("temperature", 0.7),
                "maxTokens": kwargs.get("max_tokens", 4096),
                "tools": kwargs.get("tools", []),
                "responseFormat": kwargs.get("response_format", "TEXT"),
                "metadata": {},
            },
        }
        return AgentConfigTemplate.model_validate(
            await self._post("/v1/templates/agent-configs", json=body)
        )

    async def list_agent_config_templates(self) -> List[AgentConfigTemplate]:
        data = await self._get("/v1/templates/agent-configs")
        if isinstance(data, list):
            return [AgentConfigTemplate.model_validate(t) for t in data]
        return [AgentConfigTemplate.model_validate(t) for t in data.get("templates", [])]

    # ═════════════════════════════════════════════════════════════════════════
    # Clone & Memory Mode (Sprint 17)
    # ═════════════════════════════════════════════════════════════════════════

    async def clone_character(
        self,
        character_id: str,
        name: str,
        *,
        external_id: Optional[str] = None,
        copy_memories: bool = False,
        copy_tags: bool = True,
        agent_config_override: Optional[Dict[str, Any]] = None,
    ) -> CloneResult:
        body: Dict[str, Any] = {
            "name": name,
            "copyMemories": copy_memories,
            "copyTags": copy_tags,
        }
        if external_id is not None:
            body["externalId"] = external_id
        if agent_config_override is not None:
            body["agentConfigOverride"] = agent_config_override
        return CloneResult.model_validate(
            await self._post(f"/v1/characters/{character_id}/clone", json=body)
        )

    async def set_memory_mode(self, character_id: str, mode: str) -> Character:
        return await self.update_character(character_id, memory_mode=mode)

    # ═════════════════════════════════════════════════════════════════════════
    # Ask / RAG Chat
    # ═════════════════════════════════════════════════════════════════════════

    async def ask(
        self,
        character_id: str,
        question: str,
        *,
        model: Optional[str] = None,
        top_k: Optional[int] = None,
        category: Optional[str] = None,
        use_agent_config: bool = False,
    ) -> AskResult:
        body: Dict[str, Any] = {"question": question}
        if model is not None:
            body["model"] = model
        if top_k is not None:
            body["topK"] = top_k
        if category is not None:
            body["category"] = category
        if use_agent_config:
            body["useAgentConfig"] = True
        return AskResult.model_validate(
            await self._post(f"/v1/characters/{character_id}/ask", json=body)
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Assemble Context (client-side)
    # ═════════════════════════════════════════════════════════════════════════

    async def assemble_context(
        self,
        character_id: str,
        query: str,
        *,
        top_k: int = 10,
        strategy: str = "default",
        max_context_tokens: int = 4000,
        recency_weight: float = 0.5,
    ) -> AssembledContext:
        character = await self.get_character(character_id)
        results = await self.search_memories(character_id, query, top_k=top_k)

        strategy_fn = STRATEGIES.get(strategy)
        if strategy_fn is None:
            raise ValueError(
                f"Unknown strategy '{strategy}'. Available: {', '.join(STRATEGIES.keys())}"
            )

        return strategy_fn(character, results, max_context_tokens, recency_weight)

    # ═════════════════════════════════════════════════════════════════════════
    # External ID convenience
    # ═════════════════════════════════════════════════════════════════════════

    async def upsert_by_external_id(
        self,
        external_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Character:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        return Character.model_validate(
            await self._put(f"/v1/characters/external/{external_id}", json=body)
        )


def _rows_to_csv(rows: List[Dict[str, str]]) -> bytes:
    if not rows:
        return b""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")
