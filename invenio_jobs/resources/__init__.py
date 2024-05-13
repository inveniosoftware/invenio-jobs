# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jobs resources."""

from .config import JobsResourceConfig, RunsResourceConfig, TasksResourceConfig
from .resources import JobsResource, RunsResource, TasksResource

__all__ = (
    "JobsResource",
    "JobsResourceConfig",
    "TasksResource",
    "TasksResourceConfig",
    "RunsResource",
    "RunsResourceConfig",
)
