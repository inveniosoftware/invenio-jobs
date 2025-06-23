# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Deprecaed func tests."""

import pytest

from invenio_jobs.errors import TaskExecutionError


def test_task_execution_error_deprecated(recwarn):
    with pytest.warns(DeprecationWarning, match="TaskExecutionError is deprecated"):
        TaskExecutionError("Deprecated error")
