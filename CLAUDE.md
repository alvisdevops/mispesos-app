# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal financial management system called "mispesos-app" designed to automate expense tracking through a Telegram bot with a web dashboard for visualization. The system is intended to run on an old PC at home with local data storage.

## System Architecture

The project consists of three main components:

1. **Telegram Bot** - Captures expenses and receipts through natural language and OCR
2. **Home Server** - Processes data, handles OCR, and serves APIs (using an old PC at home)
3. **Web Application** - Provides dashboard and detailed financial analysis

### Technology Stack (As Planned)

**Backend (Home Server):**
- Python 3.11+ with FastAPI
- SQLite database for local storage
- Tesseract OCR for receipt processing
- python-telegram-bot library
- Docker + Docker Compose for containerization

**Frontend (Web App):**
- React.js with Tailwind CSS
- REST API communication with Pi server
- Hosted on Namecheap shared hosting

## Database Schema

The system uses SQLite with the following key tables:

- `transactions` - Main financial transactions
- `receipts` - OCR processed receipts with metadata  
- `categories` - Expense categories with auto-classification
- `category_keywords` - Keywords for automatic categorization

## Key Features

### Telegram Bot Capabilities
- Natural language expense parsing (e.g., "50k almuerzo tarjeta")
- OCR processing of receipt photos
- Commands: `/resumen`, `/categorias`, `/balance`, `/corregir`, `/ayuda`
- Real-time transaction confirmation

### Web Dashboard
- Executive dashboard with KPIs and trend graphs
- Detailed transaction view (Excel-like interface)  
- Fiscal module for tax documentation
- Advanced filtering, search, and export capabilities

## Development Status

**Actualizado:** Septiembre 2025

El proyecto tiene especificaciones completas documentadas y arquitectura definida. Documentos disponibles:
- `financial_bot_specs.md` - Especificaciones detalladas del sistema
- `ARCHITECTURE.md` - Arquitectura completa del sistema  
- `DEVELOPMENT_PLAN.md` - Plan de desarrollo por fases con cronograma

**Estado actual:** Listo para iniciar implementación Fase 1.

## Development Approach

Implementación por fases incrementales (12 semanas total):

### Fase 1 - MVP Básico (Semanas 1-3)
- Bot de Telegram básico con parsing de lenguaje natural
- Base de datos SQLite con esquema completo
- API FastAPI core con endpoints básicos
- Categorización por palabras clave
- Deploy y testing básico

### Fase 2 - OCR y Web App (Semanas 4-7)  
- Integración Tesseract OCR para facturas
- Procesamiento de imágenes y extracción de datos
- Web app React con dashboard básico
- Gráficos y visualizaciones principales
- Deploy en Namecheap hosting

### Fase 3 - Funcionalidades Avanzadas (Semanas 8-10)
- Categorización inteligente con machine learning básico
- Módulo fiscal con gestión de facturas
- Reportes avanzados y exportación (Excel, PDF)
- Sistema de presupuestos y alertas
- Búsqueda avanzada y filtros

### Fase 4 - Deploy Producción (Semanas 11-12)
- Deploy optimizado en alvis-server
- Sistema completo de monitoreo y alertas
- Backup automático y procedimientos de recuperación
- Documentación de usuario y administración
- Optimización de performance

## Próximos Pasos Inmediatos

### Para iniciar desarrollo:

1. **Setup del Ambiente de Desarrollo:**
   - Conectar a alvis-server vía SSH
   - Configurar Python 3.11+ environment
   - Setup inicial de Docker y Docker Compose
   - Configurar estructura de proyecto

2. **Iniciar Fase 1:**
   - Crear bot de Telegram con BotFather
   - Implementar estructura básica de FastAPI
   - Setup de SQLite con schema inicial
   - Implementar parsing básico de mensajes

3. **Comandos de inicio:**
   ```bash
   # Conectar al servidor
   ssh -o ProxyCommand="cloudflared access ssh --hostname ssh.cristianalvis.com" devcris@ssh.cristianalvis.com
   
   # Crear directorio del proyecto
   mkdir -p ~/mispesos-app && cd ~/mispesos-app
   ```

### Referencias para implementación:
- Ver `ARCHITECTURE.md` para detalles técnicos completos
- Ver `DEVELOPMENT_PLAN.md` para cronograma detallado semana por semana
- Ver `financial_bot_specs.md` para funcionalidades específicas

## Security Considerations

- All financial data stays on local infrastructure (home PC + personal hosting)
- Telegram User ID authentication required
- Data encryption for sensitive information
- No third-party services for financial data processing

## Deployment Target

The system is designed to run on:
- Old PC at home as the main server (Ubuntu Server - hostname: alvis-server)
- Cloudflare tunnel for external access
- Local SQLite database (no cloud dependencies)
- Personal Namecheap hosting for web frontend

## Configuración del Servidor (Completada)

### Configuración de Acceso Remoto
- **Dominio:** cristianalvis.com (configurado con Cloudflare)
- **Acceso SSH:** ssh.cristianalvis.com vía Cloudflare Tunnel
- **Autenticación:** Autenticación basada en llaves SSH (sin contraseña)
- **Usuario:** devcris
- **IP Local:** 192.168.1.20

### Configuración de Acceso Externo (Producción)
- **Puerto API:** 8000 (FastAPI)
- **Puerto Web:** 80/443 (si se necesita servir contenido web local)
- **Telegram Webhooks:** Directo desde Telegram servers
- **Web App:** Hosted en Namecheap, consume API directamente

### Comandos de Conexión SSH (Solo Desarrollo)
```bash
# Desde red local
ssh devcris@192.168.1.20

# Desde cualquier lugar (remoto) - SOLO PARA DESARROLLO
ssh -o ProxyCommand="cloudflared access ssh --hostname ssh.cristianalvis.com" devcris@ssh.cristianalvis.com

# Alias para conveniencia (desarrollo)
alias ssh-server="ssh -o ProxyCommand=\"cloudflared access ssh --hostname ssh.cristianalvis.com\" devcris@ssh.cristianalvis.com"
```

**Nota:** Cloudflare Tunnel es SOLO para acceso SSH de desarrollo desde tu Mac. El sistema en producción NO depende de Cloudflare.

### Características de Seguridad
- Solo autenticación por llaves SSH (autenticación por contraseña deshabilitada)
- Port forwarding en router para API (puerto 8000) cuando el sistema esté en producción
- Login de root deshabilitado
- Restricción de usuario (solo devcris permitido)
- Firewall configurado para solo permitir puertos necesarios

### Restricciones de Acceso Físico
**IMPORTANTE:** El administrador del sistema **NO** tiene acceso físico regular al servidor ni al router donde está ubicado. Esto significa:

- **Cambios en router requieren coordinación** con administrador de red
- **Port forwarding** debe ser configurado por terceros cuando se lance a producción
- **Solo acceso remoto** vía Cloudflare Tunnel es viable para desarrollo
- Cualquier configuración debe ser **100% remota** y **sin intervención física**

**Implicaciones para Desarrollo:**
- Cloudflare Tunnel es la **única opción** para acceso SSH de desarrollo
- Desarrollo y testing inicial será en red local o via tunnel SSH
- Para producción, se requerirá abrir puerto 8000 en router (coordinación necesaria)
- Configuraciones deben ser reversibles remotamente

### Configuración de Red (Completada)
**Conectividad Redundante Automática:**
- **WiFi (wlp2s0):** Configurado con wpa_supplicant para inicio automático
  - IP: 192.168.1.20
  - Métrica: 600 (prioridad baja)
  - Servicio: `wpa_supplicant@wlp2s0.service` (enabled)
- **Ethernet (enp1s0):** Configurado con systemd-networkd para inicio automático  
  - IP: 192.168.1.23
  - Métrica: 100 (prioridad alta)
  - Servicio: `systemd-networkd.service` (enabled)

**Comportamiento al Reiniciar:**
- Ambas conexiones se configuran automáticamente
- Ethernet tiene prioridad sobre WiFi (métrica más baja)
- Si falla el cable, automáticamente usa WiFi como respaldo
- Sin intervención manual requerida

**Archivos de Configuración:**
- WiFi: `/etc/wpa_supplicant/wpa_supplicant-wlp2s0.conf`
- Ethernet: `/etc/systemd/network/20-wired.network`

## Preferencias de Desarrollo
- **Editor preferido:** vim (usar vim en lugar de nano para todas las ediciones)