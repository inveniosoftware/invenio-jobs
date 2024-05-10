# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Models."""

import enum

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import Timestamp
from sqlalchemy_utils.types import ChoiceType, JSONType, UUIDType

JSON = (
    db.JSON()
    .with_variant(postgresql.JSONB(none_as_null=True), "postgresql")
    .with_variant(JSONType(), "sqlite")
    .with_variant(JSONType(), "mysql")
)


class Job(db.Model, Timestamp):
    """Job model."""

    id = db.Column(UUIDType, primary_key=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    celery_tasks = db.Column(db.String(255))
    default_queue = db.Column(db.String(64))
    default_args = db.Column(JSON, default=lambda: dict(), nullable=True)
    schedule = db.Column(JSON, default=lambda: dict(), nullable=True)

    # TODO: See if we move this to an API class
    @property
    def last_run(self):
        """Last run of the job."""
        return self.runs.order_by(Run.created.desc()).first()


class RunStatusEnum(enum.Enum):
    """Enumeration of a run's possible states."""

    PENDING = "P"
    RUNNING = "R"
    SUCCESS = "S"
    FAILURE = "F"
    WARNING = "W"
    CANCELLED = "C"


class Run(db.Model, Timestamp):
    """Run model."""

    id = db.Column(UUIDType, primary_key=True)

    job_id = db.Column(UUIDType, db.ForeignKey(Job.id))
    job = db.relationship(Job, backref=db.backref("runs", lazy="dynamic"))

    started_by_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    started_by = db.relationship(User)

    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=False)

    status = db.Column(
        ChoiceType(RunStatusEnum, impl=db.String(1)),
        nullable=False,
        default=RunStatusEnum.PENDING.value,
    )

    message = db.Column(db.Text, nullable=True)

    task_id = db.Column(UUIDType, nullable=True)
    args = db.Column(JSON, default=lambda: dict(), nullable=True)
    queue = db.Column(db.String(64), nullable=True)
