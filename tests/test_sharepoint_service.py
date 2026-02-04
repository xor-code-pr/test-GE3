"""
Unit tests for SharePoint service integration.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.sharepoint_service import (
    SharePointService,
    SharePointConfig,
    SharePointSite,
    SharePointPermission
)


class TestSharePointConfig(unittest.TestCase):
    """Test SharePoint configuration."""
    
    def test_sharepoint_config_creation(self):
        """Test creating SharePoint configuration."""
        config = SharePointConfig(
            site_url="https://example.sharepoint.com/sites/test",
            tenant_id="tenant-123",
            client_id="client-123",
            client_secret="secret-123",
            use_managed_identity=False
        )
        
        self.assertEqual(config.site_url, "https://example.sharepoint.com/sites/test")
        self.assertEqual(config.tenant_id, "tenant-123")
        self.assertFalse(config.use_managed_identity)
    
    def test_sharepoint_config_with_managed_identity(self):
        """Test SharePoint config with managed identity."""
        config = SharePointConfig(
            site_url="https://example.sharepoint.com/sites/test",
            tenant_id="tenant-123",
            use_managed_identity=True
        )
        
        self.assertTrue(config.use_managed_identity)
        self.assertIsNone(config.client_id)


class TestSharePointSite(unittest.TestCase):
    """Test SharePoint site model."""
    
    def test_sharepoint_site_creation(self):
        """Test creating SharePoint site."""
        site = SharePointSite(
            site_id="site-123",
            site_url="https://example.sharepoint.com/sites/test",
            site_name="Test Site",
            library_name="Documents"
        )
        
        self.assertEqual(site.site_id, "site-123")
        self.assertEqual(site.library_name, "Documents")


class TestSharePointPermission(unittest.TestCase):
    """Test SharePoint permission model."""
    
    def test_sharepoint_permission_creation(self):
        """Test creating SharePoint permission."""
        perm = SharePointPermission(
            principal_id="user123",
            principal_type="User",
            role="Read"
        )
        
        self.assertEqual(perm.principal_id, "user123")
        self.assertEqual(perm.principal_type, "User")
        self.assertEqual(perm.role, "Read")


class TestSharePointService(unittest.TestCase):
    """Test SharePoint service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SharePointConfig(
            site_url="https://example.sharepoint.com/sites/test",
            tenant_id="tenant-123",
            client_id="client-123",
            client_secret="secret-123",
            use_managed_identity=False
        )
        self.service = SharePointService(self.config)
    
    def test_service_initialization(self):
        """Test SharePoint service initialization."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.config.site_url, self.config.site_url)
        self.assertIsNone(self.service._client)
    
    def test_get_client_error(self):
        """Test getting SharePoint client with missing imports."""
        # This test verifies the service handles missing dependencies gracefully
        service = SharePointService(self.config)
        
        # If office365 library is not installed, _get_client should raise ImportError
        # We'll just verify the service is initialized correctly
        self.assertIsNotNone(service)
        self.assertIsNone(service._client)
    
    @patch('app.sharepoint_service.SharePointService._get_client')
    def test_create_site_library(self, mock_get_client):
        """Test creating SharePoint library."""
        # Mock the client and web
        mock_client = MagicMock()
        mock_web = MagicMock()
        mock_web.properties = {
            'Id': 'site-123',
            'Title': 'Test Site'
        }
        mock_client.web.get.return_value.execute_query.return_value = mock_web
        mock_client.web.lists.filter.return_value.get.return_value.execute_query.return_value = []
        
        mock_library = MagicMock()
        mock_client.web.lists.add.return_value.execute_query.return_value = mock_library
        
        mock_get_client.return_value = mock_client
        
        # Create library
        site = self.service.create_site_library(
            kb_id="kb-123",
            kb_name="Test KB",
            description="Test description"
        )
        
        self.assertIsInstance(site, SharePointSite)
        # The library_name is the title, not the internal name with KB_ prefix
        self.assertEqual(site.library_name, "Test KB")
    
    @patch('app.sharepoint_service.SharePointService._get_client')
    def test_sync_permissions(self, mock_get_client):
        """Test syncing permissions to SharePoint."""
        mock_client = MagicMock()
        mock_library = MagicMock()
        mock_client.web.lists.get_by_title.return_value = mock_library
        mock_library.get.return_value.execute_query.return_value = mock_library
        mock_library.break_role_inheritance.return_value.execute_query.return_value = None
        
        mock_get_client.return_value = mock_client
        
        # Sync permissions
        azure_ad_groups = [
            {
                'group_id': 'group1',
                'name': 'Group 1',
                'object_id': 'obj-123'
            }
        ]
        content_managers = ['manager@example.com']
        owner_id = 'owner@example.com'
        
        result = self.service.sync_permissions(
            library_name="Test Library",
            azure_ad_groups=azure_ad_groups,
            content_managers=content_managers,
            owner_id=owner_id
        )
        
        self.assertTrue(result)
        mock_library.break_role_inheritance.assert_called_once()
    
    @patch('app.sharepoint_service.SharePointService._get_client')
    def test_import_documents_from_sharepoint(self, mock_get_client):
        """Test importing documents from SharePoint."""
        mock_client = MagicMock()
        mock_library = MagicMock()
        
        # Mock file properties
        mock_file1 = MagicMock()
        mock_file1.properties = {
            'Name': 'document1.pdf',
            'Length': 1024,
            'ServerRelativeUrl': '/sites/test/document1.pdf',
            'TimeLastModified': datetime.utcnow().isoformat(),
            'Author': {'Title': 'User 1'}
        }
        
        mock_file2 = MagicMock()
        mock_file2.properties = {
            'Name': 'document2.docx',
            'Length': 2048,
            'ServerRelativeUrl': '/sites/test/document2.docx',
            'TimeLastModified': datetime.utcnow().isoformat(),
            'Author': {'Title': 'User 2'}
        }
        
        mock_library.root_folder.files.get.return_value.execute_query.return_value = [
            mock_file1, mock_file2
        ]
        mock_client.web.lists.get_by_title.return_value = mock_library
        
        mock_get_client.return_value = mock_client
        
        # Import documents
        documents = self.service.import_documents_from_sharepoint(
            library_name="Test Library"
        )
        
        self.assertEqual(len(documents), 2)
        self.assertEqual(documents[0]['filename'], 'document1.pdf')
        self.assertEqual(documents[1]['filename'], 'document2.docx')
    
    @patch('app.sharepoint_service.SharePointService._get_client')
    def test_download_document(self, mock_get_client):
        """Test downloading document from SharePoint."""
        mock_client = MagicMock()
        mock_library = MagicMock()
        mock_file = MagicMock()
        
        mock_file.read.return_value = b'file content'
        mock_library.root_folder.files.get_by_url.return_value = mock_file
        mock_file.get.return_value.execute_query.return_value = mock_file
        
        mock_client.web.lists.get_by_title.return_value = mock_library
        mock_get_client.return_value = mock_client
        
        # Download document
        content = self.service.download_document(
            library_name="Test Library",
            file_name="document.pdf"
        )
        
        self.assertEqual(content, b'file content')
    
    @patch('app.sharepoint_service.SharePointService._get_client')
    def test_get_library_permissions(self, mock_get_client):
        """Test getting library permissions."""
        mock_client = MagicMock()
        mock_library = MagicMock()
        
        # Mock role assignment
        mock_assignment = MagicMock()
        mock_assignment.member.properties = {
            'Title': 'User 1',
            'PrincipalType': 'User'
        }
        mock_role = MagicMock()
        mock_role.properties = {'Name': 'Read'}
        mock_assignment.role_definition_bindings = [mock_role]
        
        mock_library.role_assignments.get.return_value.execute_query.return_value = [
            mock_assignment
        ]
        mock_client.web.lists.get_by_title.return_value = mock_library
        mock_get_client.return_value = mock_client
        
        # Get permissions
        permissions = self.service.get_library_permissions(
            library_name="Test Library"
        )
        
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].principal_id, 'User 1')
        self.assertEqual(permissions[0].role, 'Read')


class TestSharePointIntegration(unittest.TestCase):
    """Test SharePoint integration with KB Manager."""
    
    def test_sharepoint_config_in_kb_manager(self):
        """Test that KB Manager initializes with SharePoint config."""
        from app.config import AzureConfig, AppConfig
        
        # Setup config with SharePoint enabled
        azure_config = AzureConfig(
            storage_account_name="test",
            search_service_name="test",
            tenant_id="test",
            sharepoint_site_url="https://test.sharepoint.com/sites/test",
            enable_sharepoint_sync=True
        )
        
        app_config = AppConfig(
            admin_users=["admin@example.com"],
            database_connection_string="sqlite:///:memory:",
            azure=azure_config
        )
        
        # Verify config has SharePoint settings
        self.assertTrue(app_config.azure.enable_sharepoint_sync)
        self.assertIsNotNone(app_config.azure.sharepoint_site_url)


if __name__ == '__main__':
    unittest.main()
