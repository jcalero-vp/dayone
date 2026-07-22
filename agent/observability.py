"""Observability helpers for local and AgentCore Runtime deployments.

The workshop starts with plain stdout logs that are CloudWatch-ready (one JSON
line per record). When the app is actually deployed to AWS, these log records
can be picked up by CloudWatch Logs and optionally correlated with X-Ray via
environment variables or the AWS OpenTelemetry/CloudWatch agents.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Preserve structured fields added via `extra={...}` on the logger call.
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
            }:
                payload[key] = value

        return json.dumps(payload, default=str)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger to emit JSON to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)


def emit_metric(name: str, value: float, unit: str = "Count", **dimensions: str) -> None:
    """Emit a metric record as a JSON log line.

    In production this is replaced by a CloudWatch `put_metric_data` call or by
    an embedded metric format (EMF) log event that CloudWatch Logs parses.
    """
    metric = {
        "metric_name": name,
        "metric_value": value,
        "metric_unit": unit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dimensions": dimensions,
    }
    logging.getLogger("metrics").info("metric", extra=metric)
