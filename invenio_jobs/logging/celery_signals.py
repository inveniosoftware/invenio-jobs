# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery signals."""

from celery import signals

from .jobs import job_context


# Capture context when a task is sent
@signals.before_task_publish.connect
def capture_context(sender=None, headers=None, body=None, **kwargs):
    """Capture the current context and attach it to Celery task headers."""
    if "context" not in headers:  # Ensure context is only added if missing
        headers["context"] = job_context.get()


# Restore context when a task starts executing
@signals.task_prerun.connect
def restore_context(task=None, **kwargs):
    """Restore context before task execution."""
    # Synchronous celery tasks will already be aware of the context although it's missing
    # in the task headers, as the before_task_publish signal is not triggered
    if not job_context.get():
        task_context = getattr(task.request, "context", {})
        job_context.set(task_context)


# Clean up context after task execution
@signals.task_postrun.connect
def cleanup_context(task=None, **kwargs):
    """Clean up context after task execution."""
    job_context.set({})
