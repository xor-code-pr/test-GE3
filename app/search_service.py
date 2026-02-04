"""
Azure AI Search service for indexing and searching documents.
"""

from typing import List, Dict, Optional, Any
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
import logging

from .config import AzureConfig
from .models import SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    """Service for managing Azure AI Search operations."""
    
    def __init__(self, config: AzureConfig):
        """Initialize the search service."""
        self.config = config
        self.credential = self._get_credential()
        self.index_client = SearchIndexClient(
            endpoint=config.search_endpoint,
            credential=self.credential
        )
        self.indexer_client = SearchIndexerClient(
            endpoint=config.search_endpoint,
            credential=self.credential
        )
    
    def _get_credential(self):
        """Get the appropriate credential based on configuration."""
        if self.config.use_managed_identity:
            return DefaultAzureCredential()
        else:
            return AzureKeyCredential(self.config.search_admin_key)
    
    def create_index(self, index_name: str) -> SearchIndex:
        """Create a search index for a knowledge base."""
        fields = [
            SimpleField(name="document_id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="filename", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="title", type=SearchFieldDataType.String, sortable=True),
            SimpleField(name="kb_id", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="blob_path", type=SearchFieldDataType.String),
            SimpleField(name="content_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="uploaded_by", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="uploaded_at", type=SearchFieldDataType.DateTimeOffset, sortable=True),
            SearchableField(name="metadata", type=SearchFieldDataType.String),
        ]
        
        index = SearchIndex(name=index_name, fields=fields)
        
        try:
            result = self.index_client.create_or_update_index(index)
            logger.info(f"Created/updated search index: {index_name}")
            return result
        except Exception as e:
            logger.error(f"Error creating search index {index_name}: {e}")
            raise
    
    def delete_index(self, index_name: str) -> None:
        """Delete a search index."""
        try:
            self.index_client.delete_index(index_name)
            logger.info(f"Deleted search index: {index_name}")
        except Exception as e:
            logger.error(f"Error deleting search index {index_name}: {e}")
            raise
    
    def create_indexer(
        self,
        indexer_name: str,
        index_name: str,
        data_source_name: str,
        container_name: str
    ) -> SearchIndexer:
        """Create an indexer for automatic document indexing."""
        try:
            # Create data source connection
            data_source = SearchIndexerDataSourceConnection(
                name=data_source_name,
                type="azureblob",
                connection_string=self.config.storage_connection_string,
                container=SearchIndexerDataContainer(name=container_name)
            )
            
            self.indexer_client.create_or_update_data_source_connection(data_source)
            
            # Create indexer
            indexer = SearchIndexer(
                name=indexer_name,
                data_source_name=data_source_name,
                target_index_name=index_name
            )
            
            result = self.indexer_client.create_or_update_indexer(indexer)
            logger.info(f"Created/updated indexer: {indexer_name}")
            return result
        except Exception as e:
            logger.error(f"Error creating indexer {indexer_name}: {e}")
            raise
    
    def run_indexer(self, indexer_name: str) -> None:
        """Run an indexer to index documents."""
        try:
            self.indexer_client.run_indexer(indexer_name)
            logger.info(f"Started indexer: {indexer_name}")
        except Exception as e:
            logger.error(f"Error running indexer {indexer_name}: {e}")
            raise
    
    def index_document(self, index_name: str, document: Dict[str, Any]) -> None:
        """Index a single document."""
        try:
            search_client = SearchClient(
                endpoint=self.config.search_endpoint,
                index_name=index_name,
                credential=self.credential
            )
            search_client.upload_documents(documents=[document])
            logger.info(f"Indexed document: {document.get('document_id')}")
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            raise
    
    def search(
        self,
        index_name: str,
        query: str,
        filters: Optional[str] = None,
        top: int = 10
    ) -> List[SearchResult]:
        """Search documents in an index."""
        try:
            search_client = SearchClient(
                endpoint=self.config.search_endpoint,
                index_name=index_name,
                credential=self.credential
            )
            
            results = search_client.search(
                search_text=query,
                filter=filters,
                top=top,
                include_total_count=True
            )
            
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    document_id=result.get('document_id', ''),
                    filename=result.get('filename', ''),
                    score=result.get('@search.score', 0.0),
                    highlights=result.get('@search.highlights', []),
                    metadata={
                        'kb_id': result.get('kb_id'),
                        'content_type': result.get('content_type'),
                        'uploaded_by': result.get('uploaded_by'),
                        'uploaded_at': result.get('uploaded_at')
                    }
                ))
            
            return search_results
        except Exception as e:
            logger.error(f"Error searching index {index_name}: {e}")
            raise
