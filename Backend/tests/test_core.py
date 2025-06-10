import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import json
from main import app
from core.document_processor import DocumentProcessor
from core.memory import MemoryManager
from llm import llm, Message

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    """Test the chat endpoint with the updated LLM stack"""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello, how are you?",
            "session_id": "test_session"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "response" in data
    assert "metadata" in data

def test_document_processing():
    """Test document processing with updated libraries"""
    processor = DocumentProcessor()
    
    # Create a test text file
    test_file = Path("test.txt")
    test_content = "This is a test document."
    test_file.write_text(test_content)
    
    try:
        content, metadata = processor.process_file(str(test_file))
        assert content == test_content
        assert "filename" in metadata
        assert "file_type" in metadata
    finally:
        test_file.unlink()

def test_memory_management():
    """Test memory management with updated database libraries"""
    memory = MemoryManager()
    
    # Test conversation storage
    test_messages = [
        Message(role="user", content="Test message"),
        Message(role="assistant", content="Test response")
    ]
    
    session_id = "test_memory_session"
    memory.store_conversation(session_id, test_messages)
    
    # Test conversation retrieval
    retrieved = memory.get_conversation(session_id)
    assert retrieved is not None
    assert len(retrieved["messages"]) == 2

def test_document_search():
    """Test document search with updated ChromaDB"""
    memory = MemoryManager()
    
    # Test document storage
    test_doc = {
        "filename": "test.txt",
        "file_type": ".txt",
        "content": "This is a test document for search.",
        "metadata": {"test": True},
        "embeddings": [0.1] * 384
    }
    try:
        # Store document
        memory.store_document(
            filename=test_doc["filename"],
            file_type=test_doc["file_type"],
            content=test_doc["content"],
            metadata=test_doc["metadata"],
            embeddings=test_doc["embeddings"]
        )
        # Test search
        results = memory.search_documents("test document")
        print(f"Search results: {results}")  # Debug print
        # Verify results
        assert len(results) > 0, "No search results found"
        assert any("test.txt" in doc["filename"] for doc in results), "Test document not found in results"
    except Exception as e:
        pytest.fail(f"Document search test failed with error: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 