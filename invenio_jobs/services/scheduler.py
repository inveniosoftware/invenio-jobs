# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import traceback
from typing import Any

from celery.beat import ScheduleEntry, Scheduler, debug, error, info
from celery.schedules import crontab
from invenio_access.permissions import system_identity
from invenio_app.factory import create_api
from invenio_db import db

from invenio_jobs.models import Job, Run

app = create_api()


class JobEntry(ScheduleEntry):

    #: Job ID
    job_id = None

    def __init__(
        self,
        job_id=None,
        name=None,
        task=None,
        last_run_at=None,
        total_run_count=None,
        schedule=None,
        args=...,
        kwargs=None,
        options=None,
        relative=False,
        app=None,
    ):
        self.job_id = job_id
        super().__init__(
            name,
            task,
            last_run_at,
            total_run_count,
            schedule,
            args,
            kwargs,
            options,
            relative,
            app,
        )

    @classmethod
    def from_job(cls, job):
        return cls(
            job_id=job.id,
            name=job.title,
            schedule=job.parsed_schedule,
            args=job.default_args,
            task=job.task,
            kwargs={},
            options={},
            last_run_at=job.last_run_at,
        )


class RunScheduler(Scheduler):
    Entry = JobEntry
    entries = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the database scheduler."""
        Scheduler.__init__(self, *args, **kwargs)

    @property
    def schedule(self):
        return self.entries

    def setup_schedule(self):
        self.sync()

    def reserve(self, entry):
        new_entry = self.schedule[entry.job_id] = next(entry)
        return new_entry

    def apply_entry(self, entry, producer=None):
        info("Scheduler: Sending due task %s (%s)", entry.name, entry.task)
        try:
            self.create_run(entry)
            result = self.apply_async(entry, producer=producer, advance=False)
        except Exception as exc:  # pylint: disable=broad-except
            error("Message Error: %s\n%s", exc, traceback.format_stack(), exc_info=True)
        else:
            if result and hasattr(result, "id"):
                debug("%s sent. id->%s", entry.task, result.id)
            else:
                debug("%s sent.", entry.task)

    def sync(self):
        with app.app_context():
            for job_id, entry in self.schedule.items():
                job = Job.query.filter_by(id=job_id).one()
                job.last_run_at = (entry.last_run_at,)
            db.session.commit()
            jobs = Job.query.filter(Job.active == True).all()
            for job in jobs:
                self.entries[job.id] = JobEntry.from_job(job)

    def create_run(self, entry):
        with app.app_context():
            run = Run()
            job = Job.query.filter_by(id=entry.job_id).one()
            run.job = job
            # run.started_by = started_by or "system"
            run.args = entry.args
            # run.queue = entry.default_queue # TODO Not working/considered for now
            # run.commit()
            db.session.commit()
