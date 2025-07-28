# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for subtask service methods."""

import uuid
from datetime import datetime

import pytest
from invenio_db import db

from invenio_jobs.models import Run, RunStatusEnum
from invenio_jobs.proxies import current_jobs_service, current_runs_service
from invenio_jobs.services.errors import RunNotFoundError, RunStatusChangeError


def test_create_subtask_run(app, db, anon_identity, jobs):
    """Test creating a subtask run."""
    # Create a parent run first
    parent_run = current_runs_service.create(
        anon_identity,
        jobs.simple.id,
        {"title": "Parent run"},
    )

    # Create a subtask run
    subtask_run = current_runs_service.create_subtask_run(
        anon_identity,
        parent_run_id=parent_run.id,
        job_id=jobs.simple.id,
    )

    # Verify subtask was created correctly
    assert subtask_run.id is not None
    assert subtask_run.data["parent_run_id"] == parent_run.id
    assert subtask_run.data["job_id"] == jobs.simple.id
    assert subtask_run.data["status"] == RunStatusEnum.QUEUED.name
    assert subtask_run.data["title"] == f"Run {parent_run.id} — Subtask"

    # Verify parent run was updated
    updated_parent = current_runs_service.read(
        anon_identity, jobs.simple.id, parent_run.id
    )
    assert updated_parent.data["total_subtasks"] == 1


def test_create_subtask_run_invalid_parent(app, db, anon_identity, jobs):
    """Test creating subtask with invalid parent run ID."""
    invalid_run_id = str(uuid.uuid4())

    with pytest.raises(RunNotFoundError):
        current_runs_service.create_subtask_run(
            anon_identity, parent_run_id=invalid_run_id, job_id=jobs.simple.id
        )


def test_start_processing_subtask(app, db, anon_identity, jobs):
    """Test starting processing of a subtask."""
    # Create parent and subtask
    parent_run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Parent run"}
    )

    subtask_run = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    # Start processing the subtask
    result = current_runs_service.start_processing_subtask(
        anon_identity, run_id=subtask_run.id, job_id=jobs.simple.id
    )

    # Verify status changed and started_at was set
    assert result.data["status"] == RunStatusEnum.RUNNING.name
    assert result.data["started_at"] is not None


def test_start_processing_subtask_invalid_status(app, db, anon_identity, jobs):
    """Test starting processing of subtask with invalid status."""
    # Create parent and subtask
    parent_run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Parent run"}
    )

    subtask_run = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    # Manually change status to something other than QUEUED
    run_model = db.session.get(Run, subtask_run.id)
    run_model.status = RunStatusEnum.RUNNING
    db.session.commit()

    # Attempting to start processing should fail
    with pytest.raises(RunStatusChangeError):
        current_runs_service.start_processing_subtask(
            anon_identity, run_id=subtask_run.id, job_id=jobs.simple.id
        )


def test_finalize_subtask_success(app, db, anon_identity, jobs):
    """Test finalizing a successful subtask."""
    # Create parent and subtask
    parent_run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Parent run"}
    )

    subtask_run = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    # Start processing
    current_runs_service.start_processing_subtask(
        anon_identity, run_id=subtask_run.id, job_id=jobs.simple.id
    )

    # Finalize subtask as successful
    result = current_runs_service.finalize_subtask(
        anon_identity, run_id=subtask_run.id, job_id=jobs.simple.id, success=True
    )

    # Verify subtask is marked as successful
    assert result.data["status"] == RunStatusEnum.SUCCESS.name

    # Verify parent run is updated correctly
    updated_parent = current_runs_service.read(
        anon_identity, jobs.simple.id, parent_run.id
    )
    assert updated_parent.data["completed_subtasks"] == 1
    assert updated_parent.data["failed_subtasks"] == 0
    assert updated_parent.data["status"] == RunStatusEnum.SUCCESS.name
    assert "1/1 subtasks completed" in updated_parent.data["message"]
    assert updated_parent.data["finished_at"] is not None


def test_finalize_subtask_failure(app, db, anon_identity, jobs):
    """Test finalizing a failed subtask."""
    # Create parent and subtask
    parent_run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Parent run"}
    )

    subtask_run = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    # Start processing
    current_runs_service.start_processing_subtask(
        anon_identity, run_id=subtask_run.id, job_id=jobs.simple.id
    )

    # Finalize subtask as failed
    result = current_runs_service.finalize_subtask(
        anon_identity,
        run_id=subtask_run.id,
        job_id=jobs.simple.id,
        success=False,
        errored_entries_count=5,
    )

    # Verify subtask is marked as failed
    assert result.data["status"] == RunStatusEnum.FAILED.name

    # Verify parent run reflects failure
    updated_parent = current_runs_service.read(
        anon_identity, jobs.simple.id, parent_run.id
    )
    assert updated_parent.data["completed_subtasks"] == 1
    assert updated_parent.data["failed_subtasks"] == 1
    assert updated_parent.data["errored_entries"] == 5
    assert updated_parent.data["status"] == RunStatusEnum.FAILED.name
    assert "1/1 subtasks completed" in updated_parent.data["message"]
    assert "1 subtasks with errors" in updated_parent.data["message"]


def test_finalize_subtask_partial_success(app, db, anon_identity, jobs):
    """Test finalizing multiple subtasks with partial success."""
    # Create parent run
    parent_run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Parent run"}
    )

    # Create two subtasks
    subtask1 = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    subtask2 = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    # Start processing both
    current_runs_service.start_processing_subtask(
        anon_identity, subtask1.id, jobs.simple.id
    )
    current_runs_service.start_processing_subtask(
        anon_identity, subtask2.id, jobs.simple.id
    )

    # Finalize first as success
    current_runs_service.finalize_subtask(
        anon_identity, run_id=subtask1.id, job_id=jobs.simple.id, success=True
    )

    # Verify parent is still running
    updated_parent = current_runs_service.read(
        anon_identity, jobs.simple.id, parent_run.id
    )
    assert updated_parent.data["status"] == RunStatusEnum.RUNNING.name
    assert updated_parent.data["completed_subtasks"] == 1
    assert "1/2 subtasks completed" in updated_parent.data["message"]

    # Finalize second as failure
    current_runs_service.finalize_subtask(
        anon_identity, run_id=subtask2.id, job_id=jobs.simple.id, success=False
    )

    # Verify parent shows partial success
    final_parent = current_runs_service.read(
        anon_identity, jobs.simple.id, parent_run.id
    )
    assert final_parent.data["status"] == RunStatusEnum.PARTIAL_SUCCESS.name
    assert final_parent.data["completed_subtasks"] == 2
    assert final_parent.data["failed_subtasks"] == 1
    assert "2/2 subtasks completed" in final_parent.data["message"]
    assert "1 subtasks with errors" in final_parent.data["message"]


def test_add_total_entries(app, db, anon_identity, jobs):
    """Test adding total entries to a run."""
    # Create a run
    run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Test run"}
    )

    # Add total entries
    result = current_runs_service.add_total_entries(
        anon_identity, run_id=run.id, job_id=jobs.simple.id, total_entries=100
    )

    # Verify total entries was updated
    assert result.data["total_entries"] == 100


def test_add_total_entries_invalid_values(app, db, anon_identity, jobs):
    """Test adding invalid total entries values."""
    # Create a run
    run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Test run"}
    )

    # Test negative value
    with pytest.raises(ValueError, match="total_entries cannot be negative"):
        current_runs_service.add_total_entries(
            anon_identity, run_id=run.id, job_id=jobs.simple.id, total_entries=-10
        )

    # Test non-integer value
    with pytest.raises(ValueError, match="total_entries must be an integer"):
        current_runs_service.add_total_entries(
            anon_identity, run_id=run.id, job_id=jobs.simple.id, total_entries="invalid"
        )


def test_finalize_subtask_with_errored_entries_message(app, db, anon_identity, jobs):
    """Test finalize subtask includes errored entries in progress message."""
    # Create parent run with total entries set
    parent_run = current_runs_service.create(
        anon_identity, jobs.simple.id, {"title": "Parent run"}
    )

    # Add total entries to parent
    current_runs_service.add_total_entries(
        anon_identity, run_id=parent_run.id, job_id=jobs.simple.id, total_entries=1000
    )

    # Create subtask
    subtask_run = current_runs_service.create_subtask_run(
        anon_identity, parent_run_id=parent_run.id, job_id=jobs.simple.id
    )

    # Start and finalize with errored entries
    current_runs_service.start_processing_subtask(
        anon_identity, subtask_run.id, jobs.simple.id
    )

    current_runs_service.finalize_subtask(
        anon_identity,
        run_id=subtask_run.id,
        job_id=jobs.simple.id,
        success=True,
        errored_entries_count=25,
    )

    # Verify message includes errored entries
    updated_parent = current_runs_service.read(
        anon_identity, jobs.simple.id, parent_run.id
    )
    assert "25/1000 entries errored" in updated_parent.data["message"]


def test_finalize_subtask_nonexistent_run(app, db, anon_identity, jobs):
    """Test finalizing a non-existent subtask."""
    invalid_run_id = str(uuid.uuid4())

    with pytest.raises(RunNotFoundError):
        current_runs_service.finalize_subtask(
            anon_identity, run_id=invalid_run_id, job_id=jobs.simple.id, success=True
        )
