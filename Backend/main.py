from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uuid
import os
from pathlib import Path
from pydantic import BaseModel
import traceback

from core.config import settings
from core.memory import MemoryManager
from core.document_processor import DocumentProcessor
from llm import llm, State, Message, convert_to_langgraph_message, convert_to_pydantic_message

app = FastAPI(
    title=settings.APP_NAME,
    description="Local AI Personal Assistant with document processing capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
memory_manager = MemoryManager()
document_processor = DocumentProcessor()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.post("/api/v1/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    message = request.message
    session_id = request.session_id
    context = request.context
    try:
        if not session_id:
            session_id = str(uuid.uuid4())
        conversation = memory_manager.get_conversation(session_id)
        messages = [Message(**msg) if isinstance(msg, dict) else msg for msg in (conversation["messages"] if conversation else [])]
        user_message = Message(role="user", content=message, metadata=context or {})
        messages.append(user_message)
        langgraph_messages = [convert_to_langgraph_message(msg) for msg in messages]
        response = llm.invoke(langgraph_messages)
        ai_message = convert_to_pydantic_message(response)
        messages.append(ai_message)
        memory_manager.store_conversation(session_id, messages)
        return {
            "session_id": session_id,
            "response": ai_message.content,
            "metadata": ai_message.metadata
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Upload and process a file"""
    try:
        # Validate file size
        file_size = 0
        file_path = settings.UPLOAD_DIR / file.filename
        
        # Save file
        with open(file_path, "wb") as f:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File too large"
                    )
                f.write(chunk)
        
        # Process file
        content, file_metadata = document_processor.process_file(str(file_path))
        
        # Store in database
        memory_manager.store_document(
            filename=file.filename,
            file_type=os.path.splitext(file.filename)[1],
            content=content,
            metadata={**(metadata or {}), **file_metadata}
        )
        
        return {
            "filename": file.filename,
            "content": content,
            "metadata": file_metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/api/v1/search")
async def search_documents(
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Search through processed documents"""
    try:
        results = memory_manager.search_documents(query, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
