# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Mock module tasks."""

from celery import shared_task


@shared_task
def mock_task(arg1, arg2, kwarg1=None, kwarg2=False, kwarg3="always"):
    """Mock task description."""
    pass
