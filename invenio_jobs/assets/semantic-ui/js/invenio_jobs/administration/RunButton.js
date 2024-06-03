// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { http, withCancel } from "react-invenio-forms";
import {
  Button,
  Dropdown,
  DropdownMenu,
  Form,
  FormField,
  FormInput,
  TextArea,
} from "semantic-ui-react";

export class RunButton extends Component {
  constructor(props) {
    super(props);

    this.state = {
      title: "Manual run",
      config: JSON.stringify(props.config, null, "\t"),
      queue: "low",
      loading: false,
    };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  handleTitleChange = (e, { name, value }) => this.setState({ title: value });
  handleConfigChange = (e, { name, value }) => this.setState({ config: value });
  handleQueueChange = (e, { name, value }) => this.setState({ queue: value });

  handleSubmit = async () => {
    this.setState({ loading: true });

    const { jobId, onError, setRun } = this.props;
    const { title, config, queue } = this.state;

    try {
      var userConfigJSON = JSON.parse(config);
    } catch (e) {
      onError(e);
    }

    const runData = {
      title: title,
      args: userConfigJSON,
      queue: queue,
    };

    try {
      this.cancellableAction = await withCancel(
        http.post("/api/jobs/" + jobId + "/runs", runData)
      );
    } catch (error) {
      if (error.response) {
        onError(error.response.data);
      } else {
        onError(error);
      }
    }
    const response = await this.cancellableAction.promise;
    setRun(response.data?.status, response.data?.created);
    this.setState({ loading: false });
  };

  render() {
    const { title, config, queue, loading } = this.state;
    const lines = config.split(/\r?\n/).length;

    return (
      <Dropdown
        text={i18next.t("Run now")}
        icon="play"
        floating
        labeled
        button
        className="icon"
        basic
        direction="left"
      >
        <DropdownMenu>
          <Form className="p-10" onSubmit={this.handleSubmit}>
            <FormInput
              name="title"
              label="Title"
              value={title}
              onClick={(e) => e.stopPropagation()}
              onChange={this.handleTitleChange}
            />
            <FormField
              control={TextArea}
              label="Arguments"
              name="config"
              rows={lines}
              className="block min-width-max"
              value={config}
              onClick={(e) => e.stopPropagation()}
              onChange={this.handleConfigChange}
            />
            <FormField
              control={Dropdown}
              name="queue"
              label="Queue"
              selection
              value={queue}
              options={[
                { key: "celery", text: "celery", value: "celery" },
                { key: "low", text: "low", value: "low" },
              ]}
              onChange={this.handleQueueChange}
            />
            <Button type="submit" content="Run" loading={loading} />
          </Form>
        </DropdownMenu>
      </Dropdown>
    );
  }
}

RunButton.propTypes = {
  jobId: PropTypes.string.isRequired,
  config: PropTypes.object.isRequired,
  onError: PropTypes.func.isRequired,
  setRun: PropTypes.func,
};

RunButton.defaultProps = {
  setRun: (status, created) => {
    // purposeful console.log if setRun function not passed
    console.log(status, created);
  },
};
