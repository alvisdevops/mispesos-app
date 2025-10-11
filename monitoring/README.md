# Stack de Observabilidad MisPesos

Sistema completo de monitoreo y observabilidad para MisPesos usando Prometheus y Grafana.

## Componentes

### Prometheus
- **Puerto**: 9090
- **Propósito**: Recolección y almacenamiento de métricas
- **URL**: http://localhost:9090

Recolecta métricas de:
- Aplicación FastAPI (vía endpoint `/metrics`)
- Métricas del sistema
- Métricas de negocio personalizadas (requests de IA, transacciones, etc.)

### Grafana
- **Puerto**: 3000
- **Propósito**: Visualización de métricas y dashboards
- **URL**: http://localhost:3000
- **Credenciales por defecto**: admin/admin (cambiar en primer login)

Dashboards pre-configurados:
- **MisPesos Overview**: Dashboard principal con performance de IA, métricas HTTP y estadísticas de transacciones

## Métricas Disponibles

### Métricas del Servicio de IA
- `ai_requests_total` - Total de requests de parsing por estado (success, failed, timeout, cached)
- `ai_request_duration_seconds` - Tiempo de procesamiento de requests de IA
- `ai_confidence` - Scores de confianza del parsing de IA
- `ai_cache_hits_total` - Total de cache hits
- `ai_cache_misses_total` - Total de cache misses
- `ai_fallback_used_total` - Veces que se usó fallback regex
- `ai_active_requests` - Requests de IA procesándose actualmente

### Métricas de Transacciones
- `transactions_total` - Total de transacciones por acción, categoría y método de pago
- `transaction_amount` - Montos de transacciones por categoría

### Métricas HTTP
- `http_requests_total` - Total de requests HTTP por método, endpoint y status
- `http_request_duration_seconds` - Latencia de requests HTTP

### Métricas de Base de Datos
- `db_queries_total` - Total de queries por operación
- `db_query_duration_seconds` - Duración de queries
- `db_connection_errors_total` - Errores de conexión

### Métricas del Servicio Ollama
- `ollama_requests_total` - Total de requests a Ollama API por estado
- `ollama_request_duration_seconds` - Duración de requests a Ollama
- `ollama_model_loaded` - Si el modelo está cargado en memoria

## Ejemplos de Queries

### Performance de IA
```promql
# Tasa de requests de IA
rate(ai_requests_total[5m])

# Latencia p95 de IA
histogram_quantile(0.95, rate(ai_request_duration_seconds_bucket[5m]))

# Tasa de cache hits
rate(ai_cache_hits_total[5m]) / rate(ai_requests_total[5m])

# Tasa de timeouts
rate(ai_requests_total{status="timeout"}[5m]) / rate(ai_requests_total[5m])
```

### Analítica de Transacciones
```promql
# Tasa de transacciones por categoría
rate(transactions_total[5m])

# Transacciones por método de pago
sum by (payment_method) (rate(transactions_total[5m]))
```

### Salud del Sistema
```promql
# Tasa de errores HTTP
rate(http_requests_total{status=~"5.."}[5m])

# Latencia p99 de requests
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

## Trazabilidad de Requests

Cada request HTTP recibe un trace ID único para trazabilidad end-to-end:

- **Header**: `X-Trace-ID`
- **Formato**: UUID v4
- **Uso**: Aparece en logs y headers de respuesta

Ejemplo:
```bash
curl -H "X-Trace-ID: 123e4567-e89b-12d3-a456-426614174000" http://localhost:8000/api/v1/health/metrics
```

## Persistencia de Datos

Todos los datos de monitoreo se persisten en `/var/lib/mispesos`:
- `prometheus/` - Datos de series temporales de Prometheus
- `grafana/` - Dashboards y configuración de Grafana

## Acceso a Dashboards

1. **Iniciar el stack**:
   ```bash
   docker compose up -d
   ```

2. **Acceder a Grafana**:
   - URL: http://localhost:3000
   - Login: admin/admin
   - Navegar a Dashboards > MisPesos Overview

3. **Acceder a Prometheus**:
   - URL: http://localhost:9090
   - Usar la interfaz de queries para explorar métricas

## Configuración

### Prometheus
Archivo de configuración: `prometheus/prometheus.yml`

- Intervalo de scrape: 15s
- Intervalo de evaluación: 15s

### Grafana
- Datasource: Provisionado automáticamente desde `grafana/provisioning/datasources/`
- Dashboards: Cargados automáticamente desde `grafana/provisioning/dashboards/`
- **Credenciales**: admin/admin (valores por defecto, no requiere configuración adicional)

## Troubleshooting

### Verificar targets de Prometheus
Visita http://localhost:9090/targets para ver si FastAPI se está scrapeando exitosamente.

### Verificar datasource de Grafana
1. Ir a Configuration > Data Sources
2. Verificar que el datasource de Prometheus esté conectado

### Ver logs
```bash
docker logs mispesos-prometheus
docker logs mispesos-grafana
```

## Agregar Métricas Personalizadas

1. Definir métrica en `backend/app/services/prometheus_metrics.py`
2. Trackear métrica en tu código:
   ```python
   from app.services.prometheus_metrics import mi_metrica_custom
   mi_metrica_custom.inc()
   ```
3. Consultar en Grafana o Prometheus UI

## Notas de Performance

- Retención de Prometheus: 15 días por defecto
- Intervalo de scrape optimizado para bajo uso de recursos
- Refresh de Grafana: 5s para monitoreo en tiempo real
- Rotación de logs habilitada (10MB, 3 archivos) para prevenir problemas de espacio en disco
