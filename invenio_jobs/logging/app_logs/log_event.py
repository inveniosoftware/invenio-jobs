# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Structured log event model."""

from invenio_logging.engine.log_event import BaseLogEvent

class LogEvent(BaseLogEvent):
    """Class to represent a structured log event."""

    def __init__(
        self,
        log_type="app",
        status="INFO",
        event={},
        resource={},
        user={},
        extra={},
        timestamp=None,
        message=None,
    ):
        """
        Create a LogEvent instance.

        :param log_type: Type of log event.
        :param event: Dict with `action` (required) and optional `description`.
        :param resource: Dict with `type`, `id`, and optional `metadata`.
        :param user: Dict with `id`, `email`, and optional `roles` (default: empty).
        :param extra: Additional metadata dictionary (default: empty).
        :param timestamp: Optional timestamp (defaults to now).
        :param message: Optional human-readable message.
        """
        super().__init__(log_type, timestamp, event, message)
        self.resource = resource
        self.user = user
        self.extra = extra
        self.status = status

    def to_dict(self):
        """Convert the log event to a dictionary matching the schema."""
        return {
            "timestamp": self.timestamp,
            "event": self.event,
            "message": self.message,
            "user": self.user,
            "resource": self.resource,
            "extra": self.extra,
            "status": self.status,
        }
