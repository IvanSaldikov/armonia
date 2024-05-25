import json
import logging
import os
import sys

import ecs_logging
import structlog


def mydumps(dic, **kw):
    mod = {}
    if "event" in dic:
        mod["event"] = dic["event"]
    for k in dic:
        if k != "event":
            mod[k] = dic[k]
    return json.dumps(mod, **kw)


structlog_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(),
]
STRUCTLOG_ENABLED = os.environ.get("STRUCTLOG_ENABLED", "false") == "true"
if STRUCTLOG_ENABLED:
    structlog_processors += [structlog.processors.JSONRenderer(serializer=mydumps)]
else:
    structlog_processors += [
        structlog.dev.set_exc_info,
        structlog.dev.ConsoleRenderer(),
    ]


def get_module_logger(name):
    configure_structlog()
    logger = structlog.get_logger(name)
    return logger


LOGGING_CONFIG_BASE = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": ecs_logging.StructlogFormatter(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


def handle_uncought_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger = get_module_logger(__name__)
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def configure_structlog():
    structlog.configure(
        processors=structlog_processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
