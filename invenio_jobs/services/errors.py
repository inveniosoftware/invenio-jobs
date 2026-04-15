# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
# Copyright (C) 2026 KTH Royal Institute of Technology.
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
        super().__init__(description=_("Job with ID %(id)s does not exist.", id=id))


class RunNotFoundError(JobsError):
    """Run not found error."""

    def __init__(self, id, job_id=None):
        """Initialise error."""
        description = _("Run with ID %(id)s does not exist.", id=id)
        if job_id:
            description = _(
                "Run with ID %(id)s for job %(job_id)s does not exist.",
                id=id,
                job_id=job_id,
            )
        super().__init__(description=description)


class RunStatusChangeError(JobsError):
    """Run status change error."""

    def __init__(self, run, new_status):
        """Initialise error."""
        self.run = run
        self.new_status = new_status
        super().__init__(
            description=_(
                "You cannot change run status from %(old)s to %(new)s.",
                old=run.status,
                new=new_status,
            )
        )


class RunTooManyResults(JobsError):
    """Run too many results error."""

    def __init__(self, total, max_docs):
        """Initialise error."""
        super().__init__(
            description=_(
                "Too many log results returned (%(total)s). The maximum allowed "
                "is %(max_docs)s. Please refine your search criteria to reduce "
                "the result size.",
                total=total,
                max_docs=max_docs,
            )
        )
