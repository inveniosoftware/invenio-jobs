# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services config."""

from functools import partial

from invenio_i18n import gettext as _
from invenio_logging.datastreams.schema import LogEventSchema
from invenio_records_resources.services.base import ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from invenio_records_resources.services.records.config import (
    SearchOptions as SearchOptionsBase,
)
from sqlalchemy import asc, desc

from . import results
from invenio_jobs.services.results import Item

from .permissions import (
    AppLogsPermissionPolicy,
)


class AppLogSearchOptions(SearchOptionsBase):
    """App log search options."""

    sort_default = "timestamp"
    sort_direction_default = "desc"
    sort_direction_options = {
        "asc": dict(title=_("Ascending"), fn=asc),
        "desc": dict(title=_("Descending"), fn=desc),
    }
    sort_options = {
        "timestamp": dict(title=_("Timestamp"), fields=["@timestamp"]),
    }

    pagination_options = {"default_results_per_page": 25}


class AppLogServiceConfig(ServiceConfig, ConfiguratorMixin):
    """App log service configuration."""

    service_id = "app-logs"
    permission_policy_cls = FromConfig(
        "APP_LOGS_PERMISSION_POLICY",
        default=AppLogsPermissionPolicy,
    )
    search = AppLogSearchOptions
    schema = LogEventSchema
    components = []
    links_item = None
    result_item_cls = Item
    result_list_cls = results.AppLogsList
