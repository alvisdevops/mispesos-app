# Configuración del Servidor - MisPesos

## Introducción

Este documento guía la configuración completa del servidor alvis-server para el proyecto MisPesos. Incluye instalación de Docker, Portainer, Python, configuración de GitHub con SSH, y preparación del ambiente de desarrollo.

---

## Información del Servidor

- **Hostname:** alvis-server
- **IP Local:** 192.168.1.20 (WiFi) / 192.168.1.23 (Ethernet)
- **SO:** Ubuntu Server
- **Usuario:** devcris
- **Acceso:** SSH via Cloudflare Tunnel

### Comando de Conexión
```bash
ssh -o ProxyCommand="cloudflared access ssh --hostname ssh.cristianalvis.com" devcris@ssh.cristianalvis.com
```

---

## 1. INSTALACIÓN DE PYTHON 3.11+

### 1.1 Verificar Versión Actual
```bash
python3 --version
python3 -m pip --version
```

### 1.2 Instalar Python 3.11+ (si es necesario)
```bash
# Actualizar repositorios
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y software-properties-common

# Agregar repositorio deadsnakes (si Ubuntu < 22.04)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Crear alias (opcional)
echo 'alias python=python3.11' >> ~/.bashrc
echo 'alias pip=python3.11 -m pip' >> ~/.bashrc
source ~/.bashrc
```

### 1.3 Verificar Instalación
```bash
python3.11 --version
python3.11 -m pip --version
```

---

## 2. INSTALACIÓN DE DOCKER

### 2.1 Desinstalar Versiones Antiguas (si existen)
```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

### 2.2 Instalar Docker Engine
```bash
# Instalar dependencias
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualizar e instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 2.3 Configurar Usuario Docker
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Habilitar Docker al inicio
sudo systemctl enable docker
sudo systemctl start docker
```

### 2.4 Verificar Instalación
```bash
# Verificar Docker
docker --version
docker run hello-world

# Verificar Docker Compose
docker compose version
```

---

## 3. INSTALACIÓN DE PORTAINER

### 3.1 Crear Volume para Portainer
```bash
docker volume create portainer_data
```

### 3.2 Instalar Portainer Community Edition
```bash
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

### 3.3 Verificar Instalación
```bash
# Verificar que está corriendo
docker ps | grep portainer

# El contenedor debe mostrar status "Up"
```

### 3.4 Configurar Acceso Inicial

**Opción 1: Acceso Local (desde red local)**
- URL: `https://192.168.1.20:9443`

**Opción 2: Vía Cloudflare Tunnel (recomendado)**
- Agregar al config de Cloudflare:
```yaml
tunnel: fb6f53c9-f452-4da0-9001-33d96d2dd220
credentials-file: /home/devcris/.cloudflared/fb6f53c9-f452-4da0-9001-33d96d2dd220.json

ingress:
  - hostname: portainer.cristianalvis.com
    service: https://localhost:9443
  - hostname: ssh.cristianalvis.com
    service: ssh://localhost:22
  - service: http_status:404
```

**Setup Inicial:**
1. Ir a `https://portainer.cristianalvis.com` (o IP local)
2. Crear usuario admin (primera vez)
3. Seleccionar "Docker" como ambiente
4. ✅ Portainer listo!

---

## 4. CONFIGURACIÓN DE GITHUB SSH

### 4.1 Generar Clave SSH para GitHub
```bash
# Generar nueva clave SSH
ssh-keygen -t ed25519 -C "devcris@alvis-server" -f ~/.ssh/github_key

# Iniciar ssh-agent
eval "$(ssh-agent -s)"

# Agregar clave privada
ssh-add ~/.ssh/github_key
```

### 4.2 Configurar SSH Config
```bash
# Crear/editar config SSH
vim ~/.ssh/config

# Agregar configuración:
```
```
# GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_key
    IdentitiesOnly yes

# Cloudflare SSH (existente)
Host ssh.cristianalvis.com
    ProxyCommand cloudflared access ssh --hostname ssh.cristianalvis.com
```

### 4.3 Obtener Clave Pública
```bash
cat ~/.ssh/github_key.pub
```

### 4.4 Agregar Clave a GitHub
1. Copiar salida del comando anterior
2. Ir a GitHub → Settings → SSH and GPG keys
3. Click "New SSH key"
4. Title: "alvis-server"
5. Pegar clave pública
6. Save

### 4.5 Verificar Conexión
```bash
ssh -T git@github.com
# Debe responder: "Hi username! You've successfully authenticated..."
```

---

## 5. ESTRATEGIA DE BRANCHING Y WORKFLOW

### 5.1 Estrategia Recomendada: **GitHub Flow Simplificado**

```
main (production)
├── feature/telegram-bot-setup
├── feature/fastapi-core  
├── feature/ocr-integration
└── hotfix/critical-bug
```

**¿Por qué esta estrategia?**
- ✅ Simple para un desarrollador
- ✅ Deploy directo desde main
- ✅ Features en branches separados
- ✅ Fácil rollback

### 5.2 Configurar Repositorio
```bash
# Crear directorio del proyecto
mkdir -p ~/mispesos-app
cd ~/mispesos-app

# Clonar repositorio (reemplazar con tu repo)
git clone git@github.com:tu-usuario/mispesos-app.git .

# Verificar conexión
git remote -v
```

### 5.3 Workflow de Desarrollo
```bash
# 1. Crear feature branch
git checkout -b feature/nueva-funcionalidad

# 2. Desarrollar y commitear
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 3. Push al repo
git push origin feature/nueva-funcionalidad

# 4. Merge a main (via PR o direct)
git checkout main
git merge feature/nueva-funcionalidad
git push origin main

# 5. Deploy en servidor
git pull origin main
docker compose up -d --build
```

---

## 6. INFORMACIÓN SOBRE SQLITE

### 6.1 ¿Qué es SQLite?
SQLite es una base de datos SQL **embebida** que se almacena en un solo archivo:

**Características principales:**
- **Sin servidor:** No necesita proceso separado
- **Sin configuración:** Cero setup requerido
- **ACID compliant:** Transacciones seguras
- **Multiplataforma:** Funciona en cualquier OS
- **Pequeña:** ~1MB de biblioteca

### 6.2 ¿Por qué SQLite para MisPesos?

**✅ Perfecto para tu caso:**
- **Uso personal:** 1 usuario, pocas transacciones concurrentes
- **Volumen bajo:** < 100K registros/año
- **Backup simple:** Solo copiar archivo `.db`
- **Recursos limitados:** Consume muy poca RAM/CPU
- **Desarrollo rápido:** Sin complejidad de configuración

**Performance esperada:**
- **Inserts:** ~50,000 por segundo
- **Selects:** ~500,000 por segundo  
- **Tamaño DB:** ~100MB para 100K transacciones
- **RAM usage:** ~10-50MB

### 6.3 Limitaciones de SQLite
```
❌ No ideal para:
- Múltiples escritores concurrentes (>10)
- Bases de datos muy grandes (>100GB)
- Aplicaciones distribuidas
- Write-heavy workloads

✅ Perfecto para:
- Aplicaciones embebidas
- Desarrollo y testing
- Read-heavy applications
- Aplicaciones de escritorio/personales
```

### 6.4 Estructura de Archivos SQLite en el Proyecto
```
~/mispesos-app/
├── data/
│   ├── mispesos.db          # Base de datos principal
│   ├── mispesos.db-wal      # Write-Ahead Log
│   └── mispesos.db-shm      # Shared Memory
├── receipts/                # Imágenes OCR
│   ├── 2025/01/receipt_001.jpg
│   └── 2025/01/receipt_002.jpg
└── backups/                 # Respaldos automáticos
    ├── mispesos_2025-01-15.db
    └── mispesos_2025-01-14.db
```

### 6.5 Comandos Útiles SQLite
```bash
# Conectar a la base de datos
sqlite3 data/mispesos.db

# Comandos dentro de SQLite
.tables                      # Listar tablas
.schema transactions         # Ver estructura de tabla
.backup backup.db            # Crear backup
.quit                        # Salir

# Backup desde shell
cp data/mispesos.db backups/backup_$(date +%Y%m%d).db
```

---

## 7. ESTRUCTURA DE PROYECTO RECOMENDADA

### 7.1 Organización de Directorios
```
~/mispesos-app/
├── services/
│   ├── telegram-bot/        # Contenedor 1
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   ├── api/                 # Contenedor 2  
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   └── frontend/            # Contenedor 3
│       ├── Dockerfile
│       ├── package.json
│       └── src/
├── docker-compose.yml       # Configuración contenedores
├── docker-compose.dev.yml   # Para desarrollo
├── .env                     # Variables de entorno
├── data/                    # SQLite y datos persistentes
├── receipts/                # Imágenes OCR
├── backups/                 # Respaldos automáticos
└── docs/                    # Documentación
```

### 7.2 Preparar Estructura Inicial
```bash
cd ~/mispesos-app

# Crear directorios principales
mkdir -p services/{telegram-bot,api,frontend}/src
mkdir -p data receipts backups logs
mkdir -p docs

# Crear archivos base
touch docker-compose.yml
touch docker-compose.dev.yml
touch .env
touch README.md

# Establecer permisos
chmod 755 data receipts backups logs
```

---

## 8. VARIABLES DE ENTORNO

### 8.1 Crear Archivo .env
```bash
vim .env
```

### 8.2 Contenido del .env
```env
# Telegram Bot
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://api.cristianalvis.com/webhook

# Database
DATABASE_URL=sqlite:///./data/mispesos.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key_here

# OCR Configuration
TESSERACT_CMD=/usr/bin/tesseract
RECEIPTS_PATH=./receipts

# Backup Configuration
BACKUP_INTERVAL=24h
BACKUP_RETENTION=30

# Development
DEBUG=true
LOG_LEVEL=INFO
```

---

## 9. PRÓXIMOS PASOS

### 9.1 Checklist de Preparación del Servidor
- [ ] Conectar vía SSH al servidor
- [ ] Verificar/instalar Python 3.11+
- [ ] Instalar Docker y Docker Compose
- [ ] Instalar y configurar Portainer
- [ ] Configurar SSH keys para GitHub
- [ ] Clonar repositorio del proyecto
- [ ] Crear estructura de directorios
- [ ] Configurar variables de entorno
- [ ] Verificar que todo funciona

### 9.2 Comandos de Verificación Final
```bash
# Verificar todas las instalaciones
python3.11 --version
docker --version
docker compose version
docker ps | grep portainer
ssh -T git@github.com
git status
```

### 9.3 Para Iniciar Desarrollo
Una vez completado este setup:
1. **Fase 1:** Crear bot básico de Telegram
2. **FastAPI:** Setup inicial de la API
3. **Docker Compose:** Configurar contenedores
4. **Testing:** Verificar funcionamiento

---

## 10. SOLUCIÓN DE PROBLEMAS COMUNES

### 10.1 Docker Permission Denied
```bash
sudo usermod -aG docker $USER
newgrp docker
# O reiniciar sesión SSH
```

### 10.2 Portainer No Accesible
```bash
# Verificar que está corriendo
docker ps | grep portainer

# Verificar puertos
sudo netstat -tlnp | grep :9443

# Reiniciar si es necesario
docker restart portainer
```

### 10.3 GitHub SSH Problemas
```bash
# Verificar clave
ssh-add -l

# Re-agregar si es necesario
ssh-add ~/.ssh/github_key

# Test conexión
ssh -T git@github.com -v
```

### 10.4 Python/pip Issues
```bash
# Si pip no funciona
python3.11 -m ensurepip --default-pip
python3.11 -m pip install --upgrade pip
```

---

**Documento:** SERVER_SETUP.md  
**Versión:** 1.0  
**Fecha:** Septiembre 2025  
**Estado:** Listo para ejecución

---

**Instrucciones de Uso:**
1. Conectarse al servidor vía SSH
2. Seguir los pasos en orden secuencial
3. Verificar cada instalación antes de continuar
4. Guardar este documento para referencia futura