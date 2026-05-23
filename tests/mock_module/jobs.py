# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Mock module jobs."""

from invenio_jobs.jobs import JobType

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
