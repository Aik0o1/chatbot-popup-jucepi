"""
Módulo de RAG (Retrieval-Augmented Generation) para o chatbot JUCEPI.
Implementa busca semântica em base de conhecimento usando embeddings.
"""

import json
import os
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class JucepiRAG:
    """
    Sistema RAG para recuperação de informações relevantes da base de conhecimento JUCEPI.
    Utiliza embeddings semânticos e busca FAISS para encontrar documentos relevantes.
    """
    
    def __init__(self, knowledge_base_path: str = "data/jucepi_knowledge_base.json"):
        """
        Inicializa o sistema RAG.
        
        Args:
            knowledge_base_path: Caminho para o arquivo JSON com a base de conhecimento
        """
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.documents = self._prepare_documents()
        self.embeddings = None
        self.index = None
        self._build_index()
    
    def _load_knowledge_base(self, path: str) -> Dict[str, Any]:
        """Carrega a base de conhecimento do arquivo JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _prepare_documents(self) -> List[Dict[str, Any]]:
        """
        Prepara documentos para indexação.
        Combina FAQs, procedimentos e informações de contato.
        """
        documents = []
        
        # Adicionar FAQs
        for faq in self.knowledge_base.get('faqs', []):
            documents.append({
                'type': 'faq',
                'id': faq['id'],
                'question': faq['question'],
                'answer': faq['answer'],
                'category': faq.get('category', ''),
                'keywords': faq.get('keywords', []),
                'text': f"{faq['question']} {faq['answer']}"
            })
        
        # Adicionar procedimentos
        for proc in self.knowledge_base.get('procedures', []):
            text = f"{proc['title']} "
            if 'steps' in proc:
                text += " ".join(proc['steps'])
            elif 'content' in proc:
                text += proc['content']
            
            documents.append({
                'type': 'procedure',
                'id': proc['id'],
                'title': proc['title'],
                'text': text
            })
        
        # Adicionar informações de contato
        contact_info = self.knowledge_base.get('organization', {}).get('contact', {})
        if contact_info:
            contact_text = f"Contato JUCEPI: {contact_info.get('phone', '')} {contact_info.get('email', '')} {contact_info.get('address', '')}"
            documents.append({
                'type': 'contact',
                'text': contact_text,
                'contact': contact_info
            })
        
        return documents
    
    def _build_index(self):
        """Constrói o índice FAISS com embeddings dos documentos."""
        texts = [doc['text'] for doc in self.documents]
        self.embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Criar índice FAISS
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype(np.float32))
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Recupera os documentos mais relevantes para uma consulta.
        
        Args:
            query: Texto da consulta do usuário
            top_k: Número de documentos a retornar
        
        Returns:
            Lista de documentos relevantes com scores de similaridade
        """
        # Gerar embedding da consulta
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Buscar no índice FAISS
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
        # Preparar resultados
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                # Converter distância L2 para score de similaridade (0-1)
                similarity_score = 1 / (1 + float(distance))
                doc['similarity_score'] = similarity_score
                results.append(doc)
        
        return results
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Obtém contexto formatado para usar no prompt do LLM.
        
        Args:
            query: Texto da consulta
            top_k: Número de documentos a usar
        
        Returns:
            String formatada com contexto relevante
        """
        results = self.retrieve(query, top_k)
        
        context_parts = []
        for result in results:
            if result['type'] == 'faq':
                context_parts.append(f"P: {result['question']}\nR: {result['answer']}")
            elif result['type'] == 'procedure':
                context_parts.append(f"Procedimento: {result['title']}\n{result['text']}")
            elif result['type'] == 'contact':
                context_parts.append(f"Informações de Contato:\n{result['text']}")
        
        return "\n\n".join(context_parts)
    
    def get_organization_info(self) -> Dict[str, Any]:
        """Retorna informações da organização JUCEPI."""
        return self.knowledge_base.get('organization', {})
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Busca documentos por palavras-chave.
        
        Args:
            keywords: Lista de palavras-chave
        
        Returns:
            Lista de documentos que contêm as palavras-chave
        """
        results = []
        for doc in self.documents:
            doc_keywords = doc.get('keywords', [])
            if any(kw.lower() in str(doc.get('text', '')).lower() for kw in keywords):
                results.append(doc)
        
        return results
