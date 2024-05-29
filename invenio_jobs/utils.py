from datetime import datetime, timezone
from functools import wraps

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
    # TODO check if it's a bound task and raise a runtime error
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # TODO Add failsafe of if run doesn't exist
        run = Run.query.filter_by(task_id=self.request.id).one_or_none()
        update_run(
            run, status=RunStatusEnum.RUNNING, started_at=datetime.now(timezone.utc)
        )

        try:
            message = func(self, *args, **kwargs)
        except Exception as e:
            # TODO should we log the error in message?
            print(e)
            update_run(
                run,
                status=RunStatusEnum.FAILURE,
                finished_at=datetime.now(timezone.utc),
            )
            return
        except SystemExit:
            update_run(
                run,
                status=RunStatusEnum.TERMINATED,
                finished_at=datetime.now(timezone.utc),
            )
            return
        # TODO Don't update message like this, use signals from the task
        update_run(
            run,
            status=RunStatusEnum.SUCCESS,
            message=message,
            finished_at=datetime.now(timezone.utc),
        )

    return wrapper
