from datetime import datetime
from functools import wraps
from time import sleep

from invenio_db import db

from invenio_jobs.models import Run, RunStatusEnum


# TODO 1. Move to service? 2. Don't use kwargs?
def update_run(run, **kwargs):
    if not run:
        return
    for kw, value in kwargs.items():
        setattr(run, kw, value)
    db.session.commit()


def is_a_job(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # TODO Add failsafe of if run doesn't exist
        run = Run.query.filter_by(task_id=self.request.id).one_or_none()
        update_run(run, status=RunStatusEnum.RUNNING, started_at=datetime.now())

        try:
            message = func(self, *args, **kwargs)
        except Exception:
            # TODO should we log the error in message?
            update_run(run, status=RunStatusEnum.FAILURE)
            return

        # TODO Don't update message like this, use signals from the task
        update_run(
            run,
            status=RunStatusEnum.SUCCESS,
            message=message,
            finished_at=datetime.now(),
        )

    return wrapper
