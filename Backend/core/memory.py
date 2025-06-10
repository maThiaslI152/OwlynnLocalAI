from typing import List, Dict, Any, Optional
import redis
import psycopg2
from psycopg2.extras import DictCursor
import chromadb
from chromadb.config import Settings as ChromaSettings
from core.config import settings
import json
from datetime import datetime

class MemoryManager:
    def __init__(self):
        # Initialize Redis for short-term memory
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        
        # Initialize PostgreSQL for long-term memory
        self.pg_conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        self._init_databases()
    
    def _init_databases(self):
        """Initialize database tables and collections"""
        # Create PostgreSQL tables
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    messages JSONB,
                    metadata JSONB
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    content TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        self.pg_conn.commit()
        
        # Create ChromaDB collections
        self.chroma_client.get_or_create_collection("documents")
        self.chroma_client.get_or_create_collection("conversations")
    
    def store_conversation(self, session_id: str, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None):
        """Store conversation in both Redis (STM) and PostgreSQL (LTM)"""
        # Store in Redis with 24-hour expiration
        self.redis_client.setex(
            f"conv:{session_id}",
            86400,  # 24 hours
            json.dumps({"messages": messages, "metadata": metadata or {}})
        )
        
        # Store in PostgreSQL
        with self.pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO conversations (session_id, messages, metadata) VALUES (%s, %s, %s)",
                (session_id, json.dumps(messages), json.dumps(metadata or {}))
            )
        self.pg_conn.commit()
    
    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation from Redis (STM) or PostgreSQL (LTM)"""
        # Try Redis first
        conv_data = self.redis_client.get(f"conv:{session_id}")
        if conv_data:
            return json.loads(conv_data)
        
        # If not in Redis, try PostgreSQL
        with self.pg_conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "SELECT messages, metadata FROM conversations WHERE session_id = %s ORDER BY timestamp DESC LIMIT 1",
                (session_id,)
            )
            result = cur.fetchone()
            if result:
                return {
                    "messages": result["messages"],
                    "metadata": result["metadata"]
                }
        return None
    
    def store_document(self, filename: str, file_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Store document in PostgreSQL and its embeddings in ChromaDB"""
        # Store in PostgreSQL
        with self.pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (filename, file_type, content, metadata) VALUES (%s, %s, %s, %s) RETURNING id",
                (filename, file_type, content, json.dumps(metadata or {}))
            )
            doc_id = cur.fetchone()[0]
        self.pg_conn.commit()
        
        # Store in ChromaDB (assuming embeddings are provided in metadata)
        if metadata and "embeddings" in metadata:
            self.chroma_client.get_collection("documents").add(
                ids=[str(doc_id)],
                embeddings=[metadata["embeddings"]],
                metadatas=[metadata],
                documents=[content]
            )
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search documents using ChromaDB"""
        results = self.chroma_client.get_collection("documents").query(
            query_texts=[query],
            n_results=limit
        )
        
        # Fetch full document details from PostgreSQL
        documents = []
        for doc_id, metadata in zip(results["ids"][0], results["metadatas"][0]):
            with self.pg_conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
                doc = cur.fetchone()
                if doc:
                    documents.append(dict(doc))
        
        return documents
    
    def cleanup_old_conversations(self, days: int = 30):
        """Clean up conversations older than specified days"""
        with self.pg_conn.cursor() as cur:
            cur.execute(
                "DELETE FROM conversations WHERE timestamp < NOW() - INTERVAL '%s days'",
                (days,)
            )
        self.pg_conn.commit()
    
    def __del__(self):
        """Cleanup connections"""
        if hasattr(self, 'pg_conn'):
            self.pg_conn.close()
        if hasattr(self, 'redis_client'):
            self.redis_client.close()
