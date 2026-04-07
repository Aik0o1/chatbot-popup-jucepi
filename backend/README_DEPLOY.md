# 🚀 Deploy Rápido - Backend JUCEPI Chatbot

## 📦 Arquivos Criados

1. **Dockerfile** - Imagem otimizada para GPU NVIDIA
2. **docker-compose.yml** - Orquestração com Nginx + SSL
3. **nginx.conf** - Reverse proxy com HTTPS
4. **deploy.sh** - Script de deploy automatizado
5. **.env.example** - Template de variáveis de ambiente
6. **.dockerignore** - Otimização do build
7. **DEPLOY_GUIDE.md** - Guia completo de deploy

## ⚡ Deploy em 3 Passos

### 1. Transferir para o Servidor AWS

```bash
cd /home/victor/JUCEPI-DEV/jucepi-chatbot
scp -r backend/ usuario@SEU_IP_AWS:/home/usuario/jucepi-chatbot-backend/
```

### 2. Configurar no Servidor

```bash
# SSH no servidor
ssh usuario@SEU_IP_AWS

# Entrar na pasta
cd /home/usuario/jucepi-chatbot-backend

# Configurar SSL (primeira vez)
mkdir -p ssl
sudo certbot certonly --standalone -d dev-assistente.jucepi.pi.gov.br
sudo cp /etc/letsencrypt/live/dev-assistente.jucepi.pi.gov.br/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/dev-assistente.jucepi.pi.gov.br/privkey.pem ssl/

# Configurar .env
cp .env.example .env
nano .env  # Editar conforme necessário
```

### 3. Deploy

```bash
# Executar script de deploy
./deploy.sh
```

## ✅ Verificar

```bash
# Testar API
curl https://dev-assistente.jucepi.pi.gov.br/health

# Ver logs
docker-compose logs -f
```

## 🔄 Atualizar Frontend

Após o deploy, no arquivo `.env` do frontend:

```env
# Descomentar esta linha:
VITE_CHATBOT_API_URL=https://dev-assistente.jucepi.pi.gov.br
```

## 📚 Documentação Completa

Veja `DEPLOY_GUIDE.md` para instruções detalhadas.
