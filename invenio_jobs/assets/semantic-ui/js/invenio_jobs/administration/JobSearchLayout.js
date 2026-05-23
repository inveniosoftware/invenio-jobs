/*
 * SPDX-FileCopyrightText: 2024 CERN.
 * SPDX-License-Identifier: MIT
 */

import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import PropTypes from "prop-types";
import React, { Component } from "react";

export class JobSearchLayout extends Component {
  render() {
    const { config, appName } = this.props;
    return (
      <SearchAppResultsPane
        layoutOptions={config.layoutOptions}
        appName={appName}
      />
    );
  }
}

JobSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

JobSearchLayout.defaultProps = {
  appName: "",
};
