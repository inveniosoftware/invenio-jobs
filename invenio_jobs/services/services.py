# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service definitions."""

from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.base.utils import map_search_params
from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import unit_of_work

from ..models import Task


class TasksService(RecordService):
    """Tasks service."""

    def search(self, identity, params):
        """Search for tasks."""
        self.require_permission(identity, "search")

        # TODO: Use an API class
        tasks = Task.all()

        search_params = map_search_params(self.config.search, params)
        query_param = search_params["q"]
        if query_param:
            tasks = [
                task
                for task in tasks
                if (
                    query_param in task.name.lower()
                    or query_param in task.description.lower()
                )
            ]
        sort_direction = search_params["sort_direction"]
        tasks = sort_direction(tasks)

        return self.result_list(
            service=self,
            identity=identity,
            results=tasks,
            params=search_params,
            links_tpl=LinksTemplate(self.config.links_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
        )


class JobsService(RecordService):
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


class RunsService(RecordService):
    """Runs service."""

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
