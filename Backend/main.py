# Backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# Import core chatbot logic
from core.chatbot_logic import process_chat_query

# Initialize FastAPI app
app = FastAPI(
    title="Owlynon API",
    description="API for Owlynn chatbot",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatQuery(BaseModel):
    query: str

# API endpoints
@app.post("/chat")
async def chat_endpoint(chat_query: ChatQuery):

    user_query = chat_query.query
    response_content = await process_chat_query(user_query)

    return {"response": response_content}

#Test endpoint
@app.get("/")
async def read_root():
    return {"message": "Owlynn API is running"}