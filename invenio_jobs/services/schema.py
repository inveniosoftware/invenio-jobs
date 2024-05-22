# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service schemas."""

import inspect

from invenio_i18n import lazy_gettext as _
from marshmallow import EXCLUDE, Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    max_ = kwargs.get("max", "")
    return validate.Length(
        error=_(
            "Field cannot be blank or longer than {max_} characters.".format(max_=max_)
        ),
        min=1,
        **kwargs,
    )


class TaskParameterSchema(Schema):
    """Schema for a task parameter."""

    name = SanitizedUnicode()

    # TODO: Make custom schema for serializing parameter types
    default = fields.Method("dump_default")
    kind = fields.String()

    def dump_default(self, obj):
        """Dump the default value."""
        if obj.default in (None, inspect.Parameter.empty):
            return None
        elif isinstance(obj.default, (bool, int, float, str)):
            return obj.default
        else:
            return str(obj.default)


class TaskSchema(Schema, FieldPermissionsMixin):
    """Schema for a task."""

    name = SanitizedUnicode()
    description = SanitizedUnicode()
    parameters = fields.Dict(
        keys=SanitizedUnicode(),
        values=fields.Nested(TaskParameterSchema),
    )


class JobSchema(Schema, FieldPermissionsMixin):
    """Base schema for a job."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedUnicode()


class RunSchema(Schema, FieldPermissionsMixin):
    """Base schema for a job."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedUnicode()
