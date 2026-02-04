"""
Main application entry point for the Knowledge Management System.
"""

import logging
from typing import Optional

from .config import load_config_from_env, AppConfig
from .blob_storage import BlobStorageService
from .search_service import SearchService
from .kb_manager import KnowledgeBaseManager
from .models import User, KnowledgeBase, AccessPolicy, AzureADGroup, AccessLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeManagementApp:
    """Main application class for Knowledge Management System."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize the application."""
        self.config = config or load_config_from_env()
        
        # Initialize services
        self.blob_service = BlobStorageService(self.config.azure)
        self.search_service = SearchService(self.config.azure)
        self.kb_manager = KnowledgeBaseManager(
            config=self.config,
            blob_service=self.blob_service,
            search_service=self.search_service
        )
        
        logger.info("Knowledge Management Application initialized")
    
    def create_user(
        self,
        user_id: str,
        email: str,
        name: str,
        is_admin: bool = False,
        azure_ad_object_id: Optional[str] = None
    ) -> User:
        """Create a new user."""
        user = User(
            user_id=user_id,
            email=email,
            name=name,
            is_admin=is_admin,
            azure_ad_object_id=azure_ad_object_id
        )
        self.kb_manager.users[user_id] = user
        logger.info(f"Created user: {email}")
        return user
    
    def create_knowledge_base(
        self,
        name: str,
        description: str,
        owner_id: str,
        azure_ad_groups: Optional[list] = None
    ) -> KnowledgeBase:
        """
        Create a new knowledge base with access policies.
        
        Args:
            name: Name of the knowledge base
            description: Description of the knowledge base
            owner_id: User ID of the owner
            azure_ad_groups: List of dicts with group info and content managers
                            Example: [{'group_id': 'g1', 'name': 'Group1', 
                                      'object_id': 'obj1', 'content_managers': ['user1']}]
        """
        access_policies = []
        
        if azure_ad_groups:
            for group_info in azure_ad_groups:
                azure_ad_group = AzureADGroup(
                    group_id=group_info['group_id'],
                    name=group_info['name'],
                    object_id=group_info['object_id']
                )
                policy = AccessPolicy(
                    azure_ad_group=azure_ad_group,
                    access_level=AccessLevel.READ,
                    content_managers=group_info.get('content_managers', [])
                )
                access_policies.append(policy)
        
        return self.kb_manager.create_knowledge_base(
            name=name,
            description=description,
            owner_id=owner_id,
            access_policies=access_policies
        )
    
    def upload_document(
        self,
        kb_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
        uploaded_by: str,
        metadata: Optional[dict] = None
    ):
        """Upload a document to a knowledge base."""
        return self.kb_manager.upload_document(
            kb_id=kb_id,
            filename=filename,
            file_data=file_data,
            content_type=content_type,
            uploaded_by=uploaded_by,
            metadata=metadata
        )
    
    def search(self, kb_id: str, query: str, user_id: str):
        """Search documents in a knowledge base."""
        return self.kb_manager.search_knowledge_base(
            kb_id=kb_id,
            query=query,
            user_id=user_id
        )
    
    def list_knowledge_bases(self, user_id: str):
        """List all knowledge bases accessible by a user."""
        return self.kb_manager.list_knowledge_bases(user_id)
    
    def import_from_sharepoint(self, kb_id: str, imported_by: str):
        """Import documents from SharePoint to a knowledge base."""
        return self.kb_manager.import_from_sharepoint(kb_id, imported_by)


def main():
    """Main entry point for CLI usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m app.main <command>")
        print("Commands: create_kb, upload, search")
        sys.exit(1)
    
    app = KnowledgeManagementApp()
    command = sys.argv[1]
    
    if command == "create_kb":
        kb = app.create_knowledge_base(
            name="Example KB",
            description="An example knowledge base",
            owner_id="admin"
        )
        print(f"Created knowledge base: {kb.kb_id}")
    
    elif command == "upload":
        if len(sys.argv) < 4:
            print("Usage: python -m app.main upload <kb_id> <file_path>")
            sys.exit(1)
        
        kb_id = sys.argv[2]
        file_path = sys.argv[3]
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        doc = app.upload_document(
            kb_id=kb_id,
            filename=file_path.split('/')[-1],
            file_data=file_data,
            content_type="application/octet-stream",
            uploaded_by="admin"
        )
        print(f"Uploaded document: {doc.document_id}")
    
    elif command == "search":
        if len(sys.argv) < 4:
            print("Usage: python -m app.main search <kb_id> <query>")
            sys.exit(1)
        
        kb_id = sys.argv[2]
        query = sys.argv[3]
        
        results = app.search(kb_id, query, "admin")
        print(f"Found {len(results)} results:")
        for result in results:
            print(f"  - {result.filename} (score: {result.score})")


if __name__ == "__main__":
    main()
