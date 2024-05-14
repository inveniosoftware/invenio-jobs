# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services config."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.base import ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_records_resources.services.records.config import (
    SearchOptions as SearchOptionsBase,
)
from invenio_records_resources.services.records.links import pagination_links
from invenio_records_resources.services.records.results import RecordItem, RecordList

from ..models import Job, Run
from .links import JobLink
from .permissions import JobPermissionPolicy, RunPermissionPolicy, TasksPermissionPolicy
from .schema import JobSchema


class TasksServiceConfig(ServiceConfig, ConfiguratorMixin):
    """TaskService factory configuration."""

    # Common configuration
    service_id = "tasks"
    permission_policy_cls = TasksPermissionPolicy

    result_list_cls = RecordList

    links_item = {
        "self": JobLink("{+api}/tasks"),
    }


class JobSearchOptions(SearchOptionsBase):
    """Job search options."""

    # TODO: See what we need to override


class JobsServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Service factory configuration."""

    # Common configuration
    service_id = "jobs"
    permission_policy_cls = JobPermissionPolicy

    # TODO: See if we need to define custom Job result item and list classes
    result_item_cls = RecordItem
    result_list_cls = RecordList

    # Record specific configuration
    record_cls = Job

    # TODO: See if these are needed since we don't index jobs
    # indexer_cls = None
    # indexer_queue_name = None
    # index_dumper = None

    # Search configuration
    search = JobSearchOptions

    # Service schema
    schema = JobSchema

    links_item = {
        "self": JobLink("{+api}/jobs/{id}"),
        "runs": JobLink("{+api}/jobs/{id}/runs"),
    }

    links_search = pagination_links("{+api}/jobs{?args*}")


class RunsServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Service factory configuration."""

    # Common configuration
    service_id = "runs"
    permission_policy_cls = RunPermissionPolicy

    # TODO: See if we need to define custom Job result item and list classes
    result_item_cls = RecordItem
    result_list_cls = RecordList

    # Record specific configuration
    record_cls = Run

    # TODO: See if these are needed since we don't index jobs
    # indexer_cls = None
    # indexer_queue_name = None
    # index_dumper = None

    # Search configuration
    search = JobSearchOptions

    # Service schema
    schema = JobSchema

    links_item = {
        "self": JobLink("{+api}/jobs/{job_id}/runs/{run_id}"),
        "stop": JobLink("{+api}/jobs/{job_id}/runs/{run_id}/actions/stop"),
        "logs": JobLink("{+api}/jobs/{job_id}/runs/{run_id}/logs"),
    }
