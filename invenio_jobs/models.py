# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Models."""

import enum
import uuid
from copy import deepcopy
from datetime import timedelta
from inspect import signature

import sqlalchemy as sa
from celery import current_app as current_celery_app
from celery.schedules import crontab
from invenio_accounts.models import User
from invenio_db import db
from invenio_users_resources.records import UserAggregate
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import Timestamp
from sqlalchemy_utils.types import ChoiceType, JSONType, UUIDType
from werkzeug.utils import cached_property

from .utils import eval_tpl_str, walk_values

JSON = (
    db.JSON()
    .with_variant(postgresql.JSONB(none_as_null=True), "postgresql")
    .with_variant(JSONType(), "sqlite")
    .with_variant(JSONType(), "mysql")
)


def _dump_dict(model):
    """Dump a model to a dictionary."""
    return {c.key: getattr(model, c.key) for c in sa.inspect(model).mapper.column_attrs}


class Job(db.Model, Timestamp):
    """Job model."""

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    active = db.Column(db.Boolean, default=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    task = db.Column(db.String(255))
    default_queue = db.Column(db.String(64))
    default_args = db.Column(JSON, default=lambda: dict(), nullable=True)
    schedule = db.Column(JSON, nullable=True)

    @property
    def last_run(self):
        """Last run of the job."""
        return self.runs.order_by(Run.created.desc()).first()

    @property
    def parsed_schedule(self):
        """Return schedule parsed as crontab or timedelta."""
        if not self.schedule:
            return None

        schedule = deepcopy(self.schedule)
        stype = schedule.pop("type")
        if stype == "crontab":
            return crontab(**schedule)
        elif stype == "interval":
            return timedelta(**schedule)

    def dump(self):
        """Dump the job as a dictionary."""
        return _dump_dict(self)


class RunStatusEnum(enum.Enum):
    """Enumeration of a run's possible states."""

    QUEUED = "Q"
    RUNNING = "R"
    SUCCESS = "S"
    FAILED = "F"
    WARNING = "W"
    CANCELLING = "C"
    CANCELLED = "X"


class Run(db.Model, Timestamp):
    """Run model."""

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    job_id = db.Column(UUIDType, db.ForeignKey(Job.id))
    job = db.relationship(Job, backref=db.backref("runs", lazy="dynamic"))

    started_by_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    _started_by = db.relationship(User)

    @property
    def started_by(self):
        """Return UserAggregate of the user that started the run."""
        if self._started_by:
            return UserAggregate.from_model(self._started_by)

    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    task_id = db.Column(UUIDType, nullable=True)
    status = db.Column(
        ChoiceType(RunStatusEnum, impl=db.String(1)),
        nullable=False,
        default=RunStatusEnum.QUEUED.value,
    )

    message = db.Column(db.Text, nullable=True)

    title = db.Column(db.Text, nullable=True)
    args = db.Column(JSON, default=lambda: dict(), nullable=True)
    queue = db.Column(db.String(64), nullable=False)

    @classmethod
    def create(cls, job, **kwargs):
        """Create a new run."""
        if "args" not in kwargs:
            kwargs["args"] = cls.generate_args(job)
        if "queue" not in kwargs:
            kwargs["queue"] = job.default_queue

        return cls(job=job, **kwargs)

    @classmethod
    def generate_args(cls, job):
        """Generate new run args.

        We allow a templating mechanism to generate the args for the run. It's important
        that the Jinja template context only includes "safe" values, i.e. no DB model
        classes or Python objects or functions. Otherwise we risk that users could
        execute arbitrary code, or perform harfmul DB operations (e.g. delete rows).
        """
        args = deepcopy(job.default_args)
        ctx = {"job": job.dump()}
        # Add last runs
        last_runs = {}
        for status in RunStatusEnum:
            run = job.runs.filter_by(status=status).order_by(cls.created.desc()).first()
            last_runs[status.name.lower()] = run.dump() if run else None
        ctx["last_runs"] = last_runs
        ctx["last_run"] = job.last_run.dump() if job.last_run else None
        walk_values(args, lambda val: eval_tpl_str(val, ctx))
        return args

    def dump(self):
        """Dump the run as a dictionary."""
        return _dump_dict(self)


class Task:
    """Celery Task model."""

    _all_tasks = None

    def __init__(self, obj):
        """Initialize model."""
        self._obj = obj

    def __getattr__(self, name):
        """Proxy attribute access to the task object."""
        # TODO: See if we want to limit what attributes are exposed
        return getattr(self._obj, name)

    @cached_property
    def description(self):
        """Return description."""
        if not self._obj.__doc__:
            return ""
        return self._obj.__doc__.split("\n")[0]

    @cached_property
    def parameters(self):
        """Return the task's parameters."""
        # TODO: Make this result more user friendly or enhance with type information
        return signature(self._obj).parameters

    @classmethod
    def all(cls):
        """Return all tasks."""
        if getattr(cls, "_all_tasks", None) is None:
            # Cache results
            cls._all_tasks = {
                k: cls(task)
                for k, task in current_celery_app.tasks.items()
                # Filter outer Celery internal tasks
                if not k.startswith("celery.")
            }
        return cls._all_tasks
