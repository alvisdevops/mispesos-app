# MisPesos - Sistema de Gestión Financiera Personal

Sistema automatizado de gestión financiera personal con Telegram Bot y Web Dashboard, completamente containerizado con Docker.

## 🎯 Descripción

**MisPesos** es una solución personal para registrar gastos e ingresos de manera automática y natural a través de Telegram, con visualización completa en una aplicación web. Todo funciona en un servidor casero con control total de los datos.

## ⚡ Características Principales

- 📱 **Telegram Bot** - Captura instantánea de gastos por texto natural o OCR de facturas
- 🖥️ **Web Dashboard** - Análisis completo, gráficos y reportes financieros
- 🐳 **Totalmente Containerizado** - Deploy fácil con Docker Compose
- 🏠 **100% Local** - Todos los datos en tu propio servidor
- 📊 **OCR Inteligente** - Procesamiento automático de facturas
- 💰 **Categorización Automática** - Machine learning para clasificar gastos

## 🏗️ Arquitectura

### Componentes Docker:
- **telegram-bot** - Bot handler con webhook
- **fastapi** - API REST backend
- **webapp** - Frontend React containerizado
- **postgres** - Base de datos principal
- **redis** - Cache y queue manager
- **ocr-worker** - Procesamiento de imágenes
- **nginx** - Reverse proxy y SSL

### Stack Tecnológico:
- **Backend:** Python 3.11 + FastAPI + PostgreSQL + Redis
- **Frontend:** React 18 + TypeScript + Tailwind CSS
- **OCR:** Tesseract para procesamiento de imágenes
- **Infrastructure:** Docker + Docker Compose + Ubuntu Server

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker & Docker Compose
- Token de Bot de Telegram (de @BotFather)
- Servidor Ubuntu con acceso SSH

### Instalación
```bash
# Clonar repositorio
git clone https://github.com/tuusuario/mispesos-app.git
cd mispesos-app

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Levantar todos los servicios
docker-compose up -d

# Verificar que todos los contenedores estén corriendo
docker-compose ps
```

### Acceso
- **Web App:** http://localhost (o IP del servidor)
- **API Docs:** http://localhost:8000/docs
- **Bot Telegram:** @tu_bot_name

## 📋 Casos de Uso

### Registro por Texto Natural
```
Usuario: "50k almuerzo tarjeta"
Bot: ✅ Registrado: $50,000 - Alimentación - Tarjeta
```

### Procesamiento de Facturas
```
Usuario: [Envía foto de factura]
Bot: 📸 Procesando factura...
Bot: ✅ Extraído: $25,000 - Restaurante XYZ - IVA incluido
```

### Consultas Rápidas
```
Usuario: /resumen
Bot: 📊 Hoy: $75,000 | Semana: $350,000 | Mes: $1,200,000
     🍽️ Alimentación: 60% | 🚗 Transporte: 25% | 🏠 Servicios: 15%
```

## 🔧 Desarrollo

### Estructura del Proyecto
```
mispesos-app/
├── backend/          # FastAPI application
├── frontend/         # React web application
├── telegram-bot/     # Bot handler service
├── ocr-worker/       # Image processing service
├── docker-compose.yml
├── .env.example
└── README.md
```

### Comandos de Desarrollo
```bash
# Desarrollo con hot-reload
docker-compose -f docker-compose.dev.yml up

# Ver logs de un servicio específico
docker-compose logs -f fastapi

# Ejecutar tests
docker-compose exec fastapi pytest

# Acceder a contenedor para debugging
docker-compose exec fastapi bash
```

## 📁 Documentación

La documentación completa se encuentra en la carpeta `/documentacion` (ignorada por git):
- **ARCHITECTURE.md** - Arquitectura técnica detallada
- **DEVELOPMENT_PLAN.md** - Plan de desarrollo por fases
- **financial_bot_specs.md** - Especificaciones funcionales completas

## 🔒 Seguridad

- ✅ Datos 100% locales (sin servicios externos)
- ✅ Comunicación interna entre contenedores
- ✅ Backup automático cifrado
- ✅ SSL/TLS con certificados automáticos
- ✅ Autenticación por Telegram User ID

## 📊 Estado del Proyecto

**Versión:** 1.0.0-dev
**Estado:** En desarrollo - Fase 1
**Progreso:** Arquitectura completada, iniciando implementación

### Roadmap:
- [x] ✅ Diseño de arquitectura completa
- [ ] 🚧 Fase 1: MVP básico (Semanas 1-3)
- [ ] 📋 Fase 2: OCR y Web App (Semanas 4-7)
- [ ] 📋 Fase 3: Funcionalidades avanzadas (Semanas 8-10)
- [ ] 📋 Fase 4: Deploy producción (Semanas 11-12)

## 🤝 Contribución

Este es un proyecto personal, pero acepto sugerencias y mejoras.

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

---

**Desarrollado con ❤️ para el control financiero personal**