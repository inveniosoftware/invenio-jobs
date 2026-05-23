# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-FileCopyrightText: 2024 University of Münster.
# SPDX-License-Identifier: MIT

"""InvenioRDM module for jobs management."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_jobs",
    __name__,
    template_folder="templates",
)


def create_jobs_bp(app):
    """Create jobs blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.jobs_resource.as_blueprint()


def create_tasks_bp(app):
    """Create tasks blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.tasks_resource.as_blueprint()


def create_runs_bp(app):
    """Create runs blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.runs_resource.as_blueprint()


def create_job_logs_bp(app):
    """Create job logs blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.job_log_resource.as_blueprint()
