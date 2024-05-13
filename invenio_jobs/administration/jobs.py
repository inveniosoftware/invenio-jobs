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
from invenio_search_ui.searchconfig import search_app_config


class JobListView(AdminResourceListView):
    """Search admin view for jobs."""

    api_endpoint = "/jobs"
    name = "jobs"
    resource_config = "jobs_resource"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    title = "Jobs"
    menu_label = "Jobs"
    category = "System"
    pid_path = "id"
    icon = "cogs"
    template = "invenio_administration/search.html"

    display_search = True
    display_delete = False
    display_create = True
    display_edit = True

    item_field_list = {
        "title": {"text": "Title", "order": 1, "width": 4},
    }

    actions = {
        # TODO: Define actions
        # "delete": {
        #     "text": "Delete",
        #     "payload_schema": None,
        #     "order": 2,
        # },
    }
    # TODO: Define search config for jobs
    # search_config_name = "JOBS_SEARCH"
    # search_facets_config_name = "JOBS_FACETS"
    # search_sort_config_name = "JOBS_SORT_OPTIONS"

    # def init_search_config(self):
    #     """Build search view config."""
    #     return partial(
    #         search_app_config,
    #         config_name=self.get_search_app_name(),
    #         available_facets=current_app.config.get(self.search_facets_config_name),
    #         sort_options=current_app.config[self.search_sort_config_name],
    #         endpoint=self.get_api_endpoint(),
    #         headers=self.get_search_request_headers(),
    #         initial_filters=[["status", "P"]],
    #         hidden_params=[
    #             ["include_deleted", "1"],
    #         ],
    #         page=1,
    #         size=30,
    #     )

    @staticmethod
    def disabled():
        """Disable the view on demand."""
        return current_app.config["JOBS_ADMINISTRATION_DISABLED"]


class JobDetailView(AdminResourceDetailView):
    """Admin job detail view."""

    url = "/jobs/<pid_value>"
    api_endpoint = "/jobs"
    name = "job-details"
    resource_config = "jobs_resource"
    title = "Job"

    template = "invenio_administration/details.html"
    display_delete = True
    display_edit = True

    list_view_name = "jobs"
    pid_path = "id"
    request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}

    actions = {}

    item_field_list = {
        "title": {"text": "Title", "order": 1},
    }
