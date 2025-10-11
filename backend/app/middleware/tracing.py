"""
Request Tracing Middleware
Adds trace IDs to all requests for better observability
"""

import uuid
from fastapi import Request
from loguru import logger
import contextvars

# Context variable to store trace ID
trace_id_var = contextvars.ContextVar('trace_id', default=None)


def get_trace_id() -> str:
    """Get the current trace ID"""
    return trace_id_var.get()


async def tracing_middleware(request: Request, call_next):
    """
    Middleware to add trace IDs to all requests
    Adds X-Trace-ID header to request and response
    """
    # Check if trace ID is provided in request headers
    trace_id = request.headers.get('X-Trace-ID')

    # If not, generate a new one
    if not trace_id:
        trace_id = str(uuid.uuid4())

    # Store in context variable
    trace_id_var.set(trace_id)

    # Add to logger context
    with logger.contextualize(trace_id=trace_id):
        logger.info(f"Request started: {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Add trace ID to response headers
        response.headers['X-Trace-ID'] = trace_id

        logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}")

        return response
