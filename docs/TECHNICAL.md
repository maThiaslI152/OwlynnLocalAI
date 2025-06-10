# Technical Documentation

## Architecture Overview

OwlynnLocalAI is built with a modern microservices architecture, consisting of several key components:

### 1. Backend Services

#### Core Components
- **Document Processor**: Handles file processing, OCR, and image captioning
- **Memory Manager**: Manages conversation history and document storage
- **LLM Interface**: Connects to the local Qwen3-14B model

#### Database Layer
- **Redis**: Short-term memory and caching
- **PostgreSQL**: Long-term storage for conversations and documents
- **ChromaDB**: Vector database for semantic search

### 2. Frontend

- **React**: Modern UI framework
- **Material-UI**: Component library
- **CopilotKit**: AI integration framework

## Component Details

### Document Processor

The `DocumentProcessor` class handles various file types:

```python
class DocumentProcessor:
    def process_file(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        # Process different file types
        # Return content and metadata
```

Supported file types:
- Text files (`.txt`, `.md`)
- Documents (`.pdf`, `.docx`, `.rtf`)
- Spreadsheets (`.csv`, `.xlsx`)
- Presentations (`.pptx`)
- Code files (`.py`, `.js`, `.json`, etc.)
- Images (`.jpg`, `.png`, etc.)

### Memory Management

The `MemoryManager` class handles data persistence:

```python
class MemoryManager:
    def store_conversation(self, session_id: str, messages: List[Message]):
        # Store in Redis (STM)
        # Store in PostgreSQL (LTM)

    def search_documents(self, query: str, limit: int = 5):
        # Search using ChromaDB
```

### LLM Integration

The system uses Qwen3-14B via LM Studio:

```python
llm = ChatOpenAI(
    openai_api_base="http://localhost:1234/v1",
    openai_api_key="none",
    temperature=0.65,
    max_tokens=8096,
)
```

## API Endpoints

### Chat Endpoint
```http
POST /api/v1/chat
Content-Type: application/json

{
    "message": "string",
    "session_id": "string?",
    "context": "object?"
}
```

### File Upload Endpoint
```http
POST /api/v1/upload
Content-Type: multipart/form-data

file: File
metadata: object?
```

### Search Endpoint
```http
GET /api/v1/search?query=string&limit=number
```

## Database Schema

### PostgreSQL Tables

#### Conversations
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    messages JSONB,
    metadata JSONB
);
```

#### Documents
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

### Environment Variables
```env
# Application
DEBUG=false
APP_NAME=OwlynnLocalAI
API_V1_STR=/api/v1

# LLM Settings
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=Qwen3-14B
LLM_TEMPERATURE=0.65
LLM_MAX_TOKENS=8096

# Database
POSTGRES_USER=owlynn
POSTGRES_PASSWORD=owlynn_password
POSTGRES_DB=owlynn
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_AUTH_TOKEN=chroma_token
```

## Security Considerations

1. **Local Processing**: All data processing happens locally
2. **No External APIs**: No data is sent to external services
3. **Secure Storage**: Sensitive data is encrypted at rest
4. **Access Control**: API endpoints are protected with authentication

## Performance Optimization

1. **Caching**: Redis for frequently accessed data
2. **Vector Search**: Efficient document retrieval with ChromaDB
3. **Batch Processing**: Document processing in chunks
4. **Async Operations**: Non-blocking API endpoints

## Error Handling

The system implements comprehensive error handling:

1. **Input Validation**: Pydantic models for request validation
2. **File Processing**: Graceful handling of unsupported formats
3. **Database Operations**: Transaction management and rollback
4. **API Responses**: Standardized error responses

## Monitoring and Logging

1. **Health Checks**: Regular service health monitoring
2. **Error Logging**: Detailed error tracking
3. **Performance Metrics**: Response time monitoring
4. **Resource Usage**: Memory and CPU tracking

## Deployment

### Docker Services
```yaml
services:
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: owlynn
      POSTGRES_PASSWORD: owlynn_password
      POSTGRES_DB: owlynn

  chroma:
    image: chromadb/chroma:latest
    environment:
      - ALLOW_RESET=true
      - ANONYMIZED_TELEMETRY=false
```

## Future Improvements

1. **Model Optimization**: Quantization for better performance
2. **Multi-Modal Support**: Enhanced image and video processing
3. **Plugin System**: Extensible architecture for custom features
4. **Offline Mode**: Complete offline functionality
5. **Mobile Support**: Progressive Web App capabilities 