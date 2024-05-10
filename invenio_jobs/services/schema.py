# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service schemas."""

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


class JobSchema(Schema, FieldPermissionsMixin):
    """Base schema for a job."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedUnicode()
