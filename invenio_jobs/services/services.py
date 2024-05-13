# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service definitions."""

from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import unit_of_work


class TasksService(RecordService):
    """Tasks service."""

    def search(self, identity, **kwargs):
        """Search for jobs."""
        raise NotImplementedError()


class JobService(RecordService):
    """Jobs service."""

    def search(self, identity, **kwargs):
        """Search for jobs."""
        raise NotImplementedError()

    def read(self, identity, id_):
        """Retrieve a job."""
        raise NotImplementedError()

    @unit_of_work()
    def update(self, identity, id_, data, uow=None):
        """Update a job."""
        raise NotImplementedError()

    @unit_of_work()
    def delete(self, identity, id_, uow=None):
        """Delete a job."""
        raise NotImplementedError()
