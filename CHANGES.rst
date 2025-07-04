..
    Copyright (C) 2024 CERN.
    Copyright (C) 2024-2025 Graz University of Technology.

    Invenio-Jobs is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version v4.1.0 (released 2025-07-02)

- admin: remove flag to always show the admin panel
- services: simplify search filtering logic
- fix: LegacyAPIWarning
- fix: SADeprecationWarning

Version v4.0.0 (released 2025-06-03)

- setup: bump major dependencies
- fix: ChangedInMarshmallow4Warning

Version v3.2.0 (released 2025-05-20)

- logging: add log deletion task

Version v3.1.2 (released 2025-05-14)

- logs: fix minor bug

Version v3.1.1 (released 2025-04-30)

- logging: fix celery signal

Version v3.1.0 (released 2025-04-28)

- Add custom logging handler using contextvars and OpenSearch
- Define JobLogEntrySchema and LogContextSchema
- Support search_after pagination in log search API
- Fetch logs incrementally from UI using search_after cursor
- Add React log viewer with fade-in and scroll support
- WARNING: It's required to add the job logs index template for this feature to work correctly

Version v3.0.2 (released 2025-03-24)

- scheduler: (fix) add newly created run object to db session (sqlalchemy v2 compatibility)

Version v3.0.1 (released 2025-03-10)

- ui: rename job run button label (ux improvement)

Version v3.0.0 (released 2025-02-13)

- Promote to stable release.

Version v3.0.0.dev2 (released 2025-01-23)

Version v3.0.0.dev1 (released 2024-12-12)

- fix: alembic problem
- setup: change to reusable workflows
- setup: bump major dependencies
- tasks: use utcnow

Version v2.0.0 (released 2024-10-14)

- job types: refactor public method name (breaking change)

Version v1.1.0 (released 2024-10-10)

- webpack: bump react-searchkit

Version v1.0.0 (released 2024-09-27)

- db: change tables names
- global: add jobs registry
- interface: add job types

Version v0.5.1 (released 2024-09-19)

- fix: add compatibility layer to move to flask>=3

Version v0.5.0 (released 2024-08-22)

- bump invenio-users-resources

Version v0.4.0 (released 2024-08-22)

- package: bump react-invenio-forms (#52)

Version v0.3.4 (released 2024-08-08)

- fix: pass args to task via run

Version v0.3.3 (released 2024-08-08)

- fix: utils: only eval strings

Version 0.3.2 (released 2024-07-24)

- UI: fix schedule save
- UI: fix default queue; don't error on empty args

Version 0.3.1 (released 2024-07-11)

- services: skip index rebuilding

Version 0.3.0 (released 2024-06-20)

- UI: Added create, edit and schedule options
- fix: only show stop button when task is running
- bug: fix display of durations
- global: support Jinja templating for job args
- config: rename enabled flag
- config: disable jobs view by default

Version 0.2.0 (released 2024-06-05)

- translations: added translations folder
- scheduler: filter jobs with a schedule
- service: pass run queue to task

Version 0.1.0 (released 2024-06-04)

- Initial public release.
