import json
from datetime import datetime, timedelta, timezone

from invenio_jobs.utils import job_arg_json_dumper


def test_job_arg_json_dumper():
    dts = [
        (
            datetime(2025, 7, 10, 5, 0, tzinfo=timezone.utc),
            "2025-07-10T05:00:00+00:00",
        ),
        (
            datetime(2025, 7, 10, 5, 0, tzinfo=timezone(timedelta(hours=2))),
            "2025-07-10T05:00:00+02:00",
        ),
        (
            datetime(2025, 7, 10, 5, 0, tzinfo=timezone(-timedelta(hours=2))),
            "2025-07-10T05:00:00-02:00",
        ),
        (
            datetime(2025, 7, 10, 5, 0, 0, 20000, tzinfo=timezone.utc),
            "2025-07-10T05:00:00.020000+00:00",
        ),
    ]

    for dt, expected_timestamp in dts:
        example_job_args = {"since": dt}
        serialised = json.dumps(example_job_args, default=job_arg_json_dumper)
        reparsed = json.loads(serialised)

        timestamp = reparsed["since"]
        assert timestamp == expected_timestamp
        """Python <3.10 cannot parse ISO timestamps with the "Z" shorthand (instead of "+00:00"),
        so we make 100% sure we aren't sending such a timestamp to the task implementation"""
        assert "Z" not in timestamp
