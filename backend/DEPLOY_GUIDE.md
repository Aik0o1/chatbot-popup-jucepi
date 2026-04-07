# Deploy do Backend JUCEPI Chatbot na AWS

## 📋 Pré-requisitos

- Servidor AWS com GPU (NVIDIA)
- Docker e Docker Compose instalados
- NVIDIA Container Toolkit instalado
- Domínio `dev-assistente.jucepi.pi.gov.br` configurado apontando para o IP do servidor

## 🚀 Passo a Passo

### 1. Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Transferir Arquivos para o Servidor

```bash
# No seu computador local
cd /home/victor/JUCEPI-DEV/jucepi-chatbot

# Transferir backend para o servidor
scp -r backend/ usuario@SEU_IP_AWS:/home/usuario/jucepi-chatbot-backend/
```

### 3. Configurar SSL com Let's Encrypt

```bash
# No servidor AWS
cd /home/usuario/jucepi-chatbot-backend

# Criar diretórios
mkdir -p ssl
mkdir -p /var/www/certbot

# Instalar Certbot
sudo apt install certbot -y

# Gerar certificado
sudo certbot certonly --standalone -d dev-assistente.jucepi.pi.gov.br

# Copiar certificados
sudo cp /etc/letsencrypt/live/dev-assistente.jucepi.pi.gov.br/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/dev-assistente.jucepi.pi.gov.br/privkey.pem ssl/

# Configurar permissões
sudo chmod 644 ssl/fullchain.pem
sudo chmod 644 ssl/privkey.pem
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas configurações
nano .env
```

### 5. Build e Deploy

```bash
# Build da imagem
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### 6. Verificar Deploy

```bash
# Testar health check
curl https://dev-assistente.jucepi.pi.gov.br/health

# Testar endpoint de chat
curl -X POST https://dev-assistente.jucepi.pi.gov.br/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá"}'
```

## 🔄 Renovar Certificado SSL

O certificado Let's Encrypt expira a cada 90 dias. Configure renovação automática:

```bash
# Criar script de renovação
sudo nano /etc/cron.d/certbot-renew

# Adicionar linha (renova a cada 60 dias)
0 0 1 */2 * certbot renew --quiet && cp /etc/letsencrypt/live/dev-assistente.jucepi.pi.gov.br/fullchain.pem /home/usuario/jucepi-chatbot-backend/ssl/ && cp /etc/letsencrypt/live/dev-assistente.jucepi.pi.gov.br/privkey.pem /home/usuario/jucepi-chatbot-backend/ssl/ && docker-compose -f /home/usuario/jucepi-chatbot-backend/docker-compose.yml restart nginx
```

## 📊 Comandos Úteis

```bash
# Ver logs do backend
docker logs -f jucepi-chatbot-backend

# Ver logs do nginx
docker logs -f jucepi-chatbot-nginx

# Reiniciar serviços
docker-compose restart

# Parar serviços
docker-compose down

# Atualizar aplicação
docker-compose down
docker-compose build
docker-compose up -d

# Verificar uso de GPU
nvidia-smi

# Verificar containers
docker ps
```

## 🔧 Troubleshooting

### Container não inicia
```bash
# Ver logs
docker logs jucepi-chatbot-backend

# Verificar GPU
nvidia-smi
```

### Erro de SSL
```bash
# Verificar certificados
ls -la ssl/

# Renovar certificado
sudo certbot renew
```

### CORS Error
```bash
# Verificar .env
cat .env | grep CORS_ORIGINS

# Reiniciar backend
docker-compose restart jucepi-chatbot-backend
```

## 📝 Atualizar o Frontend

Após o deploy, atualize o `.env` do frontend:

```env
VITE_CHATBOT_API_URL=https://dev-assistente.jucepi.pi.gov.br
```

## 🎯 Próximos Passos

1. Configurar monitoramento (Prometheus + Grafana)
2. Configurar backup automático da base de conhecimento
3. Implementar CI/CD com GitHub Actions
4. Configurar logs centralizados
