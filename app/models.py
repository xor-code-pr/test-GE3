"""
Data models for the Knowledge Management application.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class AccessLevel(Enum):
    """Access levels for knowledge bases."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str
    email: str
    name: str
    is_admin: bool = False
    azure_ad_object_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AzureADGroup:
    """Represents an Azure AD group."""
    group_id: str
    name: str
    object_id: str


@dataclass
class AccessPolicy:
    """Access policy for a knowledge base."""
    azure_ad_group: AzureADGroup
    access_level: AccessLevel
    content_managers: List[str] = field(default_factory=list)  # List of user_ids


@dataclass
class KnowledgeBase:
    """Represents a knowledge base."""
    kb_id: str
    name: str
    description: str
    owner_id: str
    blob_container_name: str
    search_index_name: str
    access_policies: List[AccessPolicy] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Document:
    """Represents a document in a knowledge base."""
    document_id: str
    kb_id: str
    filename: str
    blob_path: str
    content_type: str
    size_bytes: int
    uploaded_by: str
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    indexed: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class SearchResult:
    """Represents a search result."""
    document_id: str
    filename: str
    score: float
    highlights: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
