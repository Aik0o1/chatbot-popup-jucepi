# Dockerfile para GPU NVIDIA
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# Definir variáveis para evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python 3.11 e dependências do sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    python3.11-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Criar link simbólico para python3
RUN ln -sf /usr/bin/python3.11 /usr/bin/python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3

# Atualizar pip
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando para iniciar a aplicação
CMD ["python", "-m", "app.main"]
