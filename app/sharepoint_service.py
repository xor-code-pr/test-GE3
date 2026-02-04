"""
SharePoint service for integrating with Microsoft SharePoint Online.

This service handles:
- SharePoint site and library management
- Permission synchronization between KB access policies and SharePoint
- Document import from SharePoint to Azure Blob Storage
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SharePointConfig:
    """Configuration for SharePoint connection."""
    site_url: str
    tenant_id: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    use_managed_identity: bool = False


@dataclass
class SharePointSite:
    """Represents a SharePoint site."""
    site_id: str
    site_url: str
    site_name: str
    library_name: str = "Documents"


@dataclass
class SharePointPermission:
    """Represents a SharePoint permission assignment."""
    principal_id: str  # User or group ID
    principal_type: str  # "User" or "Group"
    role: str  # "Read", "Contribute", "Edit", "FullControl"


class SharePointService:
    """Service for interacting with SharePoint Online."""
    
    def __init__(self, config: SharePointConfig):
        """
        Initialize the SharePoint service.
        
        Args:
            config: SharePoint configuration
        """
        self.config = config
        self._client = None
        logger.info("SharePoint service initialized")
    
    def _get_client(self):
        """Get or create the SharePoint client."""
        if self._client is None:
            try:
                from office365.runtime.auth.client_credential import ClientCredential
                from office365.sharepoint.client_context import ClientContext
                
                if self.config.use_managed_identity:
                    # Use managed identity for authentication
                    from azure.identity import ManagedIdentityCredential
                    credential = ManagedIdentityCredential()
                    # Note: Office365-REST-Python-Client doesn't directly support managed identity
                    # In production, use Microsoft Graph API with managed identity
                    logger.warning("Managed identity not fully supported by office365 library. "
                                 "Consider using Microsoft Graph API.")
                    # Fallback to client credentials
                    if not self.config.client_id or not self.config.client_secret:
                        raise ValueError("Client credentials required when managed identity is not available")
                    credentials = ClientCredential(self.config.client_id, self.config.client_secret)
                else:
                    if not self.config.client_id or not self.config.client_secret:
                        raise ValueError("Client ID and secret required for authentication")
                    credentials = ClientCredential(self.config.client_id, self.config.client_secret)
                
                self._client = ClientContext(self.config.site_url).with_credentials(credentials)
                logger.info("SharePoint client created successfully")
            except ImportError:
                logger.error("Office365-REST-Python-Client not installed. Install with: pip install Office365-REST-Python-Client")
                raise
            except Exception as e:
                logger.error(f"Failed to create SharePoint client: {e}")
                raise
        
        return self._client
    
    def create_site_library(
        self,
        kb_id: str,
        kb_name: str,
        description: str
    ) -> SharePointSite:
        """
        Create a document library for a knowledge base.
        
        Args:
            kb_id: Knowledge base ID
            kb_name: Knowledge base name
            description: Description of the knowledge base
            
        Returns:
            SharePointSite object with library information
            
        Raises:
            Exception: If library creation fails
        
        Note:
            The library_name (internal name) uses 'KB_' + first 8 chars of kb_id
            for uniqueness, while the library title uses the full kb_name for
            better user experience in SharePoint UI.
        """
        try:
            client = self._get_client()
            web = client.web.get().execute_query()
            
            # Create a new document library
            library_name = f"KB_{kb_id[:8]}"  # Shortened ID for library internal name
            library_title = kb_name  # Full name for display title
            
            # Check if library already exists
            lists = client.web.lists.filter(f"Title eq '{library_name}'").get().execute_query()
            
            if len(lists) > 0:
                logger.info(f"Library {library_name} already exists")
                library = lists[0]
            else:
                # Create new document library
                library_creation_info = {
                    "Title": library_title,
                    "Description": description,
                    "TemplateType": 101  # Document Library template
                }
                library = client.web.lists.add(library_creation_info).execute_query()
                logger.info(f"Created SharePoint library: {library_name}")
            
            site = SharePointSite(
                site_id=web.properties['Id'],
                site_url=self.config.site_url,
                site_name=web.properties['Title'],
                library_name=library_title
            )
            
            return site
            
        except Exception as e:
            logger.error(f"Failed to create SharePoint library: {e}")
            # Re-raise the exception so calling code can handle it
            raise
    
    def sync_permissions(
        self,
        library_name: str,
        azure_ad_groups: List[Dict[str, Any]],
        content_managers: List[str],
        owner_id: str
    ) -> bool:
        """
        Synchronize permissions between KB access policies and SharePoint.
        
        Args:
            library_name: Name of the SharePoint library
            azure_ad_groups: List of Azure AD groups with access
            content_managers: List of content manager user IDs
            owner_id: Owner user ID
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            Exception: If permission sync fails critically
        """
        try:
            client = self._get_client()
            
            # Get the document library
            library = client.web.lists.get_by_title(library_name)
            library.get().execute_query()
            
            # Break role inheritance to set custom permissions
            library.break_role_inheritance(False).execute_query()
            
            # Add owner with full control
            self._add_permission(library, owner_id, "Full Control")
            
            # Add content managers with contribute permissions
            for manager in content_managers:
                self._add_permission(library, manager, "Contribute")
            
            # Add Azure AD groups with read permissions
            for group_info in azure_ad_groups:
                group_id = group_info.get('object_id') or group_info.get('group_id')
                self._add_group_permission(library, group_id, "Read")
            
            logger.info(f"Synchronized permissions for library: {library_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync permissions: {e}")
            # Return False to indicate failure but don't break the flow
            # Permissions can be set manually in SharePoint if sync fails
            return False
    
    def _add_permission(
        self,
        library,
        user_id: str,
        role: str
    ):
        """Add permission for a user to a library."""
        try:
            # Get user by email or ID
            user = self._client.web.site_users.get_by_email(user_id)
            
            # Get role definition
            role_def = self._client.web.role_definitions.get_by_name(role)
            
            # Create role assignment
            role_binding = library.role_assignments.add(user, role_def)
            role_binding.execute_query()
            
            logger.info(f"Added {role} permission for user {user_id}")
        except Exception as e:
            logger.warning(f"Could not add permission for {user_id}: {e}")
    
    def _add_group_permission(
        self,
        library,
        group_id: str,
        role: str
    ):
        """Add permission for an Azure AD group to a library."""
        try:
            # Get group by ID
            group = self._client.web.site_groups.get_by_name(group_id)
            
            # Get role definition
            role_def = self._client.web.role_definitions.get_by_name(role)
            
            # Create role assignment
            role_binding = library.role_assignments.add(group, role_def)
            role_binding.execute_query()
            
            logger.info(f"Added {role} permission for group {group_id}")
        except Exception as e:
            logger.warning(f"Could not add group permission for {group_id}: {e}")
    
    def import_documents_from_sharepoint(
        self,
        library_name: str,
        folder_path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Import documents from a SharePoint library.
        
        Args:
            library_name: Name of the SharePoint library
            folder_path: Optional folder path within the library
            
        Returns:
            List of document metadata dictionaries
        """
        try:
            client = self._get_client()
            
            # Get the document library
            library = client.web.lists.get_by_title(library_name)
            
            # Get files from the library
            if folder_path:
                folder = library.root_folder.folders.get_by_url(folder_path)
                files = folder.files.get().execute_query()
            else:
                files = library.root_folder.files.get().execute_query()
            
            documents = []
            for file in files:
                doc_info = {
                    'filename': file.properties['Name'],
                    'size': file.properties['Length'],
                    'url': file.properties['ServerRelativeUrl'],
                    'modified': file.properties['TimeLastModified'],
                    'author': file.properties.get('Author', {}).get('Title', 'Unknown')
                }
                documents.append(doc_info)
            
            logger.info(f"Found {len(documents)} documents in SharePoint library {library_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to import documents from SharePoint: {e}")
            return []
    
    def download_document(
        self,
        library_name: str,
        file_name: str
    ) -> Optional[bytes]:
        """
        Download a document from SharePoint.
        
        Args:
            library_name: Name of the SharePoint library
            file_name: Name of the file to download
            
        Returns:
            File content as bytes, or None if failed
        """
        try:
            client = self._get_client()
            
            # Get the file
            library = client.web.lists.get_by_title(library_name)
            file = library.root_folder.files.get_by_url(file_name)
            file.get().execute_query()
            
            # Download file content
            content = file.read()
            
            logger.info(f"Downloaded file {file_name} from SharePoint")
            return content
            
        except Exception as e:
            logger.error(f"Failed to download file {file_name}: {e}")
            return None
    
    def get_library_permissions(
        self,
        library_name: str
    ) -> List[SharePointPermission]:
        """
        Get current permissions for a SharePoint library.
        
        Args:
            library_name: Name of the SharePoint library
            
        Returns:
            List of SharePointPermission objects
        """
        try:
            client = self._get_client()
            
            # Get the document library
            library = client.web.lists.get_by_title(library_name)
            
            # Get role assignments
            role_assignments = library.role_assignments.get().execute_query()
            
            permissions = []
            for assignment in role_assignments:
                member = assignment.member
                roles = assignment.role_definition_bindings
                
                for role in roles:
                    permission = SharePointPermission(
                        principal_id=member.properties.get('Title', 'Unknown'),
                        principal_type=member.properties.get('PrincipalType', 'Unknown'),
                        role=role.properties.get('Name', 'Unknown')
                    )
                    permissions.append(permission)
            
            logger.info(f"Retrieved {len(permissions)} permissions for library {library_name}")
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get library permissions: {e}")
            return []
