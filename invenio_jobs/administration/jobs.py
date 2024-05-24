# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration view module."""

from functools import partial

from flask import current_app
from invenio_administration.views.base import (
    AdminResourceDetailView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _
from invenio_search_ui.searchconfig import search_app_config


class JobsListView(AdminResourceListView):
    """Configuration for Jobs list view."""

    api_endpoint = "/jobs"
    name = "jobs"
    resource_config = "jobs_resource"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    title = "Jobs"
    menu_label = "Jobs"
    category = "System"
    pid_path = "id"
    icon = "settings"
    template = "invenio_jobs/system/jobs/jobs-search.html"

    display_search = False
    display_delete = False
    display_create = False
    display_edit = False

    item_field_list = {
        "active": {"text": _("Active"), "order": 1, "width": 1},
        "job": {"text": _("Jobs"), "order": 2, "width": 3},
        "last_run_start_time": {"text": _("Last run"), "order": 3, "width": 3},
        "user": {"text": _("Started by"), "order": 4, "width": 3},
        "next_run": {"text": _("Next run"), "order": 5, "width": 3},
    }

    search_config_name = "JOBS_SEARCH"
    search_sort_config_name = "JOBS_SORT_OPTIONS"
    search_facets_config_name = "JOBS_FACETS"

    actions = {
        "settings": {
            "text": "Settings",
            "payload_schema": None,
            "order": 1,
            "icon": "star",
        },
        "schedule": {
            "text": "Schedule",
            "payload_schema": None,
            "order": 2,
        },
        "run": {
            "text": "Run Now",
            "payload_schema": None,
            "order": 2,
        },
    }


class JobsDetailsView(AdminResourceListView):
    """Configuration for Jobs detail view which shows runs."""

    api_endpoint = "/jobs/<pid_value>/runs"
    url = "/jobs/<pid_value>"
    search_request_headers = {"Accept": "application/json"}
    name = "job-details"
    resource_config = "runs_resource"
    title = "Job Details"
    disabled = lambda _: True

    template = "invenio_jobs/system/jobs/jobs-details.html"
    display_delete = False
    display_edit = False
    display_search = False
    display_create = False

    list_view_name = "jobs"
    pid_path = "id"
    pid_value = "<pid_value>"

    item_field_list = {
        "run": {"text": _("Run"), "order": 1, "width": 2},
        "duration": {"text": _("Duration"), "order": 2, "width": 2},
        "message": {"text": _("Message"), "order": 3, "width": 10},
        "user": {"text": _("Started by"), "order": 4, "width": 2},
    }

    search_config_name = "JOBS_SEARCH"
    search_sort_config_name = "JOBS_SORT_OPTIONS"
    search_facets_config_name = "JOBS_FACETS"

    actions = {
        "settings": {
            "text": "Settings",
            "payload_schema": None,
            "order": 1,
        },
        "schedule": {
            "text": "Schedule",
            "payload_schema": None,
            "order": 2,
        },
        "run": {
            "text": "Run Now",
            "payload_schema": None,
            "order": 2,
        },
    }
