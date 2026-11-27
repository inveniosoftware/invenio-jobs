# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Module tests."""

from flask import Flask
from invenio_administration.marshmallow_utils import jsonify_schema
from marshmallow import fields

from invenio_jobs import InvenioJobs
from invenio_jobs.jobs import PredefinedArgsSchema


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


def test_predefined_args_schema_subclass_defaults():
    """Subclasses of PredefinedArgsSchema bind job_arg_schema to their own name."""

    class CustomArgsSchema(PredefinedArgsSchema):
        dry_run = fields.Boolean(required=False, load_default=False)

    class ChildCustomArgsSchema(CustomArgsSchema):
        limit = fields.Integer(required=False, load_default=10)

    class WorkaroundParentSchema(PredefinedArgsSchema):
        job_arg_schema = fields.String(
            metadata={"type": "hidden"},
            dump_default="WorkaroundParentSchema",
            load_default="WorkaroundParentSchema",
        )

    class ChildOfWorkaroundSchema(WorkaroundParentSchema):
        extra = fields.String(required=False, load_default="x")

    class ExplicitOverrideSchema(PredefinedArgsSchema):
        job_arg_schema = fields.String(
            metadata={"type": "hidden"},
            dump_default="custom_override",
            load_default="custom_override",
        )

    DynamicArgsSchema = PredefinedArgsSchema.from_dict(
        {"dry_run": fields.Boolean(required=False, load_default=False)},
        name="DynamicArgsSchema",
    )

    custom = CustomArgsSchema()
    assert (
        custom.fields["job_arg_schema"]
        is custom.load_fields["job_arg_schema"]
        is custom.dump_fields["job_arg_schema"]
    )
    assert custom.dump({}) == {"job_arg_schema": "CustomArgsSchema"}
    assert custom.load({}) == {
        "job_arg_schema": "CustomArgsSchema",
        "dry_run": False,
    }
    ui_schema = jsonify_schema(custom)
    assert ui_schema["job_arg_schema"]["dump_default"] == "CustomArgsSchema"
    assert ui_schema["job_arg_schema"]["load_default"] == "CustomArgsSchema"

    child = ChildCustomArgsSchema()
    assert child.dump({}) == {"job_arg_schema": "ChildCustomArgsSchema"}
    assert child.load({}) == {
        "job_arg_schema": "ChildCustomArgsSchema",
        "dry_run": False,
        "limit": 10,
    }

    workaround_child = ChildOfWorkaroundSchema()
    assert workaround_child.dump({}) == {"job_arg_schema": "ChildOfWorkaroundSchema"}
    assert workaround_child.load({}) == {
        "job_arg_schema": "ChildOfWorkaroundSchema",
        "extra": "x",
    }

    explicit = ExplicitOverrideSchema()
    assert explicit.dump({}) == {"job_arg_schema": "custom_override"}
    assert explicit.load({}) == {"job_arg_schema": "custom_override"}

    excluded = CustomArgsSchema(exclude=("job_arg_schema",))
    assert excluded.dump({}) == {}
    assert excluded.load({}) == {"dry_run": False}

    dynamic = DynamicArgsSchema()
    assert dynamic.dump({}) == {"job_arg_schema": "DynamicArgsSchema"}
    assert dynamic.load({}) == {
        "job_arg_schema": "DynamicArgsSchema",
        "dry_run": False,
    }

    # Base PredefinedArgsSchema remains unaffected after instantiating subclasses
    base = PredefinedArgsSchema()
    assert base.dump({}) == {"job_arg_schema": "PredefinedArgsSchema"}
    assert base.load({}) == {"job_arg_schema": "PredefinedArgsSchema"}
