import contextvars

# Global context variables for tracing
correlation_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)

execution_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "execution_id", default=None
)


def get_correlation_id() -> str | None:
    return correlation_id_ctx.get()


def get_execution_id() -> str | None:
    return execution_id_ctx.get()
