// This file is part of Invenio
// Copyright (C) 2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { NotificationContext } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { http } from "react-invenio-forms";
import { RunButton } from "./RunButton";
import { withCancel } from "react-invenio-forms";

export class JobRunsHeaderComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      title: i18next.t("Job Details"),
      description: "",
      config: {},
      loading: true,
    };
  }

  componentDidMount() {
    const { jobId } = this.props;
    withCancel(
      http
        .get("/api/jobs/" + jobId)
        .then((response) => response.data)
        .then((data) => {
          this.setState({
            loading: false,
            ...(data.title && { title: data.title }),
            ...(data.description && { description: data.description }),
            ...(data.default_args && { config: data.default_args }),
          });
        })
        .catch((error) => {
          this.onError(error);
          this.setState({
            loading: false,
          });
        })
    );
  }

  static contextType = NotificationContext;

  onError = (e) => {
    const { addNotification } = this.context;
    addNotification({
      title: i18next.t("Status ") + e.status,
      content: `${e.message}`,
      type: "error",
    });
    console.error(e);
  };

  render() {
    const { title, description, config, loading } = this.state;
    const { jobId } = this.props;
    return (
      <>
        <div className="column six wide">
          <h1 className="ui header m-0">{title}</h1>
          <p className="ui grey header">{description}</p>
        </div>
        <div className="column ten wide right aligned">
          {loading ? null : (
            <RunButton jobId={jobId} config={config} onError={this.onError} />
          )}
        </div>
      </>
    );
  }
}

JobRunsHeaderComponent.propTypes = {
  jobId: PropTypes.string.isRequired,
};
