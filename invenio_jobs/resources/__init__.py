# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jobs resources."""

from .config import JobResourceConfig
from .resources import JobResource

__all__ = (
    "JobResource",
    "JobResourceConfig",
)
