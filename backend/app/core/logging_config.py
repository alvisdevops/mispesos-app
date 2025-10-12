"""
Logging configuration with trace context
"""

import sys
import json
from loguru import logger
from app.core.telemetry import get_current_trace_id, get_current_span_id


def serialize_log(record):
    """
    Serialize log record to JSON with trace context

    Args:
        record: Loguru record

    Returns:
        JSON string with log data including trace context
    """
    trace_id = get_current_trace_id()
    span_id = get_current_span_id()

    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add trace context if available
    if trace_id:
        log_entry["trace_id"] = trace_id
    if span_id:
        log_entry["span_id"] = span_id

    # Add extra fields from record
    if record["extra"]:
        log_entry["extra"] = record["extra"]

    return json.dumps(log_entry)


def setup_logging():
    """
    Configure loguru for structured logging with trace context
    """
    # Remove default logger
    logger.remove()

    # Add console logger with JSON format
    logger.add(
        sys.stdout,
        format=serialize_log,
        level="INFO",
        serialize=True,
    )

    # Add file logger with JSON format
    logger.add(
        "/app/logs/mispesos-fastapi.log",
        format=serialize_log,
        level="INFO",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
        serialize=True,
    )

    logger.info("Logging configured with trace context support")
