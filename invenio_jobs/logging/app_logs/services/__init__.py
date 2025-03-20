# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Loggigng module for app."""

from .service import AppLogService
from .config import AppLogServiceConfig

__all__ = (
    "AppLogService",
    "AppLogServiceConfig",
)
