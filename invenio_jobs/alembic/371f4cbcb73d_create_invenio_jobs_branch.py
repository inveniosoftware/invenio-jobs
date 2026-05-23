# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Create invenio-jobs branch."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "371f4cbcb73d"
down_revision = None
branch_labels = ("invenio_jobs",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
