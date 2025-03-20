# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Logging Service definitions."""

from invenio_logging.proxies import current_logging_manager
from invenio_records_resources.services.base.utils import map_search_params
from invenio_jobs.services.services import BaseService

class AppLogService(BaseService):
    """App log service."""

    def search(self, identity, params):
        """Search for app logs."""
        self.require_permission(identity, "search")
        search_params = map_search_params(self.config.search, params)
        query_param = search_params["q"]
        results = current_logging_manager.search("app", query_param)

        return self.result_list(
            self,
            identity,
            results,
            links_tpl=self.links_item_tpl,
        )
