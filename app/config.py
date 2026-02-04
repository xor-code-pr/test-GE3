"""
Configuration management for the Knowledge Management application.
"""

import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class OpenAIConfig:
    """OpenAI configuration for RAG."""
    api_key: str
    model: str = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"
    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class AzureConfig:
    """Azure service configuration."""
    # Required fields
    storage_account_name: str
    search_service_name: str
    tenant_id: str
    
    # Azure Storage (optional)
    storage_account_key: Optional[str] = None
    storage_connection_string: Optional[str] = None
    
    # Azure AI Search (optional)
    search_admin_key: Optional[str] = None
    search_endpoint: Optional[str] = None
    
    # Azure AD (optional)
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # SharePoint configuration (optional)
    sharepoint_site_url: Optional[str] = None
    sharepoint_tenant_id: Optional[str] = None
    sharepoint_client_id: Optional[str] = None
    sharepoint_client_secret: Optional[str] = None
    enable_sharepoint_sync: bool = False
    
    # Managed Identity
    use_managed_identity: bool = True
    
    def __post_init__(self):
        """Set default values from config."""
        if not self.storage_connection_string and self.storage_account_name:
            if self.storage_account_key:
                self.storage_connection_string = (
                    f"DefaultEndpointsProtocol=https;"
                    f"AccountName={self.storage_account_name};"
                    f"AccountKey={self.storage_account_key};"
                    f"EndpointSuffix=core.windows.net"
                )
        
        if not self.search_endpoint:
            self.search_endpoint = f"https://{self.search_service_name}.search.windows.net"
        
        # Use same tenant_id for SharePoint if not specified
        if not self.sharepoint_tenant_id and self.tenant_id:
            self.sharepoint_tenant_id = self.tenant_id
        
        # Use same client credentials for SharePoint if not specified
        if not self.sharepoint_client_id and self.client_id:
            self.sharepoint_client_id = self.client_id
        if not self.sharepoint_client_secret and self.client_secret:
            self.sharepoint_client_secret = self.client_secret


@dataclass
class AppConfig:
    """Application configuration."""
    # Admin users (default content managers for all KBs)
    admin_users: List[str]
    
    # Database configuration
    database_connection_string: str
    
    # Azure configuration
    azure: AzureConfig
    
    # OpenAI configuration
    openai: Optional[OpenAIConfig] = None
    
    # Application settings
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = None
    
    # RAG settings
    enable_rag: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    def __post_init__(self):
        """Set default allowed file types."""
        if self.allowed_file_types is None:
            self.allowed_file_types = [
                '.pdf', '.docx', '.doc', '.txt', '.md',
                '.pptx', '.ppt', '.xlsx', '.xls', '.csv'
            ]


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables."""
    admin_users_str = os.getenv('ADMIN_USERS', '')
    admin_users = [u.strip() for u in admin_users_str.split(',') if u.strip()]
    
    azure_config = AzureConfig(
        storage_account_name=os.getenv('AZURE_STORAGE_ACCOUNT_NAME', ''),
        storage_account_key=os.getenv('AZURE_STORAGE_ACCOUNT_KEY'),
        storage_connection_string=os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
        search_service_name=os.getenv('AZURE_SEARCH_SERVICE_NAME', ''),
        search_admin_key=os.getenv('AZURE_SEARCH_ADMIN_KEY'),
        search_endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
        tenant_id=os.getenv('AZURE_TENANT_ID', ''),
        client_id=os.getenv('AZURE_CLIENT_ID'),
        client_secret=os.getenv('AZURE_CLIENT_SECRET'),
        # SharePoint configuration
        sharepoint_site_url=os.getenv('SHAREPOINT_SITE_URL'),
        sharepoint_tenant_id=os.getenv('SHAREPOINT_TENANT_ID'),
        sharepoint_client_id=os.getenv('SHAREPOINT_CLIENT_ID'),
        sharepoint_client_secret=os.getenv('SHAREPOINT_CLIENT_SECRET'),
        enable_sharepoint_sync=os.getenv('ENABLE_SHAREPOINT_SYNC', 'false').lower() == 'true',
        use_managed_identity=os.getenv('USE_MANAGED_IDENTITY', 'true').lower() == 'true'
    )
    
    # OpenAI configuration
    openai_config = None
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        openai_config = OpenAIConfig(
            api_key=openai_api_key,
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            embedding_model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002'),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        )
    
    return AppConfig(
        admin_users=admin_users,
        database_connection_string=os.getenv('DATABASE_CONNECTION_STRING', 'sqlite:///knowledge_base.db'),
        azure=azure_config,
        openai=openai_config,
        max_file_size_mb=int(os.getenv('MAX_FILE_SIZE_MB', '100')),
        enable_rag=os.getenv('ENABLE_RAG', 'true').lower() == 'true',
        chunk_size=int(os.getenv('CHUNK_SIZE', '1000')),
        chunk_overlap=int(os.getenv('CHUNK_OVERLAP', '200')),
        top_k_results=int(os.getenv('TOP_K_RESULTS', '5'))
    )
