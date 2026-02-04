"""
Comprehensive unit tests for RAG service.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from app.rag_service import RAGService, Chunk, RAGResponse
from app.config import OpenAIConfig


class TestRAGService(unittest.TestCase):
    """Test RAG service functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = OpenAIConfig(
            api_key="test-key",
            model="gpt-4",
            embedding_model="text-embedding-ada-002"
        )
    
    @patch('app.rag_service.OpenAI')
    def test_init(self, mock_openai):
        """Test RAG service initialization."""
        service = RAGService(self.config)
        self.assertIsNotNone(service)
        self.assertEqual(service.config.model, "gpt-4")
        mock_openai.assert_called_once()
    
    @patch('app.rag_service.OpenAI', None)
    def test_init_no_openai(self):
        """Test RAG service initialization without OpenAI installed."""
        with self.assertRaises(ImportError) as context:
            RAGService(self.config)
        self.assertIn("OpenAI package not installed", str(context.exception))
    
    def test_chunk_text_basic(self):
        """Test text chunking."""
        service = RAGService.__new__(RAGService)
        service.config = self.config
        
        text = "a" * 2500
        chunks = service.chunk_text(text, chunk_size=1000, overlap=200)
        
        self.assertGreater(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 1000)
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        service = RAGService.__new__(RAGService)
        service.config = self.config
        
        chunks = service.chunk_text("", chunk_size=1000, overlap=200)
        self.assertEqual(len(chunks), 0)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        service = RAGService.__new__(RAGService)
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]
        
        # Identical vectors
        similarity = service.cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0)
        
        # Orthogonal vectors
        similarity = service.cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity, 0.0)
    
    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        service = RAGService.__new__(RAGService)
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 0.0]
        
        similarity = service.cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)
    
    @patch('app.rag_service.OpenAI')
    def test_generate_embedding(self, mock_openai):
        """Test embedding generation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        embedding = service.generate_embedding("test text")
        
        self.assertEqual(len(embedding), 3)
        self.assertEqual(embedding[0], 0.1)
    
    @patch('app.rag_service.OpenAI')
    def test_generate_embedding_error(self, mock_openai):
        """Test embedding generation with error."""
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        
        with self.assertRaises(Exception) as context:
            service.generate_embedding("test text")
        self.assertIn("API Error", str(context.exception))
    
    @patch('app.rag_service.OpenAI')
    def test_generate_embeddings_batch(self, mock_openai):
        """Test batch embedding generation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2]),
            MagicMock(embedding=[0.3, 0.4])
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        embeddings = service.generate_embeddings_batch(["text1", "text2"])
        
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings[0], [0.1, 0.2])
    
    @patch('app.rag_service.OpenAI')
    def test_generate_embeddings_batch_error(self, mock_openai):
        """Test batch embedding generation with error."""
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("Batch API Error")
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        
        with self.assertRaises(Exception) as context:
            service.generate_embeddings_batch(["text1", "text2"])
        self.assertIn("Batch API Error", str(context.exception))
    
    def test_retrieve_relevant_chunks(self):
        """Test chunk retrieval."""
        service = RAGService.__new__(RAGService)
        
        query_embedding = [1.0, 0.0, 0.0]
        chunks = [
            Chunk("1", "doc1", "text1", embedding=[1.0, 0.0, 0.0]),
            Chunk("2", "doc2", "text2", embedding=[0.0, 1.0, 0.0]),
            Chunk("3", "doc3", "text3", embedding=[0.9, 0.1, 0.0])
        ]
        
        relevant = service.retrieve_relevant_chunks(query_embedding, chunks, top_k=2)
        
        self.assertEqual(len(relevant), 2)
        self.assertEqual(relevant[0].chunk_id, "1")  # Most similar
    
    @patch('app.rag_service.OpenAI')
    def test_generate_answer(self, mock_openai):
        """Test answer generation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test answer"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        
        chunks = [
            Chunk("1", "doc1", "Context text", metadata={"source": "doc1"})
        ]
        
        response = service.generate_answer("Question?", chunks)
        
        self.assertIsInstance(response, RAGResponse)
        self.assertEqual(response.answer, "Test answer")
        self.assertEqual(len(response.sources), 1)
    
    @patch('app.rag_service.OpenAI')
    def test_generate_answer_error(self, mock_openai):
        """Test answer generation with error."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("GPT Error")
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        
        chunks = [
            Chunk("1", "doc1", "Context text", metadata={"source": "doc1"})
        ]
        
        with self.assertRaises(Exception) as context:
            service.generate_answer("Question?", chunks)
        self.assertIn("GPT Error", str(context.exception))
    
    @patch('app.rag_service.OpenAI')
    def test_process_query(self, mock_openai):
        """Test end-to-end query processing."""
        mock_client = MagicMock()
        
        # Mock embedding
        mock_embed_response = MagicMock()
        mock_embed_response.data = [MagicMock(embedding=[1.0, 0.0, 0.0])]
        
        # Mock chat completion
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock(message=MagicMock(content="Answer"))]
        
        mock_client.embeddings.create.return_value = mock_embed_response
        mock_client.chat.completions.create.return_value = mock_chat_response
        mock_openai.return_value = mock_client
        
        service = RAGService(self.config)
        
        chunks = [
            Chunk("1", "doc1", "text1", embedding=[1.0, 0.0, 0.0]),
            Chunk("2", "doc2", "text2", embedding=[0.0, 1.0, 0.0])
        ]
        
        response = service.process_query("Question?", chunks, top_k=1)
        
        self.assertIsInstance(response, RAGResponse)
        self.assertEqual(response.answer, "Answer")


class TestChunk(unittest.TestCase):
    """Test Chunk data class."""
    
    def test_chunk_creation(self):
        """Test creating a chunk."""
        chunk = Chunk(
            chunk_id="1",
            document_id="doc1",
            text="Sample text",
            embedding=[0.1, 0.2, 0.3],
            metadata={"key": "value"}
        )
        
        self.assertEqual(chunk.chunk_id, "1")
        self.assertEqual(chunk.document_id, "doc1")
        self.assertEqual(len(chunk.embedding), 3)
    
    def test_chunk_default_values(self):
        """Test chunk with default values."""
        chunk = Chunk(
            chunk_id="1",
            document_id="doc1",
            text="Sample text"
        )
        
        self.assertIsNone(chunk.embedding)
        self.assertIsNone(chunk.metadata)


class TestRAGResponse(unittest.TestCase):
    """Test RAGResponse data class."""
    
    def test_rag_response_creation(self):
        """Test creating a RAG response."""
        response = RAGResponse(
            answer="Test answer",
            sources=[{"doc": "source1"}],
            confidence=0.95
        )
        
        self.assertEqual(response.answer, "Test answer")
        self.assertEqual(len(response.sources), 1)
        self.assertEqual(response.confidence, 0.95)


if __name__ == '__main__':
    unittest.main()
