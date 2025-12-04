#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add notifications column to jobs_job."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1764848648"
down_revision = "1753948224"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        "jobs_job",
        sa.Column(
            "notifications",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
    )


def downgrade():
    """Downgrade database."""
    op.drop_column("jobs_job", "notifications")
