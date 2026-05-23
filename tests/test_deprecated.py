# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Deprecaed func tests."""

import pytest

from invenio_jobs.errors import TaskExecutionError


def test_task_execution_error_deprecated(recwarn):
    with pytest.warns(DeprecationWarning, match="TaskExecutionError is deprecated"):
        TaskExecutionError("Deprecated error")
