"""
RAG (Retrieval Augmented Generation) service using OpenAI.
Handles document chunking, embedding, retrieval, and answer generation.
"""

from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

from .config import OpenAIConfig

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk."""
    chunk_id: str
    document_id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None


@dataclass
class RAGResponse:
    """Response from RAG system."""
    answer: str
    sources: List[Dict[str, str]]
    confidence: float


class RAGService:
    """Service for RAG operations with OpenAI."""
    
    def __init__(self, config: OpenAIConfig):
        """Initialize the RAG service."""
        if not OpenAI:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        logger.info("RAG Service initialized with OpenAI")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.config.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.config.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def retrieve_relevant_chunks(
        self,
        query_embedding: List[float],
        chunks: List[Chunk],
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieve most relevant chunks based on embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            chunks: List of document chunks with embeddings
            top_k: Number of top chunks to return
            
        Returns:
            List of most relevant chunks
        """
        # Calculate similarity scores
        scored_chunks = []
        for chunk in chunks:
            if chunk.embedding:
                similarity = self.cosine_similarity(query_embedding, chunk.embedding)
                scored_chunks.append((similarity, chunk))
        
        # Sort by similarity (descending) and return top k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Chunk],
        system_prompt: Optional[str] = None
    ) -> RAGResponse:
        """
        Generate answer using GPT model with retrieved context.
        
        Args:
            question: User's question
            context_chunks: Retrieved relevant chunks
            system_prompt: Optional system prompt
            
        Returns:
            RAG response with answer and sources
        """
        # Build context from chunks
        context_parts = []
        sources = []
        
        for i, chunk in enumerate(context_chunks):
            context_parts.append(f"[Source {i+1}]: {chunk.text}")
            sources.append({
                'chunk_id': chunk.chunk_id,
                'document_id': chunk.document_id,
                'text_preview': chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                'metadata': chunk.metadata or {}
            })
        
        context = "\n\n".join(context_parts)
        
        # Default system prompt if not provided
        if not system_prompt:
            system_prompt = (
                "You are a helpful AI assistant that answers questions based on the provided context. "
                "Use the context to answer the question accurately. If the answer cannot be found in "
                "the context, say so. Cite the source numbers when referencing information."
            )
        
        # Create messages for GPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            # Simple confidence score based on response length and context usage
            confidence = min(1.0, len(answer) / 500)
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def process_query(
        self,
        question: str,
        document_chunks: List[Chunk],
        top_k: int = 5
    ) -> RAGResponse:
        """
        Process a query end-to-end: embed, retrieve, generate.
        
        Args:
            question: User's question
            document_chunks: All available document chunks
            top_k: Number of chunks to retrieve
            
        Returns:
            RAG response with answer and sources
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(question)
        
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(
            query_embedding,
            document_chunks,
            top_k
        )
        
        # Generate answer
        return self.generate_answer(question, relevant_chunks)
