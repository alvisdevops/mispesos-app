"""
Logging configuration with trace context
"""

import sys
import json
from loguru import logger
from app.core.telemetry import get_current_trace_id, get_current_span_id


def patching_sink(message):
    """
    Custom sink that patches log records to include trace context
    and outputs as JSON
    """
    record = message.record
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
        for key, value in record["extra"].items():
            if key not in log_entry:
                log_entry[key] = value

    print(json.dumps(log_entry), flush=True)


def setup_logging():
    """
    Configure loguru for structured logging with trace context
    """
    # Remove default logger
    logger.remove()

    # Add console logger with custom sink for JSON output
    logger.add(
        patching_sink,
        level="INFO",
    )

    # Add file logger with simple format
    logger.add(
        "/app/logs/mispesos-fastapi.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
    )

    logger.info("Logging configured with trace context support")
