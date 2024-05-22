# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_api as _create_app
from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies import BasePermissionPolicy


@pytest.fixture(scope="module")
def app_config(app_config):
    """Application config override."""

    class MockPermissionPolicy(BasePermissionPolicy):
        can_search = [AnyUser()]
        can_create = [AnyUser()]
        can_read = [AnyUser()]
        can_update = [AnyUser()]
        can_delete = [AnyUser()]

    app_config["JOBS_TASKS_PERMISSION_POLICY"] = MockPermissionPolicy
    app_config["JOBS_PERMISSION_POLICY"] = MockPermissionPolicy
    app_config["JOBS_RUNS_PERMISSION_POLICY"] = MockPermissionPolicy
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return _create_app


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_celery.tasks": [
            "mock_module = mock_module.tasks",
        ],
    }
