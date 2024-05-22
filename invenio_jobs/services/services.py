# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service definitions."""

import sqlalchemy as sa
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.base.utils import map_search_params
from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import (
    ModelCommitOp,
    ModelDeleteOp,
    unit_of_work,
)

from ..models import Job
from ..proxies import current_jobs
from .errors import JobNotFoundError


class TasksService(RecordService):
    """Tasks service."""

    def search(self, identity, params):
        """Search for tasks."""
        self.require_permission(identity, "search")

        tasks = current_jobs.tasks.values()

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

    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create a job."""
        self.require_permission(identity, "create")

        # TODO: See if we need extra validation (e.g. tasks, args, etc.)
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True,
        )

        job = Job(**valid_data)
        uow.register(ModelCommitOp(job))
        return self.result_item(self, identity, job, links_tpl=self.links_item_tpl)

    def search(self, identity, params):
        """Search for jobs."""
        self.require_permission(identity, "search")

        search_params = map_search_params(self.config.search, params)
        query_param = search_params["q"]
        filters = []
        if query_param:
            filters.extend(
                [
                    Job.title.ilike(f"%{query_param}%"),
                    Job.description.ilike(f"%{query_param}%"),
                ]
            )

        jobs = (
            Job.query.filter(sa.or_(*filters))
            .order_by(
                search_params["sort_direction"](
                    sa.text(",".join(search_params["sort"]))
                )
            )
            .paginate(
                page=search_params["page"],
                per_page=search_params["size"],
                error_out=False,
            )
        )

        return self.result_list(
            self,
            identity,
            jobs,
            params=search_params,
            links_tpl=LinksTemplate(self.config.links_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
        )

    def read(self, identity, id_):
        """Retrieve a job."""
        self.require_permission(identity, "read")
        job = self._get_job(id_)

        return self.result_item(self, identity, job, links_tpl=self.links_item_tpl)

    @unit_of_work()
    def update(self, identity, id_, data, uow=None):
        """Update a job."""
        self.require_permission(identity, "update")

        job = self._get_job(id_)

        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity, "job": job},
            raise_errors=True,
        )

        for key, value in valid_data.items():
            setattr(job, key, value)
        uow.register(ModelCommitOp(job))
        return self.result_item(self, identity, job, links_tpl=self.links_item_tpl)

    @unit_of_work()
    def delete(self, identity, id_, uow=None):
        """Delete a job."""
        self.require_permission(identity, "delete")
        job = self._get_job(id_)

        # TODO: Check if we can delete the job (e.g. if there are still active Runs)
        uow.register(ModelDeleteOp(job))

        return True

    @classmethod
    def _get_job(cls, id):
        """Get a job by id."""
        job = Job.query.get(id)
        if job is None:
            raise JobNotFoundError(id)
        return job


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
