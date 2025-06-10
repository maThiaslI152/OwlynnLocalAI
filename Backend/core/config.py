from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from pathlib import Path

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "OwlynnLocalAI"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    LLM_BASE_URL: str = "http://localhost:1234/v1"
    LLM_MODEL: str = "Qwen3-14B"
    LLM_TEMPERATURE: float = 0.65
    LLM_MAX_TOKENS: int = 8096
    
    # Embeddings
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"
    BLIP_MODEL: str = "Salesforce/blip-image-captioning-base"
    
    # Database
    POSTGRES_USER: str = "owlynn"
    POSTGRES_PASSWORD: str = "owlynn_password"
    POSTGRES_DB: str = "owlynn_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Chroma
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    
    # File Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_EXTENSIONS: Dict[str, Any] = {
        "text": [".txt", ".md"],
        "documents": [".pdf", ".docx", ".rtf"],
        "spreadsheets": [".csv", ".xlsx"],
        "presentations": [".pptx"],
        "code": [".py", ".js", ".json", ".yml", ".yaml", ".html", ".xml", ".css"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
    }
    
    # OCR Settings
    TESSERACT_LANGUAGES: list = ["eng", "tha"]
    
    # Storage
    UPLOAD_DIR: Path = Path("uploads")
    CACHE_DIR: Path = Path("cache")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
