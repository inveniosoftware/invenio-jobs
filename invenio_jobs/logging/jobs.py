# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio jobs logging module.

This extension provides logging configuration specifically for job execution logs.
"""

from __future__ import absolute_import, print_function

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from functools import wraps

from flask import current_app
from invenio_logging.ext import InvenioLoggingBase
from invenio_search import current_search_client

from invenio_jobs.services import JobLogEntrySchema

from .. import config

# Define a global context variable to enrich logs
job_context = ContextVar("job_context", default={})


class ContextAwareOSHandler(logging.Handler):
    """Custom logging handler that enriches logs with global context and indexes them in OS."""

    def emit(self, record):
        """Emit log record after enriching it with global context."""
        if job_context.get():
            enriched_log = self.enrich_log(record)
            self.index_in_os(enriched_log)

    def enrich_log(self, record):
        """Enrich log record with contextvars' global context."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "context": job_context.get(),
        }
        serialzed_data = JobLogEntrySchema().load(log_data)
        return serialzed_data

    def index_in_os(self, log_data):
        """Send log data to OpenSearch."""
        index_prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
        full_index_name = f"{index_prefix}job-logs"
        current_search_client.index(index=full_index_name, body=log_data)


@contextmanager
def set_job_context(data):
    """Context manager for safely setting and cleaning up contextvars."""
    token = job_context.set(data)
    try:
        yield job_context  # Yield the contextvar for modification
    finally:
        job_context.reset(token)  # Ensures cleanup


def with_job_context(base_context={}):
    """Decorator to apply and update context dynamically inside a function."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with set_job_context(base_context) as context:

                def update_context(new_data):
                    """Update context dynamically within the function."""
                    context.set({**context.get(), **new_data})

                return func(
                    *args, update_context=update_context, **kwargs
                )  # Inject update_context

        return wrapper

    return decorator


class InvenioLoggingJobs(InvenioLoggingBase):
    """Logging extension for jobs."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        if not app.config["LOGGING_JOBS"]:
            return
        # For the jobs handler to log at the configured level
        # we need to check the configured level and set it if it is lower than the app logger level
        # otherwise the handler will not log anything
        configured_level_str = app.config["LOGGING_JOBS_LEVEL"]
        if configured_level_str is not None:
            configured_level = logging._nameToLevel.get(configured_level_str.upper())
            if (
                isinstance(configured_level, int)
                and app.logger.level > configured_level
            ):
                app.logger.setLevel(configured_level)
        self.install_handler(app)

        app.extensions["invenio-logging-jobs"] = self

    def init_config(self, app):
        """Initialize config."""
        for k in dir(config):
            if k.startswith("LOGGING_JOBS"):
                app.config.setdefault(k, getattr(config, k))

    def install_handler(self, app):
        """Install logging handler for jobs."""
        # Set logging level
        if app.config["LOGGING_JOBS_LEVEL"] is not None:
            for h in app.logger.handlers:
                h.setLevel(app.config["LOGGING_JOBS_LEVEL"])

        # Add OpenSearch logging handler if not already added
        if not any(isinstance(h, ContextAwareOSHandler) for h in app.logger.handlers):
            os_handler = ContextAwareOSHandler()
            os_handler.setLevel(app.config["LOGGING_JOBS_LEVEL"])
            app.logger.addHandler(os_handler)
