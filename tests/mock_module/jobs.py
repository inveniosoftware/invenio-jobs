# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
