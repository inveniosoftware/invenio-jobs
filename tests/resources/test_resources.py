# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resource tests."""


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
