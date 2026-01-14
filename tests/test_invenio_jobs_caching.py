# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from invenio_jobs.models import Job, Run


def test_job_last_runs_cache_expiration(db, jobs):
    """Test job bulk loading."""
    job = Job.query.first()

    run = Run.create(job, queue="celery")
    db.session.add(run)
    db.session.commit()

    # job.last_runs and job.last_run are not in cache yet
    assert "last_runs" not in job.__dict__.keys()
    assert "last_run" not in job.__dict__.keys()

    # cache job.last_runs and job.last_run by calling bulk_load_last_runs
    Job.bulk_load_last_runs([job])

    # job.last_runs and job.last_run are in cache now
    assert "last_runs" in job.__dict__.keys()
    assert "last_run" in job.__dict__.keys()

    x = job.last_runs
    y = job.last_runs

    # job.last_runs returns the same instance from cache
    assert x is y

    # expire cache and thus empty job.last_runs and job.last_run
    db.session.expire(job)

    # job.last_runs and job.last_run are not in cache anymore
    assert "last_runs" not in job.__dict__.keys()
    assert "last_run" not in job.__dict__.keys()

    # cache job.last_runs and job.last_run by calling job.last_runs
    z = job.last_runs

    # job.last_runs now returns different instance from cache than the one return before cache expiration
    assert z is not y

    # job.last_runs and job.last_run are in cache again
    assert "last_runs" in job.__dict__.keys()
    assert "last_run" in job.__dict__.keys()
