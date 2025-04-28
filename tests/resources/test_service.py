# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service tests."""

from invenio_access.permissions import system_identity

from invenio_jobs.proxies import current_jobs_service, current_runs_service




def test_create_run(app, db):
    """Test service create."""

    current_runs_service.create(system_identity, )
