# Plan de Desarrollo MisPesos

## Estrategia de Implementación

El desarrollo se ejecutará en 4 fases incrementales, cada una entregando valor funcional y permitiendo validación temprana del sistema. Cada fase es completamente funcional y puede usarse independientemente.

## Fase 1: MVP Básico (Semanas 1-3)

### Objetivo
Establecer la infraestructura básica y funcionalidad core del bot de Telegram con almacenamiento local.

### Componentes a Desarrollar

#### 1.1 Configuración de Infraestructura
- **Servidor Home:** Configuración completa del ambiente Docker en alvis-server
- **Base de Datos:** Setup inicial de PostgreSQL con esquema completo
- **Entorno:** Containerización completa con Docker Compose para desarrollo y producción
- **Redis:** Configuración de cache y queue manager

#### 1.2 Bot de Telegram Core
- **Registro con BotFather:** Creación y configuración del bot
- **Webhook Setup:** Configuración de webhook (durante desarrollo usar ngrok o similar, en producción usar IP pública + port forwarding)
- **Parsing Básico:** Interpretación de mensajes simples ("50k almuerzo efectivo")
- **Comandos Básicos:**
  - `/start` - Bienvenida y setup inicial
  - `/help` - Guía de uso
  - `/resumen` - Gastos del día/semana
  - `/balance` - Estado actual simple

#### 1.3 API Core (FastAPI)
- **Estructura base:** Configuración de FastAPI con estructura modular
- **Endpoints básicos:**
  - `POST /transactions` - Crear transacción
  - `GET /transactions` - Listar transacciones
  - `GET /summary/{period}` - Resúmenes básicos
- **Modelos de datos:** SQLAlchemy models básicos

#### 1.4 Sistema de Categorización Básico
- **Categorías predefinidas:** Alimentación, Transporte, Servicios, Otros
- **Matching simple:** Por palabras clave básicas
- **Fallback manual:** Solicitar categoría si no se detecta

### Entregables Fase 1
- [ ] Bot funcional con parsing básico de mensajes
- [ ] Base de datos SQLite operativa con esquema completo
- [ ] API REST básica con endpoints core
- [ ] Sistema de categorización por palabras clave
- [ ] Comandos básicos funcionando
- [ ] Setup de desarrollo con Docker
- [ ] Tests unitarios básicos

### Criterios de Éxito Fase 1
- Usuario puede enviar "25k uber efectivo" y recibir confirmación
- `/resumen` devuelve gastos del día correctamente
- Base de datos almacena transacciones sin errores
- Bot responde en menos de 5 segundos
- 100% uptime durante testing de 3 días

---

## Fase 2: OCR y Web App Básica (Semanas 4-7)

### Objetivo
Agregar procesamiento de facturas mediante OCR y dashboard web básico para visualización.

### Componentes a Desarrollar

#### 2.1 OCR Engine
- **Tesseract Integration:** Setup y configuración de Tesseract OCR
- **Preprocessing:** Mejora de imágenes para mejor precisión OCR
- **Data Extraction:** Parsing de texto OCR para extraer campos específicos:
  - Monto total
  - Fecha de transacción
  - Nombre del establecimiento
  - NIT/RUT (si disponible)
- **File Storage:** Sistema de almacenamiento de imágenes originales

#### 2.2 Enhanced Telegram Bot
- **Photo Processing:** Recepción y procesamiento de imágenes
- **OCR Workflow:** Flujo completo desde foto hasta transacción confirmada
- **Error Handling:** Manejo de casos donde OCR falla
- **User Feedback:** Estados de procesamiento ("📸 Procesando factura...")

#### 2.3 Web Application Frontend (Containerizada)
- **React Setup:** Configuración de React con Tailwind CSS en contenedor
- **Container Config:** Dockerfile optimizado para producción
- **Páginas básicas:**
  - Dashboard principal con KPIs básicos
  - Lista de transacciones (tabla simple)
  - Vista de detalle de transacción
- **Gráficos básicos:** Gastos por categoría, tendencia por días
- **Responsive Design:** Mobile-first approach
- **Integración Docker:** Comunicación interna con FastAPI container

#### 2.4 API Extensions & Container Integration
- **Endpoints adicionales:**
  - `POST /receipts/process` - Procesar imagen OCR (con Redis queue)
  - `GET /dashboard/stats` - Estadísticas para dashboard
  - `GET /receipts/{id}` - Ver factura almacenada
- **File Upload:** Manejo de subida de archivos con volúmenes Docker
- **Data Aggregation:** Endpoints para datos agregados (gráficos)
- **Container Communication:** Configuración de red Docker interna

### Entregables Fase 2
- [ ] OCR funcional con precisión >80% en facturas comunes
- [ ] Almacenamiento de imágenes con metadatos en volúmenes Docker
- [ ] Web app containerizada con dashboard y lista de transacciones
- [ ] Gráficos de gastos por categoría y tiempo
- [ ] Bot procesa fotos y confirma datos extraídos
- [ ] Deploy completo con Docker Compose en alvis-server
- [ ] API extendida con endpoints para dashboard
- [ ] Redis queue funcionando para procesamiento asíncrono

### Criterios de Éxito Fase 2
- Usuario puede fotografiar factura y obtener transacción completa
- Dashboard web muestra gastos del mes actual correctamente
- OCR extrae monto correcto en >85% de facturas de prueba
- Web app carga en menos de 3 segundos
- Imágenes se almacenan y recuperan sin corrupción

---

## Fase 3: Funcionalidades Avanzadas (Semanas 8-10)

### Objetivo
Implementar categorización inteligente, reportes avanzados y módulo fiscal básico.

### Componentes a Desarrollar

#### 3.1 Categorización Inteligente
- **Machine Learning Básico:** Algoritmo de clasificación automática basado en:
  - Texto de descripción
  - Monto de transacción
  - Nombre del establecimiento (de OCR)
  - Patrones históricos del usuario
- **Auto-learning:** Sistema que aprende de correcciones manuales
- **Keywords Management:** Interface para gestionar palabras clave por categoría

#### 3.2 Módulo Fiscal
- **Gestión de Facturas:** 
  - Organización por período fiscal
  - Clasificación de gastos deducibles
  - Vista de imágenes almacenadas
- **Reportes Fiscales:**
  - Exportación de facturas por período
  - Resumen de gastos deducibles
  - Datos organizados para declaración de renta

#### 3.3 Reportes Avanzados
- **Dashboard Mejorado:**
  - Comparativos mes vs mes
  - Predicciones de gasto
  - Alertas de presupuesto
  - Análisis de patrones
- **Exportación:**
  - Excel con datos detallados
  - PDF con reportes ejecutivos
  - CSV para análisis externo

#### 3.4 Funcionalidades de Usuario Avanzadas
- **Presupuestos:** Definir y monitorear presupuestos por categoría
- **Metas Financieras:** Setup y tracking de metas de ahorro
- **Correcciones Masivas:** Interface para editar múltiples transacciones
- **Búsqueda Avanzada:** Filtros complejos y búsqueda por texto libre

### Entregables Fase 3
- [ ] Sistema de categorización automática funcionando
- [ ] Módulo fiscal con organización de facturas
- [ ] Reportes avanzados con gráficos mejorados
- [ ] Exportación a Excel, PDF y CSV
- [ ] Sistema de presupuestos y alertas
- [ ] Interface de correcciones y gestión masiva
- [ ] Búsqueda y filtros avanzados

### Criterios de Éxito Fase 3
- Categorización automática correcta en >90% de transacciones conocidas
- Módulo fiscal organiza facturas correctamente por período
- Exportación a Excel mantiene formato y fórmulas
- Presupuestos alertan correctamente al superarse
- Búsqueda encuentra transacciones en menos de 1 segundo

---

## Fase 4: Optimización y Deploy Producción (Semanas 11-12)

### Objetivo
Deploy completo en producción, optimización de performance y setup de monitoreo.

### Componentes a Desarrollar

#### 4.1 Production Deployment
- **Docker Production:** Configuración optimizada para producción con compose
- **Port Forwarding:** Configuración del router para puertos 80/443 y 8000 (requiere coordinación)
- **Web App Deploy:** Web app containerizada en el mismo servidor
- **Database Optimization:** PostgreSQL con índices y optimizaciones de performance
- **SSL/Security:** Configuración completa de seguridad con certificados
- **Container Orchestration:** Health checks, restart policies, resource limits

#### 4.2 Monitoreo y Logging
- **Health Monitoring:** Checks automáticos de todos los componentes
- **Logging System:** Logs estructurados con rotación automática
- **Error Tracking:** Sistema de alertas por errores críticos
- **Performance Metrics:** Monitoreo de tiempos de respuesta y uso

#### 4.3 Backup y Recuperación
- **Automated Backup:** Backup diario automático de base de datos
- **Image Backup:** Respaldo de facturas almacenadas
- **Recovery Procedures:** Procedimientos documentados de recuperación
- **Backup Verification:** Tests automáticos de integridad de backups

#### 4.4 Documentation y Training
- **User Manual:** Guía completa de uso del sistema
- **Admin Guide:** Manual técnico de administración
- **API Documentation:** Documentación completa de endpoints
- **Troubleshooting Guide:** Guía de solución de problemas comunes

### Entregables Fase 4
- [ ] Sistema completamente desplegado en producción
- [ ] Monitoreo automático con alertas configuradas
- [ ] Backup automático funcionando y verificado
- [ ] Documentación completa de usuario y técnica
- [ ] Performance optimizado para uso personal
- [ ] Procedimientos de mantenimiento establecidos
- [ ] Sistema de alertas por email configurado

### Criterios de Éxito Fase 4
- Sistema funciona 24/7 sin intervención manual
- Backups se ejecutan automáticamente y son verificables
- Tiempo de respuesta promedio <2 segundos
- Alertas llegan correctamente en caso de errores
- Usuario puede usar sistema sin asistencia técnica
- Recovery completo desde backup en <30 minutos

---

## Metodología de Desarrollo

### Approach General
- **Incremental Development:** Cada semana entrega funcionalidad usable
- **Test-Driven:** Tests unitarios para funciones críticas
- **User Feedback:** Validación continua de funcionalidades
- **Documentation First:** Documentar antes de implementar

### Tools y Frameworks

#### Backend (Containerizado)
- **Python 3.11+** con FastAPI en contenedor
- **PostgreSQL 15** como base de datos principal
- **Redis 7** para cache y queue management
- **SQLAlchemy** para ORM
- **Alembic** para migraciones de DB
- **pytest** para testing
- **python-telegram-bot** para integración Telegram
- **Tesseract OCR** para procesamiento de imágenes en contenedor dedicado

#### Frontend (Containerizado)
- **React 18** con TypeScript en contenedor Node.js
- **Tailwind CSS** para estilos
- **Recharts** para gráficos
- **React Query** para manejo de estado servidor
- **Vite** como bundler
- **Nginx** como reverse proxy y servidor web

#### DevOps
- **Docker & Docker Compose** para containerización completa
- **GitHub Actions** para CI/CD (opcional)
- **Router Port Forwarding** para conectividad Web App y API
- **systemd** para gestión de Docker en producción
- **Docker Networks** para comunicación interna segura
- **Docker Volumes** para persistencia de datos

### Testing Strategy
- **Unit Tests:** Funciones de parsing, OCR, categorización
- **Integration Tests:** APIs, bot workflows, database operations
- **E2E Tests:** Flujos completos usuario-bot-web
- **Manual Testing:** Validación de OCR con facturas reales

### Git Workflow
- **Main Branch:** Código de producción
- **Develop Branch:** Integración de features
- **Feature Branches:** Desarrollo de funcionalidades específicas
- **Conventional Commits:** Para mejor tracking de cambios

---

## Cronograma Detallado

### Semana 1: Infrastructure Setup
- [ ] Configuración completa del servidor Ubuntu con Docker
- [ ] Setup de contenedores base (PostgreSQL, Redis)
- [ ] Configuración inicial de PostgreSQL con schema
- [ ] Setup completo de Docker Compose para desarrollo
- [ ] Configuración de redes y volúmenes Docker

### Semana 2: Bot Basic Functionality  
- [ ] Registro y configuración del bot de Telegram
- [ ] Implementación de parsing básico de mensajes
- [ ] Comandos básicos (/start, /help, /resumen)
- [ ] Integración bot-API-database

### Semana 3: Core Features Polish
- [ ] Sistema de categorización por keywords
- [ ] Manejo de errores y edge cases
- [ ] Tests unitarios y validación
- [ ] Deploy básico para testing

### Semana 4: OCR Foundation
- [ ] Setup y configuración de Tesseract
- [ ] Implementación básica de procesamiento de imágenes
- [ ] Extracción de datos básicos de facturas
- [ ] Storage de imágenes

### Semana 5: OCR Integration
- [ ] Integración OCR con bot de Telegram
- [ ] Workflow completo de procesamiento de facturas
- [ ] Validación y corrección manual de datos OCR
- [ ] Optimización de precisión

### Semana 6: Web App Foundation
- [ ] Setup de React con Tailwind en contenedor
- [ ] Dockerfile optimizado para frontend
- [ ] Dashboard básico con KPIs simples
- [ ] Lista de transacciones con filtros básicos
- [ ] Integración con API backend via red Docker interna

### Semana 7: Web App Core Features
- [ ] Gráficos básicos de gastos
- [ ] Vista de detalle de transacciones
- [ ] Integración completa con Docker Compose
- [ ] Mobile responsiveness
- [ ] Nginx reverse proxy configurado

### Semana 8: Smart Categorization
- [ ] Algoritmo de categorización inteligente
- [ ] Auto-learning desde correcciones
- [ ] Interface de gestión de categorías
- [ ] Optimización de precisión

### Semana 9: Advanced Reporting
- [ ] Módulo fiscal básico
- [ ] Reportes avanzados con comparativos
- [ ] Sistema de exportación (Excel, PDF)
- [ ] Análisis de patrones de gasto

### Semana 10: User Features
- [ ] Sistema de presupuestos y alertas
- [ ] Búsqueda avanzada y filtros
- [ ] Correcciones masivas
- [ ] Predicciones de gasto

### Semana 11: Production Deployment
- [ ] Configuración de producción optimizada con Docker
- [ ] Configuración de port forwarding en router (coordinación con admin de red)
- [ ] Deploy final containerizado completo
- [ ] Configuración de SSL y seguridad con Nginx
- [ ] Health checks y monitoring de contenedores

### Semana 12: Monitoring & Documentation
- [ ] Sistema completo de monitoreo
- [ ] Backup automático configurado
- [ ] Documentación de usuario completa
- [ ] Procedures de mantenimiento

---

## Consideraciones Especiales

### Restricciones del Entorno
- **Acceso Físico Limitado:** Todo debe configurarse remotamente
- **Port Forwarding limitado:** Requiere coordinación con administrador de red
- **Hardware Limitado:** PC viejo debe manejar carga eficientemente
- **Conectividad:** Dependencia de internet doméstico estable

### Mitigación de Riesgos
- **Backup Redundante:** Local + remoto automático
- **Fallback Modes:** OCR manual si falla automático
- **Error Recovery:** Sistema robusto de manejo de errores
- **Performance Monitoring:** Alertas por problemas de rendimiento

### Success Metrics
- **Adoption:** Uso diario consistente >25 días/mes
- **Accuracy:** OCR correcta >85%, categorización >90%
- **Performance:** Bot respuesta <5s, Web <3s
- **Reliability:** Uptime >99%, cero pérdida de datos

---

**Documento:** DEVELOPMENT_PLAN.md  
**Versión:** 1.0  
**Fecha:** Septiembre 2025  
**Estado:** Plan aprobado, listo para ejecución