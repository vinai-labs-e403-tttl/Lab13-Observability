from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import observe, get_client
    from langfuse.types import TraceContext

    langfuse = get_client()

    class _LangfuseContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            # v4: user_id, session_id, tags không có update_current_trace
            # Gắn vào metadata của span hiện tại
            trace_meta: dict = {}
            for key in ("user_id", "session_id", "tags"):
                if key in kwargs:
                    trace_meta[key] = kwargs.pop(key)
            if trace_meta:
                existing = kwargs.get("metadata", {}) or {}
                existing.update(trace_meta)
                kwargs["metadata"] = existing
            if kwargs:
                langfuse.update_current_span(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            # usage_details được hỗ trợ trong start_as_current_observation nhưng không trong update
            # Merge vào metadata
            usage = kwargs.pop("usage_details", None)
            if usage:
                meta = kwargs.get("metadata", {}) or {}
                meta["usage_details"] = usage
                kwargs["metadata"] = meta
            langfuse.update_current_span(**kwargs)

    langfuse_context = _LangfuseContext()

except ImportError:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
