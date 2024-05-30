// This file is part of Invenio
// Copyright (C) 2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { RunButton } from "./RunButton";
import React, { Component } from "react";
import { NotificationContext } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import { http } from "react-invenio-forms";

export class JobRunsHeaderComponent extends Component {
  constructor(props) {
    super();

    this.state = {
      jobId: props.jobId,
      title: "Job Details",
      description: "",
      config: {},
    };
  }

  componentDidMount() {
    const { jobId } = this.state;
    http
      .get("/api/jobs/" + jobId)
      .then((response) => response.data)
      .then((data) => {
        this.setState({
          ...(data.title && { title: data.title }),
          ...(data.description && { description: data.description }),
          ...(data.default_args && { config: data.default_args }),
        });
      });
  }

  static contextType = NotificationContext;

  onError = (e) => {
    const { addNotification } = this.context;
    addNotification({
      title: i18next.t("Error"),
      content: e.message,
      type: "error",
    });
    console.error(e);
  };

  render() {
    const { jobId } = this.props;
    const { title, description, config } = this.state;
    return (
      <>
        <div className="column six wide">
          <h1 className="ui header m-0">{title}</h1>
          <p className="ui grey header">{description}</p>
        </div>
        <div className="column ten wide right aligned">
          <RunButton
            jobId={jobId}
            config={config ?? {}}
            onError={this.onError}
          />
        </div>
      </>
    );
  }
}

JobRunsHeaderComponent.propTypes = {
  jobId: PropTypes.string.isRequired,
};
