# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI schemas."""

from invenio_i18n import lazy_gettext as _
from marshmallow import Schema, fields
from marshmallow_oneofschema import OneOfSchema
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin
from marshmallow_utils.validators import LazyOneOf


class IntervalScheduleUISchema(Schema):
    """Schema for an interval schedule based on ``datetime.timedelta``."""

    weeks = fields.Integer(metadata={"title": "Weeks"})
    days = fields.Integer(metadata={"title": "Days"})
    hours = fields.Integer(metadata={"title": "Hours"})
    minutes = fields.Integer(metadata={"title": "Minutes"})
    seconds = fields.Integer(metadata={"title": "Seconds"})
    milliseconds = fields.Integer(metadata={"title": "Milliseconds"})
    microseconds = fields.Integer(metadata={"title": "Microseconds"})


class CrontabScheduleUISchema(Schema):
    """Schema for a crontab schedule."""

    month_of_year = fields.String(load_default="*", metadata={"title": "Month of Year"})
    day_of_month = fields.String(load_default="*", metadata={"title": "Day of Month"})
    day_of_week = fields.String(load_default="*", metadata={"title": "Day of Week"})
    hour = fields.String(load_default="*", metadata={"title": "Hour"})
    minute = fields.String(load_default="*", metadata={"title": "Minute"})


class ScheduleUISchema(OneOfSchema):
    """Schema for a schedule."""

    interval = fields.Nested(IntervalScheduleUISchema, dump_only=True)
    crontab = fields.Nested(CrontabScheduleUISchema, dump_only=True)
