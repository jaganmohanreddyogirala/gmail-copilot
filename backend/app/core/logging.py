import json
import logging
import sys
from datetime import datetime, timezone
from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter for production structured observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include additional contextual attributes if provided in record
        if hasattr(record, "email_id"):
            log_entry["email_id"] = record.email_id
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        if hasattr(record, "execution_time_ms"):
            log_entry["execution_time_ms"] = record.execution_time_ms

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_structured_logging():
    """Configure root logger to output structured JSON logs in production mode."""
    root_logger = logging.getLogger()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    if settings.APP_ENV.lower() == "production":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    root_logger.handlers = [handler]
    logging.getLogger("uvicorn.access").handlers = [handler]
