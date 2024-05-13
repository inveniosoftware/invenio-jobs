# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration."""

JOBS_ADMINISTRATION_DISABLED = False
from invenio_i18n import lazy_gettext as _

RDM_JOBS_FACETS = {}

RDM_JOBS_SORT_OPTIONS = {
    "jobs": dict(
        title=_("Jobs"),
        fields=["jobs"],
    ),
    "last_run_start_time": dict(
        # title=_("Last run"),
        fields=["last_run_start_time"],
    ),
    "user": dict(
        title=_("Started by"),
        fields=["user"],
    ),
    "next_run": dict(
        title=_("Next run"),
        fields=["next_run"],
    ),
}
"""Definitions of available Jobs sort options. """

RDM_JOBS_SEARCH = {
    "facets": [],
    "sort": ["jobs", "last_run_start_time", "user", "next_run"],
}
"""Jobs search configuration."""
