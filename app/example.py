"""
Example usage of the Knowledge Management System.
"""

from app.main import KnowledgeManagementApp
from app.config import AppConfig, AzureConfig


def example_usage():
    """Demonstrate the usage of the Knowledge Management System."""
    
    # Create configuration
    azure_config = AzureConfig(
        storage_account_name="your_storage_account",
        storage_account_key="your_storage_key",
        search_service_name="your_search_service",
        search_admin_key="your_search_key",
        tenant_id="your_tenant_id",
        use_managed_identity=False  # Set to True in production
    )
    
    app_config = AppConfig(
        admin_users=["admin@example.com", "superuser@example.com"],
        database_connection_string="sqlite:///kb.db",
        azure=azure_config
    )
    
    # Initialize application
    app = KnowledgeManagementApp(config=app_config)
    
    # Create users
    admin = app.create_user(
        user_id="admin",
        email="admin@example.com",
        name="Admin User",
        is_admin=True,
        azure_ad_object_id="admin-object-id"
    )
    
    user1 = app.create_user(
        user_id="user1",
        email="user1@example.com",
        name="Regular User",
        azure_ad_object_id="user1-object-id"
    )
    
    # Create a knowledge base with Azure AD group access
    kb = app.create_knowledge_base(
        name="Engineering Documentation",
        description="Documentation for the engineering team",
        owner_id="admin",
        azure_ad_groups=[
            {
                'group_id': 'eng-group',
                'name': 'Engineering Team',
                'object_id': 'azure-ad-group-object-id',
                'content_managers': ['user1']  # user1 can manage content
            }
        ]
    )
    
    print(f"Created KB: {kb.name} (ID: {kb.kb_id})")
    
    # Upload a document (admin is a default content manager)
    with open('example.txt', 'w') as f:
        f.write('This is an example document for the knowledge base.')
    
    with open('example.txt', 'rb') as f:
        doc = app.upload_document(
            kb_id=kb.kb_id,
            filename='example.txt',
            file_data=f.read(),
            content_type='text/plain',
            uploaded_by='admin',
            metadata={'category': 'documentation'}
        )
    
    print(f"Uploaded document: {doc.filename}")
    
    # Search the knowledge base
    results = app.search(
        kb_id=kb.kb_id,
        query="example",
        user_id="admin"
    )
    
    print(f"Search results: {len(results)}")
    for result in results:
        print(f"  - {result.filename} (score: {result.score})")
    
    # List accessible knowledge bases for a user
    user_kbs = app.list_knowledge_bases("user1")
    print(f"User1 has access to {len(user_kbs)} knowledge bases")


if __name__ == "__main__":
    example_usage()
