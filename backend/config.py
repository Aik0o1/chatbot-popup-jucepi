"""
Configuração da aplicação JUCEPI Chatbot.
"""

import os
from typing import List

# API Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# LLM Configuration
BUILT_IN_FORGE_API_URL = os.getenv("BUILT_IN_FORGE_API_URL", "https://api.manus.im")
BUILT_IN_FORGE_API_KEY = os.getenv("BUILT_IN_FORGE_API_KEY", "")

# CORS Configuration
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "https://localhost:3000",
    "https://localhost:5173",
]

# Adicionar origens do ambiente se fornecidas
env_origins = os.getenv("CORS_ORIGINS", "")
if env_origins:
    CORS_ORIGINS.extend(env_origins.split(","))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# RAG Configuration
RAG_TOP_K = int(os.getenv("RAG_TOP_K", 3))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# LLM Generation Configuration
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 512))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 30))
