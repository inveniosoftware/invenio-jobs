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
from sqlalchemy import asc, desc

from ..models import Job, Run, Task
from . import results
from .links import JobLink, RunLink
from .permissions import (
    JobPermissionPolicy,
    RunPermissionPolicy,
    TasksPermissionPolicy,
)
from .schema import JobSchema, RunSchema, TaskSchema


class TasksSearchOptions(SearchOptionsBase):
    """Tasks search options."""

    sort_default = "name"
    sort_direction_default = "asc"
    sort_direction_options = {
        "asc": dict(
            title=_("Ascending"),
            fn=partial(sorted, key=lambda t: t.title),
        ),
        "desc": dict(
            title=_("Descending"),
            fn=partial(sorted, key=lambda t: t.title, reverse=True),
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
    argument_item_cls = results.Item

    permission_policy_cls = FromConfig(
        "JOBS_TASKS_PERMISSION_POLICY",
        default=TasksPermissionPolicy,
    )

    result_list_cls = results.List

    links_item = None
    links_search = pagination_links("{+api}/tasks{?args*}")


class JobSearchOptions(SearchOptionsBase):
    """Job search options."""

    sort_default = "title"
    sort_direction_default = "asc"
    sort_direction_options = {
        "asc": dict(title=_("Ascending"), fn=asc),
        "desc": dict(title=_("Descending"), fn=desc),
    }
    sort_options = {"title": dict(title=_("Title"), fields=["title"])}

    pagination_options = {"default_results_per_page": 25}


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

    result_item_cls = results.JobItem
    result_list_cls = results.JobList

    links_item = {
        "self": JobLink("{+api}/jobs/{id}"),
        "runs": JobLink("{+api}/jobs/{id}/runs"),
        "self_admin_html": JobLink("{+ui}/administration/jobs/{id}"),
    }

    links_search = pagination_links("{+api}/jobs{?args*}")


class RunSearchOptions(SearchOptionsBase):
    """Run search options."""

    sort_default = "created"
    sort_direction_default = "desc"
    sort_direction_options = {
        "asc": dict(title=_("Ascending"), fn=asc),
        "desc": dict(title=_("Descending"), fn=desc),
    }
    sort_options = {"created": dict(title=_("Created"), fields=["created"])}

    sort_default_no_query = "bestmatch"

    pagination_options = {"default_results_per_page": 25}


class RunsServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Service factory configuration."""

    service_id = "runs"

    record_cls = Run
    search = RunSearchOptions
    schema = RunSchema

    permission_policy_cls = FromConfig(
        "JOBS_RUNS_PERMISSION_POLICY",
        default=RunPermissionPolicy,
    )

    result_item_cls = results.Item
    result_list_cls = results.List

    links_item = {
        "self": RunLink("{+api}/jobs/{job_id}/runs/{id}"),
        "stop": RunLink("{+api}/jobs/{job_id}/runs/{id}/actions/stop"),
        "logs": RunLink("{+api}/jobs/{job_id}/runs/{id}/logs"),
    }

    links_search = pagination_links("{+api}/jobs/{job_id}{?args*}")


class AppLogSearchOptions(SearchOptionsBase):
    """App log search options."""

    sort_default = "timestamp"
    sort_direction_default = "desc"
    sort_direction_options = {
        "asc": dict(title=_("Ascending"), fn=asc),
        "desc": dict(title=_("Descending"), fn=desc),
    }
    sort_options = {
        "timestamp": dict(title=_("Timestamp"), fields=["@timestamp"]),
    }

    pagination_options = {"default_results_per_page": 25}
