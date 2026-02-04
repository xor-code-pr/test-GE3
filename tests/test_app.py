"""
Unit tests for the Knowledge Management application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.models import (
    User, KnowledgeBase, AccessPolicy, AzureADGroup,
    AccessLevel, Document, SearchResult
)
from app.config import AzureConfig, AppConfig


class TestModels(unittest.TestCase):
    """Test data models."""
    
    def test_user_creation(self):
        """Test creating a user."""
        user = User(
            user_id="user1",
            email="user1@example.com",
            name="User One",
            is_admin=False
        )
        
        self.assertEqual(user.user_id, "user1")
        self.assertEqual(user.email, "user1@example.com")
        self.assertFalse(user.is_admin)
        self.assertIsInstance(user.created_at, datetime)
    
    def test_knowledge_base_creation(self):
        """Test creating a knowledge base."""
        kb = KnowledgeBase(
            kb_id="kb1",
            name="Test KB",
            description="A test knowledge base",
            owner_id="user1",
            blob_container_name="kb-container",
            search_index_name="kb-index"
        )
        
        self.assertEqual(kb.kb_id, "kb1")
        self.assertEqual(kb.name, "Test KB")
        self.assertEqual(kb.owner_id, "user1")
        self.assertEqual(len(kb.access_policies), 0)
    
    def test_access_policy_creation(self):
        """Test creating an access policy."""
        group = AzureADGroup(
            group_id="group1",
            name="Test Group",
            object_id="obj123"
        )
        
        policy = AccessPolicy(
            azure_ad_group=group,
            access_level=AccessLevel.READ,
            content_managers=["user1", "user2"]
        )
        
        self.assertEqual(policy.azure_ad_group.group_id, "group1")
        self.assertEqual(policy.access_level, AccessLevel.READ)
        self.assertEqual(len(policy.content_managers), 2)
    
    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            document_id="doc1",
            kb_id="kb1",
            filename="test.pdf",
            blob_path="path/to/test.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            uploaded_by="user1"
        )
        
        self.assertEqual(doc.document_id, "doc1")
        self.assertEqual(doc.kb_id, "kb1")
        self.assertFalse(doc.indexed)


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_azure_config_creation(self):
        """Test creating Azure configuration."""
        config = AzureConfig(
            storage_account_name="teststorage",
            search_service_name="testsearch",
            tenant_id="tenant123"
        )
        
        self.assertEqual(config.storage_account_name, "teststorage")
        self.assertEqual(config.search_service_name, "testsearch")
        self.assertTrue(config.use_managed_identity)
        self.assertEqual(
            config.search_endpoint,
            "https://testsearch.search.windows.net"
        )
    
    def test_app_config_defaults(self):
        """Test application configuration defaults."""
        azure_config = AzureConfig(
            storage_account_name="test",
            search_service_name="test",
            tenant_id="test"
        )
        
        app_config = AppConfig(
            admin_users=["admin@test.com"],
            database_connection_string="sqlite:///test.db",
            azure=azure_config
        )
        
        self.assertEqual(len(app_config.admin_users), 1)
        self.assertEqual(app_config.max_file_size_mb, 100)
        self.assertIsNotNone(app_config.allowed_file_types)
        self.assertIn('.pdf', app_config.allowed_file_types)


class TestKnowledgeBaseManager(unittest.TestCase):
    """Test knowledge base manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        from app.kb_manager import KnowledgeBaseManager
        
        self.azure_config = AzureConfig(
            storage_account_name="test",
            search_service_name="test",
            tenant_id="test"
        )
        
        self.app_config = AppConfig(
            admin_users=["admin@test.com"],
            database_connection_string="sqlite:///test.db",
            azure=self.azure_config
        )
        
        # Create mock services
        self.blob_service = Mock()
        self.search_service = Mock()
        
        self.manager = KnowledgeBaseManager(
            config=self.app_config,
            blob_service=self.blob_service,
            search_service=self.search_service
        )
    
    def test_create_knowledge_base(self):
        """Test creating a knowledge base."""
        kb = self.manager.create_knowledge_base(
            name="Test KB",
            description="Test description",
            owner_id="user1"
        )
        
        self.assertIsNotNone(kb)
        self.assertEqual(kb.name, "Test KB")
        self.assertEqual(kb.owner_id, "user1")
        self.blob_service.create_container.assert_called_once()
        self.search_service.create_index.assert_called_once()
    
    def test_admin_is_content_manager(self):
        """Test that admin users are content managers."""
        kb = self.manager.create_knowledge_base(
            name="Test KB",
            description="Test",
            owner_id="user1"
        )
        
        # Admin should be content manager
        self.assertTrue(
            self.manager.is_content_manager(kb.kb_id, "admin@test.com")
        )
        
        # Regular user should not be content manager
        self.assertFalse(
            self.manager.is_content_manager(kb.kb_id, "user2@test.com")
        )
    
    def test_owner_is_content_manager(self):
        """Test that KB owner is a content manager."""
        kb = self.manager.create_knowledge_base(
            name="Test KB",
            description="Test",
            owner_id="owner@test.com"
        )
        
        # Owner should be content manager
        self.assertTrue(
            self.manager.is_content_manager(kb.kb_id, "owner@test.com")
        )


class TestSearchResult(unittest.TestCase):
    """Test search result model."""
    
    def test_search_result_creation(self):
        """Test creating a search result."""
        result = SearchResult(
            document_id="doc1",
            filename="test.pdf",
            score=0.95,
            highlights=["highlight 1", "highlight 2"],
            metadata={"kb_id": "kb1"}
        )
        
        self.assertEqual(result.document_id, "doc1")
        self.assertEqual(result.score, 0.95)
        self.assertEqual(len(result.highlights), 2)
        self.assertEqual(result.metadata["kb_id"], "kb1")


if __name__ == '__main__':
    unittest.main()
