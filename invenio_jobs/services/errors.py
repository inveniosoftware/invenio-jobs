# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service definitions."""

from invenio_i18n import gettext as _


class JobsError(Exception):
    """Base class for Jobs errors."""

    def __init__(self, description, *args: object):
        """Constructor."""
        self.description = description
        super().__init__(*args)


class JobNotFoundError(JobsError):
    """Job not found error."""

    def __init__(self, id):
        """Initialise error."""
        super().__init__(
            description=_("Job with ID {id} does not exist.").format(id=id)
        )
