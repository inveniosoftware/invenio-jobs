#
# This file is part of Invenio.
# Copyright (C) 2016-2026 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Merge invenio_jobs heads."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1773910810"
down_revision = ("1757597048", "9732b5f7609a")
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
