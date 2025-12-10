# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2025 KTH Royal Institute of Technology.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import pytest

from invenio_jobs.proxies import current_jobs_logs_service


@pytest.mark.usefixtures("app")
def test_job_logs_search_limits_to_max_docs(
    monkeypatch, anon_identity, app, _make_hit, FakeSearch
):
    """Service returns only the most recent max_docs hits with a warning."""
    service = current_jobs_logs_service

    original_max = app.config.get("JOBS_LOGS_MAX_RESULTS")
    original_batch = app.config.get("JOBS_LOGS_BATCH_SIZE")
    app.config["JOBS_LOGS_MAX_RESULTS"] = 5
    app.config["JOBS_LOGS_BATCH_SIZE"] = 5

    created_searches = []

    hits = [_make_hit(idx) for idx in range(8, 0, -1)]

    def fake_search(self, *args, **kwargs):
        search = FakeSearch(hits)
        created_searches.append(search)
        return search

    monkeypatch.setattr(service.__class__, "_search", fake_search)

    payload = None
    try:
        with app.app_context():
            result = service.search(anon_identity, {"q": "test"})
            payload = result.to_dict()
    finally:
        app.config["JOBS_LOGS_MAX_RESULTS"] = original_max
        app.config["JOBS_LOGS_BATCH_SIZE"] = original_batch

    assert created_searches
    search_obj = created_searches[0]
    assert search_obj.execute_calls == 1

    assert payload["hits"]["total"] == len(hits)
    assert len(payload["hits"]["hits"]) == 5
    messages = [entry["message"] for entry in payload["hits"]["hits"]]
    assert messages == ["log-8", "log-7", "log-6", "log-5", "log-4"]

    # Verify warning is present
    assert "warnings" in payload
    assert len(payload["warnings"]) == 1
    warning = payload["warnings"][0]
    assert warning["type"] == "truncated_results"
    assert warning["total_available"] == 8
    assert warning["max_results"] == 5
    assert "Too many log results" in warning["message"]

    assert "sort" in payload["hits"]
    # The last returned hit is the 5th one (index 4 in hits), which is log-4
    assert payload["hits"]["sort"] == hits[4].meta.sort


@pytest.mark.usefixtures("app")
def test_job_logs_search_returns_all_when_under_limit(
    monkeypatch, anon_identity, app, _make_hit, FakeSearch
):
    """Service returns all results when total is below max_docs."""
    service = current_jobs_logs_service

    original_max = app.config.get("JOBS_LOGS_MAX_RESULTS")
    original_batch = app.config.get("JOBS_LOGS_BATCH_SIZE")
    app.config["JOBS_LOGS_MAX_RESULTS"] = 5
    app.config["JOBS_LOGS_BATCH_SIZE"] = 5

    hits = [_make_hit(idx) for idx in range(3, 0, -1)]

    def fake_search(self, *args, **kwargs):
        return FakeSearch(hits)

    monkeypatch.setattr(service.__class__, "_search", fake_search)

    payload = None
    try:
        with app.app_context():
            result = service.search(anon_identity, {"q": "test"})
            payload = result.to_dict()
    finally:
        app.config["JOBS_LOGS_MAX_RESULTS"] = original_max
        app.config["JOBS_LOGS_BATCH_SIZE"] = original_batch

    assert payload["hits"]["total"] == len(hits)
    assert len(payload["hits"]["hits"]) == len(hits)
    messages = [entry["message"] for entry in payload["hits"]["hits"]]
    assert messages == ["log-3", "log-2", "log-1"]

    # Verify no warning when under limit
    assert "warnings" not in payload

    assert payload["hits"]["sort"] == hits[2].meta.sort  # Last hit (log-1)
