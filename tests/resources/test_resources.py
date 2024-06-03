# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resource tests."""

import pdb
from unittest.mock import patch

from invenio_jobs.tasks import execute_run


@patch.object(execute_run, "apply_async")
def test_simple_flow(mock_apply_async, app, db, client, user):
    """Test simple flow."""
    client = user.login(client)
    job_paylod = {
        "title": "Test job",
        "task": "tasks.mock_task",
        "description": "Test description",
        "active": False,
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
        "schedule": {"type": "interval", "hours": 4},
    }

    # Create a job
    res = client.post("/jobs", json=job_paylod)
    assert res.status_code == 201
    job_id = res.json["id"]
    expected_job = {
        "id": job_id,
        "title": "Test job",
        "description": "Test description",
        "active": False,
        "task": "tasks.mock_task",
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
        "schedule": {"type": "interval", "hours": 4},
        "last_run": None,
        "created": res.json["created"],
        "updated": res.json["updated"],
        "links": {
            "self": f"https://127.0.0.1:5000/api/jobs/{job_id}",
            "runs": f"https://127.0.0.1:5000/api/jobs/{job_id}/runs",
        },
    }

    assert res.json == expected_job

    # Activate the job (i.e. update)
    res = client.put(f"/jobs/{job_id}", json={**job_paylod, "active": True})
    assert res.status_code == 200
    expected_job["active"] = True
    expected_job["updated"] = res.json["updated"]
    assert res.json == expected_job

    # List jobs
    res = client.get("/jobs")
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0] == expected_job

    # Get job
    res = client.get(f"/jobs/{job_id}")
    assert res.status_code == 200
    assert res.json == expected_job

    # Create/trigger a run
    res = client.post(
        f"/jobs/{job_id}/runs",
        json={
            "title": "Manually triggered run",
            "args": {
                "arg1": "manual_value1",
                "arg2": "manual_value2",
                "kwarg2": "manual_value3",
            },
            "queue": "celery",
        },
    )
    assert res.status_code == 201
    run_id = res.json["id"]
    expected_run = {
        "id": run_id,
        "job_id": job_id,
        "started_by_id": int(user.id),
        "started_by": {
            "id": str(user.id),
            "username": user.username,
            "profile": user._user_profile,
            "links": {
                # "self": f"https://127.0.0.1:5000/api/users/{user.id}",
            },
            "identities": {},
            "is_current_user": True,
            "type": "user",
        },
        "started_at": res.json["started_at"],
        "finished_at": res.json["finished_at"],
        "status": "QUEUED",
        "message": None,
        "title": "Manually triggered run",
        "args": {
            "arg1": "manual_value1",
            "arg2": "manual_value2",
            "kwarg2": "manual_value3",
        },
        "queue": "celery",
        "created": res.json["created"],
        "updated": res.json["updated"],
        "links": {
            "self": f"https://127.0.0.1:5000/api/jobs/{job_id}/runs/{run_id}",
            "logs": f"https://127.0.0.1:5000/api/jobs/{job_id}/runs/{run_id}/logs",
            "stop": f"https://127.0.0.1:5000/api/jobs/{job_id}/runs/{run_id}/actions/stop",
        },
    }
    assert "task_id" in res.json
    assert res.json["task_id"] != None
    expected_run["task_id"] = res.json["task_id"]
    assert res.json == expected_run

    # List runs
    res = client.get(f"/jobs/{job_id}/runs")
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0] == expected_run

    # Get run
    res = client.get(f"/jobs/{job_id}/runs/{run_id}")
    assert res.status_code == 200
    assert res.json == expected_run

    # Stop run
    res = client.post(f"/jobs/{job_id}/runs/{run_id}/actions/stop")
    assert res.status_code == 202
    assert res.json["status"] == "CANCELLING"


def test_tasks_search(client):
    """Test tasks search."""
    mock_task_res = {
        "name": "tasks.mock_task",
        "description": "Mock task description.",
        "links": {},
        "parameters": {
            "arg1": {
                "name": "arg1",
                "default": None,
                "kind": "POSITIONAL_OR_KEYWORD",
            },
            "arg2": {
                "name": "arg2",
                "default": None,
                "kind": "POSITIONAL_OR_KEYWORD",
            },
            "kwarg1": {
                "name": "kwarg1",
                "default": None,
                "kind": "POSITIONAL_OR_KEYWORD",
            },
            "kwarg2": {
                "name": "kwarg2",
                "default": False,
                "kind": "POSITIONAL_OR_KEYWORD",
            },
            "kwarg3": {
                "name": "kwarg3",
                "default": "always",
                "kind": "POSITIONAL_OR_KEYWORD",
            },
        },
    }
    res = client.get("/tasks")
    assert res.status_code == 200
    assert "hits" in res.json
    # We can't know exactly what tasks will be in the results
    assert res.json["hits"]["total"] > 0
    assert mock_task_res in res.json["hits"]["hits"]

    # Test filtering
    res = client.get("/tasks?q=mock_task")
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert mock_task_res == res.json["hits"]["hits"][0]


def test_jobs_create(db, client):
    """Test job creation."""
    # Test minimal job payload
    res = client.post(
        "/jobs",
        json={
            "title": "Test minimal job",
            "task": "tasks.mock_task",
        },
    )
    assert res.status_code == 201
    assert res.json == {
        "id": res.json["id"],
        "title": "Test minimal job",
        "description": None,
        "active": True,
        "task": "tasks.mock_task",
        "default_queue": "celery",
        "default_args": {},
        "schedule": None,
        "last_run": None,
        "created": res.json["created"],
        "updated": res.json["updated"],
        "links": {
            "runs": f"https://127.0.0.1:5000/api/jobs/{res.json['id']}/runs",
            "self": f"https://127.0.0.1:5000/api/jobs/{res.json['id']}",
        },
    }

    # Test full job payload
    res = client.post(
        "/jobs",
        json={
            "title": "Test full job",
            "task": "tasks.mock_task",
            "description": "Test description",
            "active": False,
            "default_queue": "low",
            "default_args": {
                "arg1": "value1",
                "arg2": "value2",
                "kwarg1": "value3",
            },
            "schedule": {"type": "interval", "hours": 4},
        },
    )
    assert res.status_code == 201
    assert res.json == {
        "id": res.json["id"],
        "title": "Test full job",
        "description": "Test description",
        "active": False,
        "task": "tasks.mock_task",
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
        "schedule": {"type": "interval", "hours": 4},
        "last_run": None,
        "created": res.json["created"],
        "updated": res.json["updated"],
        "links": {
            "runs": f"https://127.0.0.1:5000/api/jobs/{res.json['id']}/runs",
            "self": f"https://127.0.0.1:5000/api/jobs/{res.json['id']}",
        },
    }


def test_jobs_update(db, client, jobs):
    """Test job updates."""
    # Update existing job
    res = client.put(
        f"/jobs/{jobs.simple.id}",
        json={
            "title": "Test updated job",
            "task": "tasks.mock_task",
            "description": "Test updated description",
            "schedule": {"type": "interval", "hours": 2},
            "active": False,
            "default_queue": "celery",
            "default_args": {
                "arg1": "new_value1",
                "arg2": "new_value2",
                "kwarg2": False,
            },
        },
    )
    assert res.status_code == 200
    updated_job = {
        "id": jobs.simple.id,
        "title": "Test updated job",
        "description": "Test updated description",
        "active": False,
        "task": "tasks.mock_task",
        "default_queue": "celery",
        "default_args": {
            "arg1": "new_value1",
            "arg2": "new_value2",
            "kwarg2": False,
        },
        "schedule": {"type": "interval", "hours": 2},
        "last_run": None,
        "created": jobs.simple["created"],
        "updated": res.json["updated"],
        "links": {
            "runs": f"https://127.0.0.1:5000/api/jobs/{jobs.simple.id}/runs",
            "self": f"https://127.0.0.1:5000/api/jobs/{jobs.simple.id}",
        },
    }
    assert res.json == updated_job

    # Read the job to check the update
    res = client.get(f"/jobs/{jobs.simple.id}")
    assert res.status_code == 200
    assert res.json == updated_job


def test_jobs_search(client, jobs):
    """Test jobs search."""
    res = client.get("/jobs")
    assert res.status_code == 200
    assert "hits" in res.json
    assert res.json["hits"]["total"] == 3
    hits = res.json["hits"]["hits"]

    interval_job_res = next((j for j in hits if j["id"] == jobs.interval.id), None)
    assert interval_job_res == {
        "id": jobs.interval.id,
        "title": "Test interval job",
        "description": None,
        "active": True,
        "task": "tasks.mock_task",
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
        "schedule": {
            "type": "interval",
            "hours": 4,
        },
        "last_run": None,
        "created": jobs.interval["created"],
        "updated": jobs.interval["updated"],
        "links": {
            "runs": f"https://127.0.0.1:5000/api/jobs/{jobs.interval.id}/runs",
            "self": f"https://127.0.0.1:5000/api/jobs/{jobs.interval.id}",
        },
    }

    crontab_job_res = next((j for j in hits if j["id"] == jobs.crontab.id), None)
    assert crontab_job_res == {
        "id": jobs.crontab.id,
        "title": "Test crontab job",
        "description": None,
        "active": True,
        "task": "tasks.mock_task",
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
        "schedule": {
            "type": "crontab",
            "minute": "0",
            "hour": "0",
            "day_of_week": "*",
            "day_of_month": "*",
            "month_of_year": "*",
        },
        "last_run": None,
        "created": jobs.crontab["created"],
        "updated": jobs.crontab["updated"],
        "links": {
            "runs": f"https://127.0.0.1:5000/api/jobs/{jobs.crontab.id}/runs",
            "self": f"https://127.0.0.1:5000/api/jobs/{jobs.crontab.id}",
        },
    }

    simple_job_res = next((j for j in hits if j["id"] == jobs.simple.id), None)
    assert simple_job_res == {
        "id": jobs.simple.id,
        "title": "Test unscheduled job",
        "description": None,
        "active": True,
        "task": "tasks.mock_task",
        "default_queue": "low",
        "default_args": {
            "arg1": "value1",
            "arg2": "value2",
            "kwarg1": "value3",
        },
        "schedule": None,
        "last_run": None,
        "created": jobs.simple["created"],
        "updated": jobs.simple["updated"],
        "links": {
            "runs": f"https://127.0.0.1:5000/api/jobs/{jobs.simple.id}/runs",
            "self": f"https://127.0.0.1:5000/api/jobs/{jobs.simple.id}",
        },
    }

    # Test filtering
    res = client.get("/jobs?q=interval")
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert interval_job_res == res.json["hits"]["hits"][0]


def test_jobs_delete(db, client, jobs):
    """Test job deletion."""
    res = client.delete(f"/jobs/{jobs.simple.id}")
    assert res.status_code == 204

    # Shouldn't be able to get again
    res = client.get(f"/jobs/{jobs.simple.id}")
    assert res.status_code == 404
    assert res.json == {
        "message": f"Job with ID {jobs.simple.id} does not exist.",
        "status": 404,
    }

    # Shouldn't appear in search results
    res = client.get("/jobs")
    assert res.status_code == 200
    assert "hits" in res.json
    assert res.json["hits"]["total"] == 2
    hits = res.json["hits"]["hits"]
    assert all(j["id"] != jobs.simple.id for j in hits)
