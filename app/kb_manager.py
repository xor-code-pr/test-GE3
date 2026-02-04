"""
Knowledge base manager for creating and managing knowledge bases.
"""

import uuid
import logging
from typing import List, Optional
from datetime import datetime

from .models import KnowledgeBase, AccessPolicy, User, Document
from .blob_storage import BlobStorageService
from .search_service import SearchService
from .config import AppConfig

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Manager for knowledge base operations."""
    
    def __init__(
        self,
        config: AppConfig,
        blob_service: BlobStorageService,
        search_service: SearchService
    ):
        """Initialize the knowledge base manager."""
        self.config = config
        self.blob_service = blob_service
        self.search_service = search_service
        self.knowledge_bases = {}  # In-memory storage (use database in production)
        self.users = {}  # In-memory storage (use database in production)
    
    def create_knowledge_base(
        self,
        name: str,
        description: str,
        owner_id: str,
        access_policies: Optional[List[AccessPolicy]] = None
    ) -> KnowledgeBase:
        """Create a new knowledge base."""
        kb_id = str(uuid.uuid4())
        container_name = f"kb-{kb_id.replace('-', '')[:20]}"
        index_name = f"kb-index-{kb_id.replace('-', '')[:20]}"
        
        # Create blob container
        self.blob_service.create_container(container_name)
        
        # Create search index
        self.search_service.create_index(index_name)
        
        # Create indexer for automatic indexing
        indexer_name = f"indexer-{kb_id.replace('-', '')[:20]}"
        data_source_name = f"datasource-{kb_id.replace('-', '')[:20]}"
        
        try:
            self.search_service.create_indexer(
                indexer_name=indexer_name,
                index_name=index_name,
                data_source_name=data_source_name,
                container_name=container_name
            )
        except Exception as e:
            logger.warning(f"Could not create indexer (may require additional config): {e}")
        
        # Create knowledge base
        kb = KnowledgeBase(
            kb_id=kb_id,
            name=name,
            description=description,
            owner_id=owner_id,
            blob_container_name=container_name,
            search_index_name=index_name,
            access_policies=access_policies or []
        )
        
        self.knowledge_bases[kb_id] = kb
        logger.info(f"Created knowledge base: {name} (ID: {kb_id})")
        
        return kb
    
    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """Get a knowledge base by ID."""
        return self.knowledge_bases.get(kb_id)
    
    def list_knowledge_bases(self, user_id: str) -> List[KnowledgeBase]:
        """List all knowledge bases accessible by a user."""
        accessible_kbs = []
        user = self.users.get(user_id)
        
        for kb in self.knowledge_bases.values():
            # Owner can always access
            if kb.owner_id == user_id:
                accessible_kbs.append(kb)
                continue
            
            # Admin users can access all
            if user and user.is_admin:
                accessible_kbs.append(kb)
                continue
            
            # Check access policies
            if user and user.azure_ad_object_id:
                for policy in kb.access_policies:
                    # Simplified check (in production, verify AD group membership)
                    accessible_kbs.append(kb)
                    break
        
        return accessible_kbs
    
    def update_access_policies(
        self,
        kb_id: str,
        access_policies: List[AccessPolicy]
    ) -> KnowledgeBase:
        """Update access policies for a knowledge base."""
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            raise ValueError(f"Knowledge base not found: {kb_id}")
        
        kb.access_policies = access_policies
        kb.updated_at = datetime.utcnow()
        
        logger.info(f"Updated access policies for KB: {kb_id}")
        return kb
    
    def is_content_manager(self, kb_id: str, user_id: str) -> bool:
        """Check if a user is a content manager for a knowledge base."""
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            return False
        
        # Admins are always content managers
        if user_id in self.config.admin_users:
            return True
        
        # KB owner is always a content manager
        if kb.owner_id == user_id:
            return True
        
        # Check if user is designated content manager in any policy
        for policy in kb.access_policies:
            if user_id in policy.content_managers:
                return True
        
        return False
    
    def upload_document(
        self,
        kb_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
        uploaded_by: str,
        metadata: Optional[dict] = None
    ) -> Document:
        """Upload a document to a knowledge base."""
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            raise ValueError(f"Knowledge base not found: {kb_id}")
        
        # Check if user is authorized
        if not self.is_content_manager(kb_id, uploaded_by):
            raise PermissionError(f"User {uploaded_by} is not authorized to upload to KB {kb_id}")
        
        document_id = str(uuid.uuid4())
        blob_name = f"{document_id}/{filename}"
        
        # Upload to blob storage
        from io import BytesIO
        self.blob_service.upload_file(
            container_name=kb.blob_container_name,
            blob_name=blob_name,
            data=BytesIO(file_data),
            content_type=content_type,
            metadata=metadata
        )
        
        # Create document record
        document = Document(
            document_id=document_id,
            kb_id=kb_id,
            filename=filename,
            blob_path=blob_name,
            content_type=content_type,
            size_bytes=len(file_data),
            uploaded_by=uploaded_by,
            metadata=metadata or {}
        )
        
        # Index the document
        try:
            self.search_service.index_document(
                index_name=kb.search_index_name,
                document={
                    'document_id': document_id,
                    'filename': filename,
                    'content': '',  # Extract content in production
                    'title': filename,
                    'kb_id': kb_id,
                    'blob_path': blob_name,
                    'content_type': content_type,
                    'uploaded_by': uploaded_by,
                    'uploaded_at': document.uploaded_at.isoformat(),
                    'metadata': str(metadata or {})
                }
            )
            document.indexed = True
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
        
        logger.info(f"Uploaded document: {filename} to KB: {kb_id}")
        return document
    
    def search_knowledge_base(
        self,
        kb_id: str,
        query: str,
        user_id: str
    ) -> List:
        """Search documents in a knowledge base."""
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            raise ValueError(f"Knowledge base not found: {kb_id}")
        
        # Check if user has access (simplified)
        accessible_kbs = self.list_knowledge_bases(user_id)
        if kb not in accessible_kbs:
            raise PermissionError(f"User {user_id} does not have access to KB {kb_id}")
        
        return self.search_service.search(
            index_name=kb.search_index_name,
            query=query,
            filters=f"kb_id eq '{kb_id}'"
        )
