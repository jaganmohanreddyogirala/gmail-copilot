import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


def is_transient_error(exc: Exception) -> bool:
    """Check if exception is transient and retryable."""
    err_str = str(exc).lower()
    return any(
        kw in err_str
        for kw in [
            "rate limit",
            "429",
            "500",
            "502",
            "503",
            "504",
            "timeout",
            "connection refused",
            "network",
            "service unavailable",
        ]
    )


# Standard retry decorator for LLM and API invocations
retry_on_transient_error = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(
        f"Retry attempt #{retry_state.attempt_number} due to transient error: {retry_state.outcome.exception()}"
    ),
    reraise=True,
)
