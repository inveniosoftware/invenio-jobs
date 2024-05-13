# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jobs resources."""

from .config import JobResourceConfig, TasksResourceConfig
from .resources import JobResource, TasksResource

__all__ = (
    "JobResource",
    "JobResourceConfig",
    "TasksResource",
    "TasksResourceConfig",
)
