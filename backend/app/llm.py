"""
Módulo de integração com modelo de IA para geração de respostas.
Suporta Ollama local e outros modelos open-source.
"""

from typing import Optional, List, Dict
import os
import requests


class ChatbotLLM:
    """
    Interface para modelos de linguagem.
    Utiliza Ollama local para processamento de IA.
    """

    def __init__(
        self,
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Inicializa o cliente LLM com Ollama.

        Args:
            ollama_url: URL da API Ollama (padrão: http://localhost:11434)
            model: Nome do modelo (padrão: llama3:latest)
            temperature: Temperatura do modelo (padrão: 0.7)
            max_tokens: Máximo de tokens na resposta (padrão: 512)
        """
        self.ollama_url = ollama_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3:latest')
        self.temperature = temperature or float(os.getenv('LLM_TEMPERATURE', 0.7))
        self.max_tokens = max_tokens or int(os.getenv('LLM_MAX_TOKENS', 512))

        # System prompt para o chatbot Cris
        self.system_prompt = """Você é Cris, uma assistente virtual amigável e profissional da JUCEPI (Junta Comercial do Estado do Piauí).

Suas responsabilidades:
- Responder dúvidas sobre registro mercantil, abertura de empresas e serviços da JUCEPI
- Fornecer informações precisas baseadas na base de conhecimento oficial
- Ser atenciosa, prestativa e ágil nas respostas
- Manter um tom profissional mas amigável
- Sempre mencionar contatos oficiais quando apropriado
- Sugerir que o usuário visite o portal GOV.PI Empresas para serviços online

Diretrizes:
- Se não souber a resposta, seja honesto e sugira contatar a JUCEPI diretamente
- Sempre cite fontes confiáveis (portal oficial, telefone, email)
- Use linguagem clara e acessível
- Estruture respostas de forma organizada
- Seja conciso mas informativo

Responda sempre em português do Brasil."""

    def generate_response(self, user_message: str, context: str = "") -> str:
        """
        Gera uma resposta usando o modelo Ollama.

        Args:
            user_message: Mensagem do usuário
            context: Contexto recuperado pela busca RAG

        Returns:
            Resposta gerada pelo modelo
        """
        # Construir messages para o Ollama
        messages = self._build_messages(user_message, context)

        try:
            payload = {
                'model': self.model,
                'messages': messages,
                'stream': False,
                'options': {
                    'temperature': self.temperature,
                    'num_predict': 256
                }
            }

            response = requests.post(
                f'{self.ollama_url}/api/chat',
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get('message', {}).get('content', '')
                if content:
                    return content
                else:
                    print(f"Ollama retornou resposta vazia")
                    return self._fallback_response(user_message, context)
            else:
                print(f"Erro na API Ollama: {response.status_code} - {response.text}")
                return self._fallback_response(user_message, context)

        except requests.exceptions.Timeout:
            print(f"Timeout ao conectar ao Ollama em {self.ollama_url}")
            return self._fallback_response(user_message, context)
        except requests.exceptions.ConnectionError:
            print(f"Erro: Não foi possível conectar ao Ollama em {self.ollama_url}")
            return self._fallback_response(user_message, context)
        except Exception as e:
            print(f"Erro ao chamar Ollama: {type(e).__name__}: {e}")
            return self._fallback_response(user_message, context)

    def _build_messages(self, user_message: str, context: str) -> List[Dict[str, str]]:
        """Constrói a lista de mensagens para o Ollama."""
        messages = [
            {'role': 'system', 'content': self.system_prompt}
        ]

        if context:
            messages.append({
                'role': 'user',
                'content': f"""Baseando-se nas seguintes informações da base de conhecimento JUCEPI:

{context}

Responda à seguinte pergunta do usuário:
{user_message}"""
            })
        else:
            messages.append({'role': 'user', 'content': user_message})

        return messages

    def _fallback_response(self, user_message: str, context: str) -> str:
        """Resposta fallback quando o Ollama não está disponível."""
        if context:
            return f"""Baseado nas informações disponíveis sobre sua pergunta "{user_message}":

{context}

Para mais informações, entre em contato com a JUCEPI:
- Telefone: (86) 3230-8800 / 3230-8810
- Email: jucepi@jucepi.pi.gov.br
- Portal: https://www.piauidigital.pi.gov.br"""
        else:
            return """Desculpe, não consegui encontrar informações específicas sobre sua pergunta.

Por favor, entre em contato com a JUCEPI:
- Telefone: (86) 3230-8800 / 3230-8810
- Email: jucepi@jucepi.pi.gov.br
- Horário: 07h30 às 13h30
- Portal: https://www.piauidigital.pi.gov.br"""
