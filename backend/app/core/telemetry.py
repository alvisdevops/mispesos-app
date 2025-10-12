"""
OpenTelemetry configuration for distributed tracing
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def setup_telemetry(app):
    """
    Configure OpenTelemetry for the FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Configure resource with service information
    resource = Resource.create({
        SERVICE_NAME: "mispesos-fastapi",
        SERVICE_VERSION: "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "app": "backend",
    })

    # Create TracerProvider with resource
    tracer_provider = TracerProvider(resource=resource)

    # Configure OTLP exporter to send traces to Tempo
    tempo_endpoint = os.getenv("TEMPO_ENDPOINT", "http://tempo:4318/v1/traces")
    otlp_exporter = OTLPSpanExporter(
        endpoint=tempo_endpoint,
        # timeout=10,
    )

    # Add BatchSpanProcessor to send spans in batches
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy (will auto-instrument when engine is used)
    SQLAlchemyInstrumentor().instrument()

    # Instrument Redis
    RedisInstrumentor().instrument()

    # Instrument HTTPX
    HTTPXClientInstrumentor().instrument()

    print(f"✅ OpenTelemetry configured - sending traces to {tempo_endpoint}")


def get_tracer(name: str = __name__):
    """
    Get a tracer instance

    Args:
        name: Name for the tracer

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def get_current_trace_id() -> str:
    """
    Get the current trace ID from the active span

    Returns:
        Trace ID as hex string, or empty string if no active span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return ""


def get_current_span_id() -> str:
    """
    Get the current span ID from the active span

    Returns:
        Span ID as hex string, or empty string if no active span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, '016x')
    return ""
