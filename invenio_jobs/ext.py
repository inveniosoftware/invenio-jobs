# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jobs extension."""

from invenio_i18n import gettext as _

from . import config
from .resources import (
    JobsResource,
    JobsResourceConfig,
    RunsResource,
    RunsResourceConfig,
    TasksResource,
    TasksResourceConfig,
)
from .services import (
    JobsService,
    JobsServiceConfig,
    RunsService,
    RunsServiceConfig,
    TasksService,
    TasksServiceConfig,
)


class InvenioJobs:
    """Invenio-Jobs extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resource(app)
        app.extensions["invenio-jobs"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("JOBS_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize services."""
        self.service = JobsService(JobsServiceConfig.build(app))
        self.runs_service = RunsService(RunsServiceConfig.build(app))
        self.tasks_service = TasksService(TasksServiceConfig.build(app))

    def init_resource(self, app):
        """Initialize resources."""
        self.jobs_resource = JobsResource(JobsResourceConfig.build(app), self.service)
        self.runs_resource = RunsResource(RunsResourceConfig.build(app), self.runs_service)
        self.tasks_resource = TasksResource(
            TasksResourceConfig.build(app), self.tasks_service
        )


def finalize_app(app):
    """Finalize app."""
    rr_ext = app.extensions["invenio-records-resources"]
    ext = app.extensions["invenio-jobs"]

    # services
    rr_ext.registry.register(ext.service, service_id="jobs")
    rr_ext.registry.register(ext.runs_service, service_id="runs")
    rr_ext.registry.register(ext.tasks_service, service_id="tasks")
