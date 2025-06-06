# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jobs module."""

from abc import ABC
from datetime import timezone

from invenio_i18n import gettext as _
from marshmallow import Schema, fields
from marshmallow_utils.fields import TZDateTime


class PredefinedArgsSchema(Schema):
    """Base schema of predefined task input arguments.

    Attributes:
        job_arg_schema (fields.String): A system hidden field that holds the name of
            this schema class. Required whenever at least one argument is needed.
        since (TZDateTime): A date-time field with UTC timezone and ISO format.
            It includes a description indicating that the field can be left
            empty to continue from the last successful run.
    """

    """Schema of task input arguments."""

    job_arg_schema = fields.String(
        metadata={"type": "hidden"},
        dump_default="PredefinedArgsSchema",
        load_default="PredefinedArgsSchema",
    )

    since = TZDateTime(
        timezone=timezone.utc,
        format="iso",
        metadata={
            "description": _(
                "YYYY-MM-DD HH:mm format. "
                "Leave empty to continue since last successful run."
            )
        },
    )


class JobType(ABC):
    """Base class to define a job."""

    id = None
    title = None
    description = None

    task = None

    arguments_schema = PredefinedArgsSchema

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
                **attrs,
            ),
        )

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Override to define extra arguments to be injected on task execution.

        :param job_obj (Job): the Job object.
        :param since (datetime): last time the job was executed, or None if never
            executed.
        :return: a dict of arguments to be injected on task execution.
        """
        return {}

    @classmethod
    def _build_task_arguments(cls, job_obj, since=None, custom_args=None, **kwargs):
        """Build dict of arguments injected on task execution.

        :param job_obj (Job): the Job object.
        :param since (datetime): last time the job was executed.
        :param custom_args (dict): when provided, takes precedence over any other
            provided argument.
        :return: a dict of arguments to be injected on task execution.
        """
        if custom_args:
            return custom_args

        if since is None and job_obj.last_runs["success"]:
            since = job_obj.last_runs["success"].started_at
        return {**cls.build_task_arguments(job_obj, since=since, **kwargs)}
