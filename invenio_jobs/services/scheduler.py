# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import traceback
import uuid
from typing import Any

from celery.beat import ScheduleEntry, Scheduler, logger
from invenio_db import db

from invenio_jobs.models import Job, Run, Task


class JobEntry(ScheduleEntry):

    job = None

    def __init__(self, job, *args, **kwargs):
        self.job = job
        super().__init__(*args, **kwargs)

    @staticmethod
    def parse_args(job_args, task):
        # NOTE In future if we use positional only args with celery tasks, this will need an update
        # Since we are only returning kwargs for now
        # TODO add check for self?
        return tuple(), job_args or {}

    @classmethod
    def from_job(cls, job):
        args, kwargs = cls.parse_args(job.default_args or {}, job.task)
        return cls(
            job=job,
            name=job.title,
            schedule=job.parsed_schedule,
            args=args,
            kwargs=kwargs,
            task=job.task,
            options={
                "queue": job.default_queue
            },
            last_run_at=(job.last_run and job.last_run.created),
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
        new_entry = self.schedule[entry.job.id] = next(entry)
        return new_entry

    def apply_entry(self, entry, producer=None):
        with self.app.flask_app.app_context():
            logger.info("Scheduler: Sending due task %s (%s)", entry.name, entry.task)
            try:
                # TODO Only create and send task if there is no "stale" run (status running, starttime > hour, Run pending for > 1 hr)
                run = self.create_run(entry)
                entry.options["task_id"] = str(run.task_id)
                if not entry.task:
                    return
                result = self.apply_async(entry, producer=producer, advance=False)
            except Exception as exc:
                logger.error(
                    "Message Error: %s\n%s",
                    exc,
                    traceback.format_stack(),
                    exc_info=True,
                )
            else:
                if result and hasattr(result, "id"):
                    logger.debug("%s sent. id->%s", entry.task, result.id)
                else:
                    logger.debug("%s sent.", entry.task)

    def sync(self):
        # TODO Should we also have a cleaup task for runs? "stale" run (status running, starttime > hour, Run pending for > 1 hr)
        with self.app.flask_app.app_context():
            jobs = Job.query.filter(Job.active == True).all()
            self.entries = {}  # because some jobs might be deactivated
            for job in jobs:
                self.entries[job.id] = JobEntry.from_job(job)

    def create_run(self, entry):
        run = Run()
        job = Job.query.filter_by(id=entry.job.id).one()
        run.job = job
        run.args = job.default_args  # NOTE Args template resolution goes here
        run.queue = job.default_queue # TODO Not working/considered for now -> move it to options
        run.task_id = uuid.uuid4()
        print("creating run")
        db.session.commit()
        return run
