"""HippoDid Python SDK — character memory for AI agents."""

from hippodid.client import HippoDid
from hippodid.async_client import AsyncHippoDid
from hippodid.models import (
    AgentConfig,
    AskResult,
    AssembledContext,
    BatchJob,
    BatchJobProgress,
    Category,
    Character,
    CharacterProfile,
    CharacterTemplate,
    Citation,
    CloneResult,
    Memory,
    SearchResult,
    Tag,
)
from hippodid.exceptions import (
    AuthenticationError,
    HippoDidError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    "HippoDid",
    "AsyncHippoDid",
    "AgentConfig",
    "AskResult",
    "AssembledContext",
    "BatchJob",
    "BatchJobProgress",
    "Category",
    "Character",
    "CharacterProfile",
    "CharacterTemplate",
    "Citation",
    "CloneResult",
    "Memory",
    "SearchResult",
    "Tag",
    "AuthenticationError",
    "HippoDidError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
