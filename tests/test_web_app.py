"""
Unit tests for web application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.web_app import app as flask_app
from app.models import KnowledgeBase


class TestWebApp(unittest.TestCase):
    """Test web application routes."""
    
    def setUp(self):
        """Set up test client."""
        flask_app.config['TESTING'] = True
        flask_app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = flask_app.test_client()
        self.ctx = flask_app.app_context()
        self.ctx.push()
    
    def tearDown(self):
        """Clean up."""
        self.ctx.pop()
    
    def test_index(self):
        """Test index page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Knowledge Management System', response.data)
    
    def test_login_get(self):
        """Test login page GET."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_login_post(self):
        """Test login POST."""
        response = self.client.post('/login', data={
            'user_id': 'testuser',
            'email': 'test@example.com'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_no_login(self):
        """Test dashboard without login redirects."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_with_login(self):
        """Test dashboard with login."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
            sess['email'] = 'test@example.com'
        
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_logout(self):
        """Test logout."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_create_kb_no_login(self):
        """Test create KB without login."""
        response = self.client.get('/kb/create')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_kb_get(self):
        """Test create KB GET with login."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
            sess['email'] = 'test@example.com'
        
        response = self.client.get('/kb/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Knowledge Base', response.data)


class TestWebAppAPI(unittest.TestCase):
    """Test web application API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        flask_app.config['TESTING'] = True
        flask_app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = flask_app.test_client()
        self.ctx = flask_app.app_context()
        self.ctx.push()
    
    def tearDown(self):
        """Clean up."""
        self.ctx.pop()
    
    def test_ask_question_no_login(self):
        """Test ask question without login."""
        response = self.client.post('/kb/test123/ask', json={
            'question': 'What is this?'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_search_no_login(self):
        """Test search without login."""
        response = self.client.post('/kb/test123/search', json={
            'query': 'test'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_upload_no_login(self):
        """Test upload without login."""
        response = self.client.post('/kb/test123/upload')
        self.assertEqual(response.status_code, 302)  # Redirect


if __name__ == '__main__':
    unittest.main()
