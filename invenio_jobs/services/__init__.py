# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services."""

from .config import JobServiceConfig
from .schema import JobSchema
from .services import JobService

__all__ = (
    "JobSchema",
    "JobService",
    "JobServiceConfig",
)
