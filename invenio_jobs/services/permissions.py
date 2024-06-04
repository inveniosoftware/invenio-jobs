# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service permissions."""

from invenio_administration.generators import Administration
from invenio_records_permissions.policies import BasePermissionPolicy
from invenio_records_permissions.generators import SystemProcess


class TasksPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for tasks."""

    can_search = [Administration()]
    can_read = [Administration()]


class JobPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for jobs."""

    can_search = [Administration()]
    can_create = [Administration()]
    can_read = [Administration(), SystemProcess()]
    can_update = [Administration()]
    can_delete = [Administration()]


class RunPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for runs.

    Later the runs may be done by librarians.
    """

    can_search = [Administration()]
    can_create = [Administration()]
    can_read = [Administration()]
    can_update = [Administration()]
    can_delete = [Administration()]
    can_stop = [Administration()]
