# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Mock module jobs."""

from marshmallow import fields

from invenio_jobs.jobs import JobType, PredefinedArgsSchema

from .tasks import mock_task


class MockJob(JobType):
    """Mock job."""

    description = "Updates expired embargos"
    id = "update_expired_embargos"
    title = "Update expired embargos"
    task = mock_task

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Mock job using only the since argument."""
        return {"since": since}


class CustomArgsSchema(PredefinedArgsSchema):
    """Mock custom arguments schema."""

    dry_run = fields.Boolean(
        required=False,
        load_default=False,
        metadata={"description": "If true, no changes will be persisted."},
    )


class MockCustomArgsJob(JobType):
    """Mock job with custom arguments schema."""

    description = "Custom job with extra args"
    id = "custom_embargo_job"
    title = "Custom embargo job"
    task = mock_task
    arguments_schema = CustomArgsSchema

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, dry_run=False, **kwargs):
        """Mock job forwarding since and dry_run."""
        return {"since": since, "dry_run": dry_run}
