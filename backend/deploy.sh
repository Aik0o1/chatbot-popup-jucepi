#!/bin/bash

# Script de Deploy - JUCEPI Chatbot Backend
# Uso: ./deploy.sh

set -e

echo "🚀 Iniciando deploy do JUCEPI Chatbot Backend..."

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Instale o Docker primeiro."
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
fi

# Verificar se .env existe
if [ ! -f .env ]; then
    warn "Arquivo .env não encontrado. Criando a partir do .env.example..."
    cp .env.example .env
    warn "Edite o arquivo .env com suas configurações antes de continuar."
    exit 1
fi

# Parar containers existentes
log "Parando containers existentes..."
docker-compose down || true

# Build da imagem
log "Fazendo build da imagem Docker..."
docker-compose build

# Iniciar serviços
log "Iniciando serviços..."
docker-compose up -d

# Aguardar backend iniciar
log "Aguardando backend iniciar..."
sleep 10

# Verificar health check
log "Verificando health check..."
if curl -f http://localhost:8000/health &> /dev/null; then
    log "✅ Backend está rodando com sucesso!"
else
    error "❌ Backend não está respondendo. Verifique os logs com: docker-compose logs -f"
fi

# Mostrar status
log "Status dos containers:"
docker-compose ps

echo ""
log "🎉 Deploy concluído com sucesso!"
log "📝 Para ver os logs: docker-compose logs -f"
log "🔄 Para reiniciar: docker-compose restart"
log "⏹️  Para parar: docker-compose down"
