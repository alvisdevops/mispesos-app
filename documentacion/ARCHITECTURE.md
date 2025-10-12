# Arquitectura del Sistema MisPesos

## Visión General del Sistema

El sistema MisPesos está diseñado como una solución de gestión financiera personal distribuida en tres componentes principales que trabajan en conjunto para ofrecer una experiencia fluida de captura, procesamiento y visualización de transacciones financieras.

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA MISPESOS                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────────────────────────┐
│   TELEGRAM BOT  │◄──►│         HOME SERVER                 │
│  (Interface de  │    │       (alvis-server)                │
│   Captura)      │    │                                     │
│                 │    │ ┌─────────────┐ ┌─────────────────┐ │
│ • Input Natural │    │ │   FastAPI   │ │   WEB APP       │ │
│ • OCR Photos    │    │ │   Server    │ │ (Dashboard)     │ │
│ • Commands      │    │ │  Port 8000  │ │                 │ │
│ • Confirmations │    │ │  REST API   │ │ • React Frontend│ │
└─────────────────┘    │ └─────────────┘ │ • Tailwind CSS  │ │
                       │ ┌─────────────┐ │ • Analytics     │ │
                       │ │  Telegram   │ │ • Export Tools  │ │
                       │ │  Bot Core   │ │                 │ │
                       │ │ + Redis     │ └─────────────────┘ │
                       │ │ Queue Mgr   │ ┌─────────────────┐ │
                       │ └─────────────┘ │   OCR Engine    │ │
                       │ ┌─────────────┐ │  (Tesseract)    │ │
                       │ │ PostgreSQL  │ │ Image Process   │ │
                       │ │  Database   │ └─────────────────┘ │
                       │ │Local Storage│                     │
                       │ └─────────────┘                     │
                       └─────────────────────────────────────┘
```

## Componentes Detallados

### 1. Telegram Bot (Interface de Captura)
**Propósito:** Punto de entrada principal para captura de transacciones

**Responsabilidades:**
- Procesar mensajes de texto en lenguaje natural con IA local
- Extraer información financiera desde texto libre (sin comandos rígidos)
- Recibir y pre-procesar imágenes de facturas
- Ejecutar comandos de consulta (/resumen, /categorias, etc.)
- Proporcionar confirmaciones y feedback inmediato
- Manejar correcciones de transacciones
- Integración con modelos AI locales para parsing inteligente

**Tecnologías:**
- `python-telegram-bot` library
- Webhook para recepción de mensajes
- Integración con FastAPI backend
- **Ollama** para modelos AI locales (LLaMA 3.2:3b → Phi-3:mini)
- **AI-powered parsing** en lugar de regex tradicional

**Flujo de Datos:**
```
Usuario → Mensaje/Foto → Bot → AI Parser/OCR → Validación → Confirmación → Usuario
                                    ↓
                            Ollama (LLaMA/Phi-3)
                               Local AI
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

#### 2.2 Telegram Bot Core + AI Engine + Redis Queue Manager
**Responsabilidades:**
- **Parsing inteligente** con IA local (Ollama + LLaMA/Phi-3)
- Extracción de entidades financieras desde texto libre
- Fallback a regex si IA falla (sistema robusto)
- Lógica de comandos del bot
- Gestión de conversaciones y estado
- Integración con sistema de categorización automática
- Gestión de colas asíncronas con Redis para OCR y procesamiento

**Estrategia de Modelos AI:**
- **Desarrollo:** LLaMA 3.2:3b (funciona con 8GB RAM actuales)
- **Producción:** Phi-3:mini (requiere upgrade a 16GB RAM)
- **Cambio trivial:** Solo modificar parámetro "model" en código
- **100% Local:** Sin dependencias externas, procesamiento privado

#### 2.3 OCR Engine (Tesseract)
**Responsabilidades:**
- Procesamiento de imágenes de facturas
- Extracción de texto mediante OCR
- Post-procesamiento para identificación de campos específicos
- Extracción de metadatos fiscales (NIT, número de factura, etc.)

#### 2.4 Ollama AI Engine
**Propósito:** Procesamiento local de lenguaje natural para parsing inteligente

**Responsabilidades:**
- Análisis semántico de mensajes financieros en texto libre
- Extracción estructurada de datos (monto, categoría, método de pago, etc.)
- Categorización automática inteligente
- Procesamiento 100% local sin APIs externas

**Modelos Soportados:**
```yaml
Estrategia Progresiva:
├── Desarrollo (8GB RAM): LLaMA 3.2:3b
│   ├── Tamaño: ~2GB
│   ├── Velocidad: 1-2 segundos
│   └── Precisión: Alta para español
└── Producción (16GB RAM): Phi-3:mini
    ├── Tamaño: ~2.3GB
    ├── Velocidad: <1 segundo
    └── Precisión: Máxima capacidad conversacional
```

**Ejemplos de Parsing:**
```
Input: "50k almuerzo tarjeta"
Output: {
  "amount": 50000,
  "description": "almuerzo",
  "category": "alimentacion",
  "payment_method": "tarjeta",
  "confidence": 0.95
}

Input: "pagué 25000 de uber efectivo ayer"
Output: {
  "amount": 25000,
  "description": "uber",
  "category": "transporte",
  "payment_method": "efectivo",
  "date_offset": -1,
  "confidence": 0.92
}
```

#### 2.5 PostgreSQL Database
**Responsabilidades:**
- Almacenamiento robusto de transacciones
- Gestión de categorías y reglas de clasificación
- Almacenamiento de metadatos de facturas
- Respaldo de imágenes procesadas
- Auditoría de cambios
- Soporte para concurrencia y backups avanzados

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
**Propósito:** Dashboard completo integrado en el Home Server
**Ubicación:** Contenedor dentro del mismo servidor alvis-server

#### 3.1 React Frontend Containerizado
**Responsabilidades:**
- Dashboard ejecutivo con KPIs
- Vista detallada tipo Excel de transacciones
- Módulo fiscal para gestión de facturas
- Formularios de edición y configuración
- Exportación de datos (Excel, PDF, CSV)
- Comunicación directa con FastAPI (misma red interna)

#### 3.2 Características Principales
- **Dashboard:** Gráficos de tendencias, resúmenes por categoría, alertas
- **Vista Detallada:** Tabla completa con filtros, búsqueda, ordenamiento
- **Módulo Fiscal:** Organización de facturas, reportes para impuestos
- **Configuración:** Gestión de categorías, reglas, presupuestos
- **Ventajas de Containerización:** Comunicación ultra-rápida con API, deploy unificado

## Infraestructura y Conectividad

### Home Server Specifications
**Hardware:** PC reutilizado en casa
- **OS:** Ubuntu Server
- **Usuario:** devcris
- **IP Local:** 192.168.1.20
- **Hostname:** alvis-server

### Conectividad Externa
```
Internet ◄─► Router Port Forward ◄─► Home Server (192.168.1.20)
                    │                         │
                    ▼                         ▼
         Telegram Webhooks ────────► Web App (Puerto 80/443)
                                     FastAPI (Puerto 8000)
```

**Configuración de Producción:**
- **Web App:** Puerto 80/443 (requiere port forwarding en router)
- **API FastAPI:** Puerto 8000 (acceso directo para desarrollo/APIs)
- **Telegram Webhooks:** Directo desde servers de Telegram
- **Arquitectura Unificada:** Todo en el mismo servidor, comunicación interna ultra-rápida

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
Usuario: Accede a Web App (localhost o IP servidor)
    ↓
React: Cargar dashboard (misma red que API)
    ↓
API REST: Solicitar datos a FastAPI (comunicación interna)
    ↓
FastAPI: Consultar PostgreSQL
    ↓
PostgreSQL: Devolver datos agregados
    ↓
Web App: Renderizar gráficos y tablas (ultra-rápido)
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
- **Puerto API expuesto:** Solo puerto 8000 para FastAPI (HTTPS recomendado)
- **Firewall:** Solo permitir tráfico en puerto 8000
- **Rate limiting:** Protección contra ataques de API
- **Monitoreo:** Alertas automáticas por accesos sospechosos
- **SSL/TLS:** Certificados para API endpoints (Let's Encrypt)

## Escalabilidad y Rendimiento

### Optimizaciones Actuales
- **PostgreSQL:** Base de datos robusta para crecimiento futuro
- **Redis:** Caché y gestión de colas para procesamiento asíncrono
- **Containerización:** Isolación de servicios y escalabilidad
- **AI Local:** Ollama para procesamiento inteligente sin APIs externas
- **Modelos AI:** Estrategia progresiva según recursos disponibles
- **Parsing Inteligente:** IA local + fallback regex para robustez
- **Comunicación Interna:** Web App y API en la misma red Docker
- **Imágenes:** Compresión automática de facturas
- **API:** Paginación en consultas grandes

### Planes de Escalabilidad Futura
- **Base de Datos:** Migración a PostgreSQL si es necesario
- **Caché:** Redis para sesiones web si se requiere
- **CDN:** Optimización de imágenes vía Namecheap/CDN
- **Monitoreo:** Métricas de performance y uso
- **Load Balancer:** Si se requiere más de una instancia

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