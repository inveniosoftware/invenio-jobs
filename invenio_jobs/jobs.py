# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jobs module."""

from abc import ABC

from marshmallow import fields


class JobType(ABC):
    """Base class to define a job."""

    id = None
    title = None
    description = None

    task = None

    arguments_schema = {
        "since": fields.DateTime(required=False),
    }

    @classmethod
    def create(
        cls, job_cls_name, arguments_schema, id_, task, description, title, attrs=None
    ):
        """Create a new instance of a job."""
        if not attrs:
            attrs = {}
        return type(
            job_cls_name,
            (JobType,),
            dict(
                id=id_,
                arguments_schema=arguments_schema,
                task=task,
                description=description,
                title=title,
                **attrs
            ),
        )

    @classmethod
    def get_task_args(cls, job_obj, **kwargs):
        """Override to define extra arguments to be injected on task execution.

        :param job_obj (Job): the Job object.
        :return: a dict of arguments to be injected on task execution.
        """
        return {}

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, custom_args=None, **kwargs):
        """Build dict of arguments injected on task execution.

        :param job_obj (Job): the Job object.
        :param since (datetime): last time the job was executed.
        :param custom_args (dict): when provided, takes precedence over any other
            provided argument.
        :return: a dict of arguments to be injected on task execution.
        """
        if custom_args:
            return custom_args

        # `since` is a predefined argument
        if since is None and job_obj.last_runs["success"]:
            since = job_obj.last_runs["success"].started_at
        return {"since": since, **cls.get_task_args(job_obj, **kwargs)}
