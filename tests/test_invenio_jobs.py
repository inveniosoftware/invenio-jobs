# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Module tests."""

from flask import Flask

from invenio_jobs import InvenioJobs


def test_version():
    """Test version import."""
    from invenio_jobs import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioJobs(app)
    assert "invenio-jobs" in app.extensions

    app = Flask("testapp")
    ext = InvenioJobs()
    assert "invenio-jobs" not in app.extensions
    ext.init_app(app)
    assert "invenio-jobs" in app.extensions
