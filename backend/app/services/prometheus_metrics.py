"""
Prometheus Metrics Service
Exports application metrics in Prometheus format
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict
import time

# Application info
app_info = Info('mispesos_app', 'MisPesos Application Information')
app_info.info({
    'version': '1.0.0',
    'service': 'mispesos-fastapi'
})

# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 30.0, 60.0, 90.0)
)

# ============================================================================
# AI Service Metrics
# ============================================================================

ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI parsing requests',
    ['status']  # success, failed, timeout, cached
)

ai_request_duration_seconds = Histogram(
    'ai_request_duration_seconds',
    'AI request processing time in seconds',
    buckets=(1.0, 5.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0, 75.0, 90.0, 120.0)
)

ai_confidence = Histogram(
    'ai_confidence',
    'AI parsing confidence scores',
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0)
)

ai_cache_hits = Counter(
    'ai_cache_hits_total',
    'Total AI cache hits'
)

ai_cache_misses = Counter(
    'ai_cache_misses_total',
    'Total AI cache misses'
)

ai_fallback_used = Counter(
    'ai_fallback_used_total',
    'Total times fallback regex parsing was used'
)

ai_active_requests = Gauge(
    'ai_active_requests',
    'Number of AI requests currently being processed'
)

# ============================================================================
# Transaction Metrics
# ============================================================================

transactions_total = Counter(
    'transactions_total',
    'Total transactions processed',
    ['action', 'category', 'payment_method']  # action: created, validated, corrected, deleted
)

transaction_amount = Histogram(
    'transaction_amount',
    'Transaction amounts',
    ['category'],
    buckets=(1000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000)
)

# ============================================================================
# Database Metrics
# ============================================================================

db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation']  # select, insert, update, delete
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

db_connection_errors = Counter(
    'db_connection_errors_total',
    'Total database connection errors'
)

# ============================================================================
# Ollama Service Metrics
# ============================================================================

ollama_requests_total = Counter(
    'ollama_requests_total',
    'Total requests to Ollama API',
    ['status']  # success, timeout, error
)

ollama_request_duration_seconds = Histogram(
    'ollama_request_duration_seconds',
    'Ollama API request duration in seconds',
    buckets=(5.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0, 75.0, 90.0)
)

ollama_model_loaded = Gauge(
    'ollama_model_loaded',
    'Whether Ollama model is loaded in memory',
    ['model']
)

# ============================================================================
# System Metrics
# ============================================================================

system_errors_total = Counter(
    'system_errors_total',
    'Total system errors',
    ['component', 'error_type']
)

# ============================================================================
# Helper Functions
# ============================================================================

def track_ai_request(duration: float, success: bool, confidence: float = None,
                     from_cache: bool = False, timeout: bool = False,
                     used_fallback: bool = False):
    """Track an AI request with all metrics"""

    # Determine status
    if from_cache:
        status = 'cached'
        ai_cache_hits.inc()
    elif timeout:
        status = 'timeout'
        ai_cache_misses.inc()
    elif success:
        status = 'success'
        ai_cache_misses.inc()
    else:
        status = 'failed'
        ai_cache_misses.inc()

    # Increment counters
    ai_requests_total.labels(status=status).inc()

    # Record duration (only if not from cache)
    if not from_cache:
        ai_request_duration_seconds.observe(duration)

    # Record confidence (if available)
    if confidence is not None:
        ai_confidence.observe(confidence)

    # Track fallback usage
    if used_fallback:
        ai_fallback_used.inc()


def track_transaction(action: str, category: str, payment_method: str, amount: float = None):
    """Track a transaction"""
    transactions_total.labels(
        action=action,
        category=category,
        payment_method=payment_method
    ).inc()

    if amount is not None:
        transaction_amount.labels(category=category).observe(amount)


def track_ollama_request(duration: float, success: bool, timeout: bool = False):
    """Track an Ollama API request"""
    if timeout:
        status = 'timeout'
    elif success:
        status = 'success'
    else:
        status = 'error'

    ollama_requests_total.labels(status=status).inc()
    ollama_request_duration_seconds.observe(duration)


def track_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track an HTTP request"""
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)
    ).inc()

    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


class AIRequestTracker:
    """Context manager for tracking AI requests"""

    def __init__(self):
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        ai_active_requests.inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ai_active_requests.dec()
        return False
