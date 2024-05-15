# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for jobs."""

from invenio_assets.webpack import WebpackThemeBundle

administration = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-jobs-search": "./js/invenio_jobs/administration/search/index.js",
                "invenio-jobs-details": "./js/invenio_jobs/administration/details/index.js",
            },
            dependencies={
                "react-invenio-forms": "^3.0.0",
                "react-searchkit": "^2.0.0",
            },
            aliases={
                "@less/invenio_jobs": "less/invenio_jobs",
                "@js/invenio_jobs": "js/invenio_jobs",
                "@translations/invenio_jobs": "translations/invenio_jobs",
            },
        ),
    },
)
