"""
Configuration management for the Knowledge Management application.
"""

import os
from typing import List, Optional
from dataclasses import dataclass


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


@dataclass
class AppConfig:
    """Application configuration."""
    # Admin users (default content managers for all KBs)
    admin_users: List[str]
    
    # Database configuration
    database_connection_string: str
    
    # Azure configuration
    azure: AzureConfig
    
    # Application settings
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = None
    
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
        use_managed_identity=os.getenv('USE_MANAGED_IDENTITY', 'true').lower() == 'true'
    )
    
    return AppConfig(
        admin_users=admin_users,
        database_connection_string=os.getenv('DATABASE_CONNECTION_STRING', 'sqlite:///knowledge_base.db'),
        azure=azure_config,
        max_file_size_mb=int(os.getenv('MAX_FILE_SIZE_MB', '100'))
    )
