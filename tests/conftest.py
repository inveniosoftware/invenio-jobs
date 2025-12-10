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

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from flask_principal import AnonymousIdentity
from invenio_access.permissions import any_user as any_user_need
from invenio_app.factory import create_api
from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy

from invenio_jobs.api import AttrDict
from invenio_jobs.proxies import current_jobs_service


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    # __import__("ipdb").set_trace()
    return {
        "invenio_jobs.jobs": [
            "mock_module = mock_module.jobs:MockJob",
        ],
        "invenio_celery.tasks": [
            "mock_module = mock_module.tasks",
        ],
    }


@pytest.fixture(scope="module")
def app_config(app_config):
    """Application config override."""

    class MockPermissionPolicy(BasePermissionPolicy):
        can_search = [AnyUser(), SystemProcess()]
        can_create = [AnyUser(), SystemProcess()]
        can_read = [AnyUser()]
        can_update = [AnyUser()]
        can_delete = [AnyUser()]
        can_stop = [AnyUser()]

    app_config["REST_CSRF_ENABLED"] = False

    app_config["JOBS_TASKS_PERMISSION_POLICY"] = MockPermissionPolicy
    app_config["JOBS_PERMISSION_POLICY"] = MockPermissionPolicy
    app_config["JOBS_RUNS_PERMISSION_POLICY"] = MockPermissionPolicy
    app_config["APP_LOGS_PERMISSION_POLICY"] = MockPermissionPolicy
    app_config["THEME_FRONTPAGE"] = False
    app_config["CELERY_TASK_ALWAYS_EAGER"] = True
    app_config["CELERY_TASK_EAGER_PROPAGATES"] = True
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


#
# Users and identities
#
@pytest.fixture()
def anon_identity(user):
    """Anonymous user."""
    identity = AnonymousIdentity()
    identity.id = user.id  # Mock it with the user id
    identity.provides.add(any_user_need)
    return identity


@pytest.fixture()
def user(UserFixture, app, db):
    """User meant to test permissions."""
    u = UserFixture(
        email="user@inveniosoftware.org",
        username="user",
        password="user",
        user_profile={
            "full_name": "User",
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
    )
    u.create(app, db)
    return u


@pytest.fixture()
def jobs(db, anon_identity):
    """Job fixtures."""
    common_data = {
        "task": "update_expired_embargos",
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
    }
    interval_job = current_jobs_service.create(
        anon_identity,
        {
            "title": "Test interval job",
            "schedule": {
                "type": "interval",
                "hours": 4,
            },
            **common_data,
        },
    )
    crontab_job = current_jobs_service.create(
        anon_identity,
        {
            "title": "Test crontab job",
            "schedule": {
                "type": "crontab",
                "minute": "0",
                "hour": "0",
            },
            **common_data,
        },
    )
    simple_job = current_jobs_service.create(
        anon_identity,
        {
            "title": "Test unscheduled job",
            **common_data,
        },
    )
    return SimpleNamespace(
        interval=interval_job,
        crontab=crontab_job,
        simple=simple_job,
    )


@pytest.fixture()
def _make_hit():
    def _make_hit(idx):
        """Create a fake search hit."""
        timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() + idx
        sort_value = [timestamp, f"id-{idx}"]
        hit = AttrDict(
            {
                "@timestamp": datetime.fromtimestamp(
                    timestamp, timezone.utc
                ).isoformat(),
                "level": "ERROR",
                "message": f"log-{idx}",
                "module": "tests",
                "function": "fn",
                "line": idx,
                "context": {
                    "job_id": "job-123",
                    "run_id": "run-456",
                    "identity_id": "user-789",
                },
                "sort": sort_value,
            }
        )
        hit.meta = AttrDict({"sort": sort_value})
        return hit

    return _make_hit


class FakeHits(list):
    """List-like container mimicking an OpenSearch hits collection."""

    def __init__(self, hits, total):
        """Init of FakeHits."""
        super().__init__(hits)
        self.hits = self  # mimic .hits attribute used by the service
        self.total = {"value": total}


class FakeResponse:
    """Response object mimicking OpenSearch DSL responses."""

    def __init__(self, hits, total):
        """Init of FakeResponse."""
        self.hits = FakeHits(hits, total)

    def __iter__(self):
        """Iterate over hits like elasticsearch-dsl responses."""
        return iter(self.hits)


@pytest.fixture()
def FakeSearch():
    """Very small fake Search implementation for unit testing."""

    class FakeSearch:
        """Very small fake Search implementation for unit testing."""

        def __init__(self, hits):
            self._hits = list(hits)
            self._cursor = 0
            self._params = {}
            self.execute_calls = 0

        def _clone(self):
            clone = FakeSearch(self._hits)
            clone._cursor = self._cursor
            clone._params = dict(self._params)
            return clone

        def count(self):
            return len(self._hits)

        def sort(self, *args, **kwargs):
            return self

        def extra(self, **kwargs):
            self._params.update(kwargs)
            return self

        def execute(self):
            self.execute_calls += 1
            size = self._params.get("size", max(len(self._hits) - self._cursor, 0))
            start = self._cursor
            end = min(start + size, len(self._hits))
            if start >= len(self._hits):
                page_hits = []
            else:
                page_hits = self._hits[start:end]
                self._cursor = end
            return FakeResponse(list(page_hits), len(self._hits))

    return FakeSearch
