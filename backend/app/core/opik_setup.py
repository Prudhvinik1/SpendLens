"""
Opik observability setup for LLM tracing.

Opik provides:
- Automatic tracing of all LLM calls
- Token usage and latency metrics
- Ability to review and evaluate traces
- Integration with LangChain via callbacks

Key concepts:
- Project: Groups all traces for this app
- Trace: A single request/response flow (e.g., one upload processing)
- Span: Individual operations within a trace (e.g., one LLM call)
"""

import opik
from opik.integrations.langchain import OpikTracer

from app.core.config import settings


# Global flag to track initialization
_initialized = False


def init_opik() -> None:
    """
    Initialize Opik client.

    Call this once at app startup. Safe to call multiple times.
    """
    global _initialized

    if _initialized:
        return

    if not settings.OPIK_API_KEY:
        print("Warning: OPIK_API_KEY not set. Tracing will be disabled.")
        return

    try:
        opik.configure(
            api_key=settings.OPIK_API_KEY,
            project_name=settings.OPIK_PROJECT_NAME,
        )
        _initialized = True
        print(f"Opik initialized for project: {settings.OPIK_PROJECT_NAME}")
    except Exception as e:
        print(f"Failed to initialize Opik: {e}")


def get_opik_tracer(
    tags: list[str] | None = None,
    metadata: dict | None = None
) -> OpikTracer | None:
    """
    Get an Opik tracer for LangChain callbacks.

    Args:
        tags: Optional tags to add to traces (e.g., ["categorization", "batch"])
        metadata: Optional metadata dict (e.g., {"statement_id": 123})

    Returns:
        OpikTracer instance for use in LangChain callbacks, or None if not configured

    Usage with LangChain:
        tracer = get_opik_tracer(tags=["categorization"])
        result = chain.invoke(input, config={"callbacks": [tracer]})
    """
    if not settings.OPIK_API_KEY:
        return None

    # Ensure Opik is initialized
    init_opik()

    return OpikTracer(
        tags=tags or [],
        metadata=metadata or {}
    )


def create_trace_context(
    name: str,
    statement_id: int | None = None,
    metadata: dict | None = None
) -> dict:
    """
    Create a context dict for tracing a complete operation.

    This is used to group related LLM calls under a single trace.

    Args:
        name: Name of the operation (e.g., "process_statement")
        statement_id: Optional statement ID for linking
        metadata: Additional metadata to include

    Returns:
        Dict with trace configuration
    """
    ctx = {
        "trace_name": name,
        "tags": [name],
        "metadata": metadata or {}
    }

    if statement_id:
        ctx["metadata"]["statement_id"] = statement_id
        ctx["tags"].append(f"statement:{statement_id}")

    return ctx
