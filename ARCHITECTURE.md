# Arquitectura del Sistema MisPesos

## Visión General del Sistema

El sistema MisPesos está diseñado como una solución de gestión financiera personal distribuida en tres componentes principales que trabajan en conjunto para ofrecer una experiencia fluida de captura, procesamiento y visualización de transacciones financieras.

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA MISPESOS                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   TELEGRAM BOT  │◄──►│  HOME SERVER     │◄──►│   WEB APP       │
│  (Interface de  │    │ (Procesamiento)  │    │ (Visualización) │
│   Captura)      │    │                  │    │                 │
│                 │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ • Input Natural │    │ │   FastAPI    │ │    │ │   React     │ │
│ • OCR Photos    │    │ │   Server     │ │    │ │   Frontend  │ │
│ • Commands      │    │ └──────────────┘ │    │ └─────────────┘ │
│ • Confirmations │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
└─────────────────┘    │ │   Telegram   │ │    │ │ Tailwind    │ │
                       │ │   Bot Core   │ │    │ │    CSS      │ │
                       │ └──────────────┘ │    │ └─────────────┘ │
┌─────────────────┐    │ ┌──────────────┐ │    └─────────────────┘
│ CLOUDFLARE      │◄───┤ │  OCR Engine  │ │
│ TUNNEL          │    │ │ (Tesseract)  │ │    ┌─────────────────┐
│                 │    │ └──────────────┘ │    │ NAMECHEAP       │
│ • ssh access    │    │ ┌──────────────┐ │    │ HOSTING         │
│ • api access    │    │ │   SQLite     │ │    │                 │
│ • web routing   │    │ │   Database   │ │    │ • Static Files  │
└─────────────────┘    │ └──────────────┘ │    │ • Web Hosting   │
                       └──────────────────┘    │ • CDN           │
                                              └─────────────────┘
```

## Componentes Detallados

### 1. Telegram Bot (Interface de Captura)
**Propósito:** Punto de entrada principal para captura de transacciones

**Responsabilidades:**
- Procesar mensajes de texto en lenguaje natural
- Recibir y pre-procesar imágenes de facturas
- Ejecutar comandos de consulta (/resumen, /categorias, etc.)
- Proporcionar confirmaciones y feedback inmediato
- Manejar correcciones de transacciones

**Tecnologías:**
- `python-telegram-bot` library
- Webhook para recepción de mensajes
- Integración con FastAPI backend

**Flujo de Datos:**
```
Usuario → Mensaje/Foto → Bot → Parser/OCR → Validación → Confirmación → Usuario
```

### 2. Home Server (Núcleo de Procesamiento)
**Propósito:** Cerebro del sistema, maneja toda la lógica de negocio y almacenamiento

#### 2.1 FastAPI Application Server
**Responsabilidades:**
- API REST para comunicación con Web App
- Orchestración de procesos de negocio
- Manejo de autenticación y autorización
- Gestión de webhooks de Telegram
- Exposición de endpoints para consultas y modificaciones

#### 2.2 Telegram Bot Core
**Responsabilidades:**
- Parsing de mensajes en lenguaje natural
- Extracción de entidades (monto, categoría, fecha, etc.)
- Lógica de comandos del bot
- Gestión de conversaciones y estado
- Integración con sistema de categorización automática

#### 2.3 OCR Engine (Tesseract)
**Responsabilidades:**
- Procesamiento de imágenes de facturas
- Extracción de texto mediante OCR
- Post-procesamiento para identificación de campos específicos
- Extracción de metadatos fiscales (NIT, número de factura, etc.)

#### 2.4 SQLite Database
**Responsabilidades:**
- Almacenamiento de transacciones
- Gestión de categorías y reglas de clasificación
- Almacenamiento de metadatos de facturas
- Respaldo de imágenes procesadas
- Auditoría de cambios

**Esquema Principal:**
```sql
transactions
├── id (PK)
├── date, timestamp
├── amount, description
├── category, payment_method
├── location, telegram_message_id
└── created_at, updated_at

receipts
├── id (PK)
├── transaction_id (FK)
├── file_path, ocr_text
├── company_name, company_nit
├── receipt_number, tax_amount
└── processed_at

categories & category_keywords
├── Auto-classification rules
└── User-defined categories
```

### 3. Web Application (Interface de Visualización)
**Propósito:** Dashboard completo para análisis y gestión financiera

#### 3.1 React Frontend
**Responsabilidades:**
- Dashboard ejecutivo con KPIs
- Vista detallada tipo Excel de transacciones
- Módulo fiscal para gestión de facturas
- Formularios de edición y configuración
- Exportación de datos (Excel, PDF, CSV)

#### 3.2 Características Principales
- **Dashboard:** Gráficos de tendencias, resúmenes por categoría, alertas
- **Vista Detallada:** Tabla completa con filtros, búsqueda, ordenamiento
- **Módulo Fiscal:** Organización de facturas, reportes para impuestos
- **Configuración:** Gestión de categorías, reglas, presupuestos

## Infraestructura y Conectividad

### Home Server Specifications
**Hardware:** PC reutilizado en casa
- **OS:** Ubuntu Server
- **Usuario:** devcris
- **IP Local:** 192.168.1.20
- **Hostname:** alvis-server

### Conectividad Externa
```
Internet ◄─► Cloudflare Tunnel ◄─► Home Server (192.168.1.20)
                    │
                    ▼
              Web App (Namecheap)
```

**Cloudflare Tunnel:**
- ID: fb6f53c9-f452-4da0-9001-33d96d2dd220
- Dominio: cristianalvis.com
- SSH Access: ssh.cristianalvis.com
- API Endpoints: api.cristianalvis.com

### Red Local Redundante
**Ethernet (enp1s0):** IP 192.168.1.23, Métrica 100 (prioridad alta)
**WiFi (wlp2s0):** IP 192.168.1.20, Métrica 600 (fallback)

## Flujos de Datos Principales

### 1. Captura de Transacción por Texto
```
Usuario: "50k almuerzo tarjeta"
    ↓
Telegram Bot: Parse mensaje
    ↓
FastAPI: Procesar y validar
    ↓
SQLite: Almacenar transacción
    ↓
Bot: Confirmar a usuario
    ↓
Web App: Auto-actualizar dashboard
```

### 2. Procesamiento de Factura
```
Usuario: [Foto de factura]
    ↓
Telegram Bot: Recibir imagen
    ↓
OCR Engine: Extraer texto y datos
    ↓
FastAPI: Procesar y estructurar
    ↓
SQLite: Guardar transacción + metadata + imagen
    ↓
Bot: Confirmar con datos extraídos
    ↓
Web App: Actualizar con nueva transacción y factura
```

### 3. Consulta Web Dashboard
```
Usuario: Accede a Web App
    ↓
React: Cargar dashboard
    ↓
API REST: Solicitar datos a FastAPI
    ↓
FastAPI: Consultar SQLite
    ↓
SQLite: Devolver datos agregados
    ↓
Web App: Renderizar gráficos y tablas
```

## Consideraciones de Seguridad

### Autenticación y Autorización
- **Telegram:** Verificación por User ID único
- **Web App:** Login seguro con sesión
- **API:** Token-based authentication
- **SSH:** Autenticación por llaves, sin contraseña

### Protección de Datos
- **Cifrado:** Datos sensibles cifrados en base de datos
- **Localización:** Todos los datos permanecen en infraestructura controlada
- **Respaldo:** Backup automático cifrado
- **Auditoría:** Log de todas las transacciones y accesos

### Conectividad Segura
- **Sin puertos abiertos:** Solo Cloudflare Tunnel
- **VPN no requerida:** Túnel seguro incorporado
- **Rate limiting:** Protección contra ataques de API
- **Monitoreo:** Alertas automáticas por accesos sospechosos

## Escalabilidad y Rendimiento

### Optimizaciones Actuales
- **SQLite:** Adecuado para uso personal (< 100K transacciones/año)
- **Caché:** Respuestas frecuentes cacheadas en memoria
- **Imágenes:** Compresión automática de facturas
- **API:** Paginación en consultas grandes

### Planes de Escalabilidad Futura
- **Base de Datos:** Migración a PostgreSQL si es necesario
- **Caché:** Redis para sesiones web si se requiere
- **CDN:** Optimización de imágenes vía Cloudflare
- **Monitoreo:** Métricas de performance y uso

## Monitoreo y Mantenimiento

### Health Checks
- **Bot Status:** Verificación cada 5 minutos
- **API Uptime:** Monitoring continuo
- **Database:** Checks de integridad automáticos
- **Disk Space:** Alertas antes de límites

### Backup Strategy
- **Local:** Backup diario automático
- **Remoto:** Sincronización semanal cifrada
- **Versionado:** 30 días de respaldos históricos
- **Verificación:** Tests automáticos de recuperación

### Logs y Auditoría
- **Application Logs:** Rotación automática
- **Access Logs:** Monitoreo de patrones
- **Error Tracking:** Notificaciones inmediatas
- **Performance Metrics:** Recolección continua

## Próximos Pasos de Implementación

Esta arquitectura servirá como base para el desarrollo por fases:

1. **Fase 1:** Bot básico + SQLite + API core
2. **Fase 2:** OCR + Web App básica
3. **Fase 3:** Funcionalidades avanzadas + categorización inteligente
4. **Fase 4:** Optimización + deploy en producción

---

**Documento:** ARCHITECTURE.md  
**Versión:** 1.0  
**Fecha:** Septiembre 2025  
**Estado:** Diseño completo aprobado para desarrollo