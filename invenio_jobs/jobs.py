# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
from functools import partial


class RegisteredTask:

    arguments_schema = None
    task = None
    id = None
    title = None
    description = None
    @classmethod
    def factory(cls, job_cls_name, arguments_schema, id_, task, description, title, attrs=None):
        """Create a new instance of a job."""
        if not attrs:
            attrs = {}
        return type(
            job_cls_name,
            (RegisteredTask,),
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
    def build_task_arguments(cls, job_obj, since=None, custom_args=None, **kwargs):
        if custom_args:
            return custom_args
        return {}
