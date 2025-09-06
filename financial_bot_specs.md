# Sistema de Gestión Financiera Personal
## Especificaciones Técnicas del Proyecto

### 1. RESUMEN EJECUTIVO

**Objetivo:** Desarrollar un sistema automatizado de gestión financiera personal que permita registrar gastos e ingresos de manera rápida y natural a través de Telegram, con visualización completa en una aplicación web personal.

**Problema a resolver:** Abandono del control financiero manual en Excel debido a la fricción del proceso, resultando en descontrol de cuentas personales.

**Solución:** Bot de Telegram para captura instantánea + Web App para análisis y visualización completa.

---

### 2. ARQUITECTURA DEL SISTEMA

#### 2.1 Componentes Principales
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │◄──►│  Raspberry Pi 5  │◄──►│   Web App       │
│   (Captura)     │    │  (Procesamiento) │    │ (Visualización) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────▼──────┐
                       │ Base de     │
                       │ Datos Local │
                       └─────────────┘
```

#### 2.2 Infraestructura
- **Servidor Principal:** Raspberry Pi 5 ($50 USD)
- **Hosting Web App:** Hosting compartido Namecheap (existente)
- **Base de Datos:** SQLite en Raspberry Pi
- **Dominio:** Dominio existente en Namecheap
- **Conectividad:** Túnel Cloudflare gratuito

#### 2.3 Costos Operativos
- **Inicial:** ~$70 USD (Raspberry Pi + accesorios)
- **Mensual:** ~$2-3 USD (electricidad)
- **Hosting:** $0 (ya existente)

---

### 3. ESPECIFICACIONES FUNCIONALES

#### 3.1 Bot de Telegram

**Funcionalidades de Captura:**
- **Texto natural:** "50k almuerzo tarjeta" → Procesamiento automático
- **Fotos de facturas:** OCR automático + almacenamiento de imagen
- **Procesamiento en tiempo real:** Respuesta inmediata (2-10 segundos)

**Comandos del Bot:**
- `/resumen` - Gastos del día/semana/mes
- `/categorias` - Vista por categorías de gasto
- `/balance` - Estado financiero actual
- `/corregir` - Editar último registro
- `/ayuda` - Guía de uso

**Parsing Inteligente de Mensajes:**
```
Entrada: "hoy gasté 100 mil en almuerzo en la oficina"
Extracción automática:
├── Fecha: Fecha actual
├── Hora: Timestamp del mensaje
├── Monto: $100,000
├── Categoría: Alimentación (por "almuerzo")
├── Descripción: "Almuerzo en la oficina"
├── Ubicación: "Oficina"
└── Medio de pago: Solicitar confirmación
```

#### 3.2 Procesamiento OCR de Facturas

**Datos extraídos automáticamente:**
- Monto total
- Fecha y hora de la transacción
- Empresa/establecimiento
- NIT/RUT del emisor
- Número de factura
- Items detallados (cuando sea posible)
- Impuestos (IVA, otros)

**Almacenamiento:**
- Datos estructurados en base de datos
- Imagen original como adjunto
- Metadatos para declaración de impuestos

#### 3.3 Web Application

**Dashboard Ejecutivo:**
- KPIs financieros principales
- Gráficos de tendencias por período
- Resumen de gastos por categorías
- Alertas de presupuesto
- Comparativos mes a mes

**Vista Detallada (Tipo Excel Mejorado):**
- Tabla completa de todas las transacciones
- Filtros avanzados (fecha, categoría, monto, medio de pago)
- Ordenamiento por cualquier campo
- Búsqueda por texto libre
- Edición in-line de registros

**Módulo Fiscal:**
- Facturas organizadas por período fiscal
- Exportación para declaración de impuestos
- Visualización de facturas almacenadas
- Reportes de gastos deducibles

**Funcionalidades Avanzadas:**
- Metas y presupuestos por categoría
- Predicciones de gasto
- Análisis de patrones
- Exportación (Excel, PDF, CSV)

---

### 4. ESPECIFICACIONES TÉCNICAS

#### 4.1 Stack Tecnológico

**Raspberry Pi (Servidor Principal):**
- **OS:** Raspberry Pi OS Lite
- **Runtime:** Python 3.11+
- **Framework Bot:** python-telegram-bot
- **Base de Datos:** SQLite
- **OCR:** Tesseract OCR
- **Web Framework:** FastAPI
- **Containerización:** Docker + Docker Compose

**Web Application:**
- **Frontend:** React.js + Tailwind CSS
- **Backend API:** FastAPI (mismo servidor Pi)
- **Hosting:** Namecheap hosting compartido
- **Comunicación:** REST API entre web app y servidor Pi

#### 4.2 Base de Datos - Modelo de Datos

```sql
-- Tabla principal de transacciones
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(12,2) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    payment_method VARCHAR(20), -- 'efectivo', 'tarjeta', 'transferencia'
    location VARCHAR(100),
    telegram_message_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de facturas/recibos
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER REFERENCES transactions(id),
    original_filename VARCHAR(255),
    file_path VARCHAR(500),
    ocr_text TEXT,
    company_name VARCHAR(200),
    company_nit VARCHAR(20),
    receipt_number VARCHAR(50),
    tax_amount DECIMAL(10,2),
    receipt_date DATE,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de categorías
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    color_hex VARCHAR(7),
    is_income BOOLEAN DEFAULT FALSE,
    parent_category_id INTEGER REFERENCES categories(id)
);

-- Tabla de palabras clave para categorización automática
CREATE TABLE category_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    keyword VARCHAR(100),
    weight DECIMAL(3,2) DEFAULT 1.0
);
```

#### 4.3 APIs y Integraciones

**Telegram Bot API:**
- Webhook para recepción de mensajes
- Procesamiento de texto y archivos
- Respuestas automáticas con confirmación

**OCR Integration:**
- Tesseract OCR para extracción de texto
- Pre-procesamiento de imágenes para mejor precisión
- Post-procesamiento para extracción de datos específicos

**Conectividad Externa:**
- Cloudflare Tunnel para acceso remoto
- API REST para comunicación web app ↔ servidor Pi
- Backup automático a hosting Namecheap

---

### 5. CASOS DE USO DETALLADOS

#### 5.1 Caso de Uso: Registro de Gasto por Texto
```
Actor: Usuario
Flujo principal:
1. Usuario envía mensaje: "25k uber efectivo"
2. Bot procesa y extrae: monto=$25,000, categoría=transporte, pago=efectivo
3. Bot responde: "✅ Registrado: $25,000 - Transporte - Efectivo"
4. Sistema guarda en base de datos
5. Web app se actualiza automáticamente

Flujo alternativo:
- Si bot no puede determinar categoría, solicita aclaración
- Usuario puede corregir con /corregir
```

#### 5.2 Caso de Uso: Procesamiento de Factura
```
Actor: Usuario
Flujo principal:
1. Usuario envía foto de factura
2. Bot responde: "📸 Procesando factura..."
3. OCR extrae datos: monto, empresa, NIT, fecha, items
4. Bot presenta datos extraídos para confirmación
5. Usuario confirma o corrige
6. Sistema guarda transacción + imagen + metadatos fiscales
7. Bot responde: "✅ Factura registrada y almacenada"

Flujo de error:
- Si OCR falla, solicita datos mínimos manualmente
```

#### 5.3 Caso de Uso: Consulta de Resumen
```
Actor: Usuario
Flujo principal:
1. Usuario envía /resumen
2. Bot consulta base de datos
3. Bot responde con:
   - Total gastado hoy
   - Comparativo con ayer
   - Top 3 categorías del día
   - Balance disponible estimado

Opciones:
- /resumen semana
- /resumen mes
- /resumen categoria alimentacion
```

---

### 6. PLAN DE DESARROLLO

#### 6.1 Fase 1 - MVP Básico (2-3 semanas)
**Objetivos:**
- Bot básico funcionando
- Registro manual por texto
- Base de datos operativa
- Comandos básicos

**Entregables:**
- Bot de Telegram operativo
- Base de datos SQLite configurada
- Parsing básico de mensajes de texto
- Comandos: /resumen, /ayuda

#### 6.2 Fase 2 - OCR y Web App (3-4 semanas)
**Objetivos:**
- Procesamiento de facturas
- Web app básica
- Visualizaciones principales

**Entregables:**
- OCR de facturas funcionando
- Almacenamiento de imágenes
- Web app con dashboard básico
- Vista de transacciones

#### 6.3 Fase 3 - Funcionalidades Avanzadas (2-3 semanas)
**Objetivos:**
- Categorización inteligente
- Reportes avanzados
- Módulo fiscal

**Entregables:**
- Aprendizaje automático de categorías
- Reportes personalizables
- Exportación de datos
- Gestión de facturas para impuestos

#### 6.4 Fase 4 - Optimización y Deploy (1-2 semanas)
**Objetivos:**
- Deploy en Raspberry Pi
- Optimización de performance
- Monitoreo y logs

**Entregables:**
- Sistema productivo en Raspberry Pi
- Túnel Cloudflare configurado
- Web app desplegada en Namecheap
- Documentación de usuario

---

### 7. CONSIDERACIONES DE SEGURIDAD

#### 7.1 Datos Financieros
- Encriptación de datos sensibles en base de datos
- Backup encriptado automático
- Acceso restringido por IP/VPN
- Logs de auditoría de transacciones

#### 7.2 Acceso al Sistema
- Autenticación por Telegram User ID
- Web app con login seguro
- Rate limiting en APIs
- Monitoreo de accesos sospechosos

#### 7.3 Privacidad
- Datos nunca salen del entorno controlado (Pi + hosting propio)
- No uso de servicios de terceros para datos sensibles
- Anonimización para logs de debugging

---

### 8. MONITOREO Y MANTENIMIENTO

#### 8.1 Monitoreo Operativo
- Health checks automáticos del bot
- Alertas por email en caso de fallos
- Monitoreo de espacio en disco
- Backup automático diario

#### 8.2 Métricas de Uso
- Número de transacciones por día
- Tiempo de respuesta del bot
- Tasa de éxito del OCR
- Uso de categorías más frecuentes

#### 8.3 Mantenimiento
- Actualizaciones de seguridad automáticas
- Rotación de logs
- Optimización periódica de base de datos
- Backup verificado semanal

---

### 9. CRONOGRAMA Y PRESUPUESTO

#### 9.1 Timeline del Proyecto
```
Semana 1-3:   Fase 1 - MVP Básico
Semana 4-7:   Fase 2 - OCR y Web App  
Semana 8-10:  Fase 3 - Funcionalidades Avanzadas
Semana 11-12: Fase 4 - Deploy y Optimización
```

#### 9.2 Presupuesto Total
```
Hardware:
├── Raspberry Pi 5: $50
├── MicroSD 64GB: $15
├── Fuente oficial: $10
└── Case/accesorios: $15
Total Hardware: $90

Costos Operativos (anuales):
├── Electricidad: $30
├── Dominio: $0 (ya existente)
└── Hosting: $0 (ya existente)
Total Anual: $30

ROI: Sistema se paga solo vs VPS en 18 meses
```

---

### 10. RIESGOS Y MITIGACIONES

#### 10.1 Riesgos Técnicos
**Riesgo:** Falla de Raspberry Pi
**Mitigación:** Backup automático + procedimiento de restauración rápida

**Riesgo:** Precisión baja del OCR  
**Mitigación:** Fallback a entrada manual + mejora iterativa del modelo

**Riesgo:** Límites de Telegram API
**Mitigación:** Monitoreo de quotas + implementación de queue si necesario

#### 10.2 Riesgos Operativos
**Riesgo:** Pérdida de datos
**Mitigación:** Backup triple (local + hosting + cloud)

**Riesgo:** Acceso no autorizado
**Mitigación:** VPN + autenticación robusta + monitoreo

**Riesgo:** Corte de internet doméstico
**Mitigación:** Modo offline + sincronización automática al reconectar

---

### 11. CRITERIOS DE ÉXITO

#### 11.1 Métricas Cuantitativas
- **Tiempo de registro:** < 30 segundos por transacción
- **Precisión OCR:** > 85% en facturas estándar
- **Uptime del sistema:** > 99%
- **Tiempo de respuesta web:** < 3 segundos

#### 11.2 Objetivos Cualitativos
- Uso diario consistente (> 80% de días en el mes)
- Reducción significativa de transacciones no registradas
- Satisfacción personal con el control financiero
- Facilidad de declaración de impuestos

---

### 12. DOCUMENTACIÓN ADICIONAL

#### 12.1 Manuales Requeridos
- Manual de instalación en Raspberry Pi
- Guía de usuario del bot de Telegram
- Tutorial de uso de la web app
- Procedimientos de backup y recuperación

#### 12.2 Documentación Técnica
- API documentation (endpoints REST)
- Esquema de base de datos detallado
- Configuración de infraestructura
- Procedimientos de troubleshooting

---

**Documento creado:** Septiembre 2025  
**Versión:** 1.0  
**Estado:** Especificación completa lista para desarrollo