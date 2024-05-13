# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resources config."""

import marshmallow as ma
from flask_resources import HTTPJSONException, ResourceConfig, create_error_handler
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.services.base.config import ConfiguratorMixin


class TasksResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Celery tasks resource config."""

    # Blueprint configuration
    blueprint_name = "tasks"
    url_prefix = "/tasks"
    routes = {"list": ""}


class JobsSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Jobs search request parameters."""

    active = ma.fields.Boolean()


class JobsResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Jobs resource config."""

    # Blueprint configuration
    blueprint_name = "jobs"
    url_prefix = "/jobs"
    routes = {
        "list": "",
        "item": "/<job_id>",
    }

    # Request parsing
    request_read_args = {}
    request_view_args = {"job_id": ma.fields.Int()}
    request_search_args = JobsSearchRequestArgsSchema

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        # TODO: Add custom error handlers here
    }


class RunsResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Runs resource config."""

    # Blueprint configuration
    blueprint_name = "job_runs"
    url_prefix = ""

    routes = {
        "runs": "/jobs/<job_id>/runs",
        "run_item": "/jobs/<job_id>/runs/<run_id>",
        "logs": "/jobs/<job_id>/runs/<run_id>/logs",
    }

    # Request parsing
    request_view_args = {
        "job_id": ma.fields.Int(),
        "run_id": ma.fields.Int(),
    }

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        # TODO: Add custom error handlers here
    }
