"""Pydantic models for HippoDid API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Character & Profile ──────────────────────────────────────────────────────


class CharacterProfile(BaseModel):
    system_prompt: Optional[str] = Field(None, alias="systemPrompt")
    personality: Optional[str] = None
    background: Optional[str] = None
    rules: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, str] = Field(default_factory=dict, alias="customFields")

    model_config = {"populate_by_name": True}


class Alias(BaseModel):
    alias: str
    source_hint: Optional[str] = Field(None, alias="sourceHint")

    model_config = {"populate_by_name": True}


class AgentConfig(BaseModel):
    system_prompt: str = Field("", alias="systemPrompt")
    preferred_model: str = Field("claude-sonnet-4-20250514", alias="preferredModel")
    temperature: float = 0.7
    max_tokens: int = Field(4096, alias="maxTokens")
    tools: List[str] = Field(default_factory=list)
    response_format: str = Field("TEXT", alias="responseFormat")
    metadata: Dict[str, str] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class Category(BaseModel):
    name: str
    description: str = ""
    extraction_hints: List[str] = Field(default_factory=list, alias="extractionHints")
    importance: str = "NORMAL"
    half_life_days: int = Field(0, alias="halfLifeDays")
    effective_half_life_days: int = Field(0, alias="effectiveHalfLifeDays")
    retrieval_boost: float = Field(1.0, alias="retrievalBoost")
    is_default: bool = Field(False, alias="isDefault")
    is_evergreen: bool = Field(False, alias="isEvergreen")
    memory_count: int = Field(0, alias="memoryCount")

    model_config = {"populate_by_name": True}


class Character(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    external_id: Optional[str] = Field(None, alias="externalId")
    visibility: str = "PRIVATE"
    created_by: Optional[str] = Field(None, alias="createdBy")
    profile: CharacterProfile = Field(default_factory=CharacterProfile)
    aliases: List[Alias] = Field(default_factory=list)
    categories: List[Category] = Field(default_factory=list)
    agent_config: Optional[AgentConfig] = Field(None, alias="agentConfig")
    memory_mode: str = Field("EXTRACTED", alias="memoryMode")
    memory_count: int = Field(0, alias="memoryCount")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


# ── Memory ────────────────────────────────────────────────────────────────────


class Memory(BaseModel):
    id: str
    character_id: str = Field(alias="characterId")
    created_by: Optional[str] = Field(None, alias="createdBy")
    content: str
    category: str
    salience: float
    content_hash: str = Field("", alias="contentHash")
    visibility: str = "PRIVATE"
    state: str = "ACTIVE"
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class SearchResult(BaseModel):
    memory_id: str = Field(alias="memoryId")
    content: str
    category: str
    relevance_score: float = Field(alias="relevanceScore")
    salience: float = 0.0
    decay_weight: float = Field(1.0, alias="decayWeight")
    occurrence_count: int = Field(0, alias="occurrenceCount")
    occurrence_boost: float = Field(0.0, alias="occurrenceBoost")
    final_score: float = Field(0.0, alias="finalScore")

    model_config = {"populate_by_name": True}


# ── Tags ──────────────────────────────────────────────────────────────────────


class Tag(BaseModel):
    character_id: str = Field(alias="characterId")
    tags: List[str] = Field(default_factory=list)
    total: int = 0

    model_config = {"populate_by_name": True}


# ── Character Template ────────────────────────────────────────────────────────


class CategoryDefinitionDto(BaseModel):
    category_name: str = Field(alias="categoryName")
    purpose: str = ""
    when_to_recall: str = Field("", alias="whenToRecall")
    how_to_extract: str = Field("", alias="howToExtract")
    constraints: str = ""
    fields: List[Any] = Field(default_factory=list)
    half_life: Optional[str] = Field(None, alias="halfLife")

    model_config = {"populate_by_name": True}


class FieldMappingDto(BaseModel):
    source_column: str = Field(alias="sourceColumn")
    target_category: str = Field("", alias="targetCategory")
    target_field: str = Field(alias="targetField")

    model_config = {"populate_by_name": True}


class CharacterTemplate(BaseModel):
    id: str
    name: str
    description: str = ""
    categories: List[CategoryDefinitionDto] = Field(default_factory=list)
    default_values: Dict[str, str] = Field(default_factory=dict, alias="defaultValues")
    field_mappings: List[FieldMappingDto] = Field(default_factory=list, alias="fieldMappings")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ── Batch Job ─────────────────────────────────────────────────────────────────


class BatchJobProgress(BaseModel):
    total: int = 0
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0


class BatchJobError(BaseModel):
    row_index: int = Field(0, alias="rowIndex")
    external_id: str = Field("", alias="externalId")
    message: str = ""

    model_config = {"populate_by_name": True}


class BatchJob(BaseModel):
    job_id: str = Field(alias="jobId")
    type: str = ""
    status: str = ""
    progress: BatchJobProgress = Field(default_factory=BatchJobProgress)
    errors: List[BatchJobError] = Field(default_factory=list)
    dry_run: bool = Field(False, alias="dryRun")
    created_at: datetime = Field(alias="createdAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    model_config = {"populate_by_name": True}


# ── Agent Config Template ─────────────────────────────────────────────────────


class AgentConfigTemplate(BaseModel):
    id: str
    name: str
    config: AgentConfig
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ── Clone ─────────────────────────────────────────────────────────────────────


class CloneResult(BaseModel):
    character: Character
    memories_copied: int = Field(0, alias="memoriesCopied")

    model_config = {"populate_by_name": True}


# ── Ask / RAG ─────────────────────────────────────────────────────────────────


class Citation(BaseModel):
    memory_id: str = Field(alias="memoryId")
    content: str
    category: str
    source: str = ""
    relevance_score: float = Field(0.0, alias="relevanceScore")

    model_config = {"populate_by_name": True}


class AskResult(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    memories_searched: int = Field(0, alias="memoriesSearched")
    ai_ops_consumed: int = Field(0, alias="aiOpsConsumed")

    model_config = {"populate_by_name": True}


# ── Assembled Context (client-side) ──────────────────────────────────────────


class AssembledContext(BaseModel):
    system_prompt: str = ""
    profile: str = ""
    memories: str = ""
    config: Optional[AgentConfig] = None
    formatted_prompt: str = ""
    token_estimate: int = 0
