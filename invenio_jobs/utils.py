# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities."""

import ast
from datetime import datetime

from flask import current_app, render_template
from invenio_mail.tasks import send_email
from jinja2.sandbox import SandboxedEnvironment

jinja_env = SandboxedEnvironment()


def eval_tpl_str(val, ctx):
    """Evaluate a Jinja template string."""
    if not isinstance(val, str):
        return val

    tpl = jinja_env.from_string(val)
    res = tpl.render(**ctx)

    try:
        res = ast.literal_eval(res)
    except Exception:
        pass

    return res


def walk_values(obj, transform_fn):
    """Recursively apply a function in-place to the value of dictionary or list."""
    if isinstance(obj, dict):
        items = obj.items()
    elif isinstance(obj, list):
        items = enumerate(obj)
    else:
        return transform_fn(obj)

    for key, val in items:
        if isinstance(val, (dict, list)):
            walk_values(val, transform_fn)
        else:
            obj[key] = transform_fn(val)


def job_arg_json_dumper(obj):
    """Handle non-serializable values such as datetimes when dumping the arguments of a job run."""
    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj


def send_run_notification(run, job):
    """Send email notification for a job run.

    Args:
        run: The Run object.
        job: The Job object associated with the run.
    """
    # Check if notifications should be sent
    notifications = job.notifications or {}
    should_send_notification = notifications.get("emails") and notifications.get(
        "statuses"
    )
    should_send_for_status = run.status.name in notifications.get("statuses", [])

    if not (should_send_notification and should_send_for_status):
        return

    try:
        # Prepare status-specific content
        status_messages = {
            "SUCCESS": {
                "title": "Job Completed Successfully",
                "summary": f"Job '{job.title}' has completed successfully.",
                "user_message": f"Great news! The job '{job.title}' has finished running and completed successfully.",
                "action": "You can review the results by clicking the button below.",
                "color": "#28a745",
            },
            "FAILED": {
                "title": "Job Failed",
                "summary": f"Job '{job.title}' has failed.",
                "user_message": f"Unfortunately, the job '{job.title}' encountered an error and could not complete.",
                "action": "Please review the details below or contact your system administrator if you need assistance.",
                "color": "#dc3545",
            },
            "PARTIAL_SUCCESS": {
                "title": "Job Completed with Errors",
                "summary": f"Job '{job.title}' completed but encountered errors.",
                "user_message": f"The job '{job.title}' has finished, but some items could not be processed.",
                "action": "Please review which items failed and take appropriate action if needed.",
                "color": "#ffc107",
            },
        }

        status_info = status_messages.get(
            run.status.name,
            {
                "title": f"Job Status: {run.status.name}",
                "summary": f"Job '{job.title}' status: {run.status.name}",
                "user_message": f"The job '{job.title}' has a status update: {run.status.name}",
                "action": "Please review the details below for more information.",
                "color": "#6c757d",
            },
        )

        subject = f"{status_info['title']}: {job.title}"

        # Generate run URL
        ui_url = current_app.config.get("SITE_UI_URL", "")
        run_url = f"{ui_url}/administration/runs/{run.id}"

        # Calculate success count for partial success
        success_count = None
        if (
            run.status.name == "PARTIAL_SUCCESS"
            and run.errored_entries
            and run.total_entries
        ):
            success_count = run.total_entries - run.errored_entries

        # Prepare template context
        template_context = {
            "job": job,
            "run": run,
            "status_info": status_info,
            "status_color": status_info["color"],
            "title": status_info["title"],
            "run_url": run_url,
            "success_count": success_count,
        }

        # Render email templates
        html_body = render_template(
            "invenio_jobs/emails/run_notification.html", **template_context
        )

        body = render_template(
            "invenio_jobs/emails/run_notification.txt", **template_context
        )

        send_email(
            {
                "subject": subject,
                "html": html_body,
                "body": body,
                "recipients": notifications.get("emails"),
                "sender": current_app.config.get("MAIL_DEFAULT_SENDER"),
                "reply_to": current_app.config.get("MAIL_DEFAULT_REPLY_TO"),
            }
        )

        current_app.logger.info(
            f"Sent {run.status.name} notification for run {run.id} to {', '.join(notifications.get('emails', []))}"
        )
    except Exception as e:
        current_app.logger.error(
            f"Failed to send email notification for run {run.id}: {e}"
        )
