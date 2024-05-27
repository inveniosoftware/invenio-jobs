# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import traceback
import uuid
from typing import Any

from celery.beat import ScheduleEntry, Scheduler, debug, error, info
from invenio_db import db

from invenio_jobs.models import Job, Run


class JobEntry(ScheduleEntry):

    job = None

    def __init__(self, job, *args, **kwargs):
        self.job = job
        super().__init__(*args, **kwargs)

    @classmethod
    def from_job(cls, job):
        return cls(
            job=job,
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
        # TODO Check whether we need the celery backend task?
        self.sync()

    def reserve(self, entry):
        new_entry = self.schedule[entry.job.id] = next(entry)
        return new_entry

    def apply_entry(self, entry, producer=None):
        with self.app.flask_app.app_context():
            info("Scheduler: Sending due task %s (%s)", entry.name, entry.task)
            try:
                # TODO Only create and send task if there is no "stale" run (status running, starttime > hour, Run pending for > 1 hr)
                run = self.create_run(entry)
                entry.options["task_id"] = str(run.task_id)
                result = self.apply_async(entry, producer=producer, advance=False)
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
            jobs = Job.query.filter(Job.active == True).all()
            self.entries = {}  # because some jobs might be deactivated
            for job in jobs:
                self.entries[job.id] = JobEntry.from_job(job)

    def create_run(self, entry):
        run = Run()
        job = Job.query.filter_by(id=entry.job.id).one()
        run.job = job
        run.args = job.default_args  # NOTE Args template resolution goes here
        # run.queue = entry.default_queue # TODO Not working/considered for now -> move it to options
        run.task_id = uuid.uuid4()
        db.session.commit()
        return run
