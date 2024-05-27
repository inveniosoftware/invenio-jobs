# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import traceback
from typing import Any

from celery.beat import ScheduleEntry, Scheduler, debug, error, info
from invenio_db import db

from invenio_jobs.models import Job, Run


class JobEntry(ScheduleEntry):

    #: Job ID
    job_id = None

    # TODO Remove args that aren't needed
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
            last_run_at=job.last_run.created,  # TODO Could be a separate property in model
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
        # TODO Check whether we need the celery backend task?
        self.sync()

    def reserve(self, entry):
        new_entry = self.schedule[entry.job_id] = next(entry)
        return new_entry

    def apply_entry(self, entry, producer=None):
        with self.app.flask_app.app_context():
            info("Scheduler: Sending due task %s (%s)", entry.name, entry.task)
            try:
                # TODO Only create and send task if there is no "stale" run (status running, starttime > hour, Run pending for > 1 hr)
                run = self.create_run(entry)
                result = self.apply_async(entry, producer=producer, advance=False)
                run.task_id = result.id
                db.session.commit()
            except Exception as exc:
                error(
                    "Message Error: %s\n%s",
                    exc,
                    traceback.format_stack(),
                    exc_info=True,
                )
            else:
                if result and hasattr(result, "id"):
                    debug("%s sent. id->%s", entry.task, result.id)
                else:
                    debug("%s sent.", entry.task)

    def sync(self):
        # TODO Should we also have a cleaup task for runs? "stale" run (status running, starttime > hour, Run pending for > 1 hr)
        with self.app.flask_app.app_context():
            for job_id, entry in self.schedule.items():
                # TODO Add filter that schedule is not None
                job = Job.query.filter_by(id=job_id).one()
                job.last_run_at = (entry.last_run_at,)
            db.session.commit()
            jobs = Job.query.filter(Job.active == True).all()
            self.entries = {}  # because some jobs might be deactivated
            for job in jobs:
                self.entries[job.id] = JobEntry.from_job(job)

    def create_run(self, entry):
        run = Run()
        job = Job.query.filter_by(id=entry.job_id).one()
        run.job = job
        run.args = job.default_args  # NOTE Args template resolution goes here
        # run.queue = entry.default_queue # TODO Not working/considered for now -> move it to options
        db.session.commit()
        return run
