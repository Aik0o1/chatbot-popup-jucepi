"""
Aplicação FastAPI para o chatbot JUCEPI.
Fornece endpoints REST para processamento de mensagens e integração com frontend.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

# Adicionar diretório pai ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag import JucepiRAG
from app.llm import ChatbotLLM

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="JUCEPI Chatbot API",
    description="API para o chatbot de atendimento da JUCEPI",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
rag_system = None
llm_model = None


def initialize_systems():
    """Inicializa os sistemas RAG e LLM."""
    global rag_system, llm_model
    
    try:
        # Determinar caminho da base de conhecimento
        backend_dir = Path(__file__).parent.parent
        kb_path = backend_dir / "data" / "jucepi_knowledge_base.json"
        
        logger.info(f"Carregando base de conhecimento de: {kb_path}")
        rag_system = JucepiRAG(str(kb_path))
        logger.info("Sistema RAG inicializado com sucesso")
        
        llm_model = ChatbotLLM()
        logger.info("Modelo LLM inicializado com sucesso")
    
    except Exception as e:
        logger.error(f"Erro ao inicializar sistemas: {e}")
        raise


# Modelos Pydantic
class MessageRequest(BaseModel):
    """Modelo para requisição de mensagem."""
    message: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = None


class MessageResponse(BaseModel):
    """Modelo para resposta de mensagem."""
    response: str
    sources: List[dict]
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Modelo para resposta de saúde."""
    status: str
    message: str


# Endpoints
@app.on_event("startup")
async def startup_event():
    """Inicializa os sistemas ao iniciar a aplicação."""
    initialize_systems()
    logger.info("Aplicação iniciada com sucesso")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica a saúde da aplicação."""
    if rag_system is None or llm_model is None:
        raise HTTPException(status_code=503, detail="Sistemas não inicializados")
    
    return HealthResponse(
        status="healthy",
        message="JUCEPI Chatbot API está funcionando corretamente"
    )


@app.post("/api/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """
    Processa uma mensagem do usuário e retorna uma resposta.
    
    Args:
        request: Requisição contendo a mensagem do usuário
    
    Returns:
        Resposta gerada pelo chatbot com fontes utilizadas
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")
    
    if rag_system is None or llm_model is None:
        raise HTTPException(status_code=503, detail="Sistemas não inicializados")
    
    try:
        user_message = request.message.strip()
        
        # Recuperar contexto relevante
        logger.info(f"Processando mensagem: {user_message[:50]}...")
        retrieved_docs = rag_system.retrieve(user_message, top_k=3)
        context = rag_system.get_context(user_message, top_k=3)
        
        # Gerar resposta
        response_text = llm_model.generate_response(user_message, context)
        
        # Preparar fontes
        sources = []
        for doc in retrieved_docs:
            source = {
                'type': doc.get('type'),
                'similarity_score': doc.get('similarity_score', 0)
            }
            
            if doc.get('type') == 'faq':
                source['question'] = doc.get('question')
                source['category'] = doc.get('category')
            elif doc.get('type') == 'procedure':
                source['title'] = doc.get('title')
            
            sources.append(source)
        
        logger.info(f"Resposta gerada com sucesso. Fontes: {len(sources)}")
        
        return MessageResponse(
            response=response_text,
            sources=sources,
            session_id=request.session_id
        )
    
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")


@app.get("/api/info")
async def get_organization_info():
    """Retorna informações da organização JUCEPI."""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="Sistema RAG não inicializado")
    
    return rag_system.get_organization_info()


@app.get("/api/faqs")
async def get_faqs(category: Optional[str] = None):
    """
    Retorna FAQs, opcionalmente filtradas por categoria.
    
    Args:
        category: Categoria para filtrar (opcional)
    
    Returns:
        Lista de FAQs
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="Sistema RAG não inicializado")
    
    faqs = rag_system.knowledge_base.get('faqs', [])
    
    if category:
        faqs = [faq for faq in faqs if faq.get('category', '').lower() == category.lower()]
    
    return {'faqs': faqs}


@app.get("/api/categories")
async def get_categories():
    """Retorna lista de categorias de FAQs disponíveis."""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="Sistema RAG não inicializado")
    
    faqs = rag_system.knowledge_base.get('faqs', [])
    categories = list(set(faq.get('category', 'Geral') for faq in faqs))
    
    return {'categories': sorted(categories)}


# Rota raiz
@app.get("/")
async def root():
    """Rota raiz da API."""
    return {
        "name": "JUCEPI Chatbot API",
        "version": "1.0.0",
        "description": "API para o chatbot de atendimento da JUCEPI",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "info": "/api/info",
            "faqs": "/api/faqs",
            "categories": "/api/categories"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
