# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services config."""

from functools import partial

from invenio_i18n import gettext as _
from invenio_records_resources.services.base import ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from invenio_records_resources.services.records.config import (
    SearchOptions as SearchOptionsBase,
)
from invenio_records_resources.services.records.links import pagination_links

from ..models import Job, Run, Task
from . import results
from .links import JobLink
from .permissions import JobPermissionPolicy, RunPermissionPolicy, TasksPermissionPolicy
from .schema import JobSchema, TaskSchema


class TasksSearchOptions(SearchOptionsBase):
    """Tasks search options."""

    sort_default = "name"
    sort_direction_default = "asc"
    sort_direction_options = {
        "asc": dict(
            title=_("Ascending"),
            fn=partial(sorted, key=lambda t: t.name),
        ),
        "desc": dict(
            title=_("Descending"),
            fn=partial(sorted, key=lambda t: t.name, reverse=True),
        ),
    }
    sort_options = {"name": dict(title=_("Name"), fields=["name"])}

    pagination_options = {"default_results_per_page": 25}


class TasksServiceConfig(ServiceConfig, ConfiguratorMixin):
    """TaskService factory configuration."""

    service_id = "tasks"

    record_cls = Task
    search = TasksSearchOptions
    schema = TaskSchema

    permission_policy_cls = FromConfig(
        "JOBS_TASKS_PERMISSION_POLICY",
        default=TasksPermissionPolicy,
    )

    result_list_cls = results.List

    links_item = None
    links_search = pagination_links("{+api}/tasks{?args*}")


class JobSearchOptions(SearchOptionsBase):
    """Job search options."""

    # TODO: See what we need to override


class JobsServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Service factory configuration."""

    service_id = "jobs"

    record_cls = Job
    search = JobSearchOptions
    schema = JobSchema

    permission_policy_cls = FromConfig(
        "JOBS_PERMISSION_POLICY",
        default=JobPermissionPolicy,
    )

    result_item_cls = results.Item
    result_list_cls = results.List

    links_item = {
        "self": JobLink("{+api}/jobs/{id}"),
        "runs": JobLink("{+api}/jobs/{id}/runs"),
    }

    links_search = pagination_links("{+api}/jobs{?args*}")


class RunSearchOptions(SearchOptionsBase):
    """Run search options."""

    # TODO: See what we need to override


class RunsServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Service factory configuration."""

    service_id = "runs"

    record_cls = Run
    search = RunSearchOptions
    schema = JobSchema

    permission_policy_cls = FromConfig(
        "JOBS_RUNS_PERMISSION_POLICY",
        default=RunPermissionPolicy,
    )

    result_item_cls = results.Item
    result_list_cls = results.List

    links_item = {
        "self": JobLink("{+api}/jobs/{job_id}/runs/{run_id}"),
        "stop": JobLink("{+api}/jobs/{job_id}/runs/{run_id}/actions/stop"),
        "logs": JobLink("{+api}/jobs/{job_id}/runs/{run_id}/logs"),
    }

    links_search = pagination_links("{+api}/jobs/{job_id}{?args*}")
