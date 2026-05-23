# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alter datetime columns to utc aware datetime columns."""

from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "9732b5f7609a"
down_revision = "1753948224"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    for table_name in ["jobs_job", "jobs_run"]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")
    update_table_columns_column_type_to_utc_datetime("jobs_run", "started_at")
    update_table_columns_column_type_to_utc_datetime("jobs_run", "finished_at")


def downgrade():
    """Downgrade database."""
    for table_name in ["jobs_job", "jobs_run"]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
    update_table_columns_column_type_to_datetime("jobs_run", "started_at")
    update_table_columns_column_type_to_datetime("jobs_run", "finished_at")
