# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service permissions."""

from invenio_administration.generators import Administration
from invenio_records_permissions.generators import Disable, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy

class AppLogsPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for app logs."""

    can_search = [Administration(), SystemProcess()]
    can_create = [Disable()]
    can_read = [Disable()]
    can_update = [Disable()]
    can_delete = [Disable()]
