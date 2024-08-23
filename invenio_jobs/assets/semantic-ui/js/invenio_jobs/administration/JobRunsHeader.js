// This file is part of Invenio
// Copyright (C) 2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  NotificationContext,
  Loader,
  ErrorPage,
  Actions
} from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { http } from "react-invenio-forms";
import { Divider, Button, Grid, Header } from "semantic-ui-react";
import { AdminUIRoutes } from "@js/invenio_administration";
import { withCancel } from "react-invenio-forms";

export class JobRunsHeader extends Component {
  constructor(props) {
    super(props);

    this.state = {
      title: i18next.t("Job Details"),
      description: "",
      config: {},
      loading: true,
    };
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
    const {
      pid,
      columns,
      actions,
      apiEndpoint,
      idKeyPath,
      listUIEndpoint,
      resourceSchema,
      resourceName,
      displayDelete,
      displayEdit,
      uiSchema,
      data,
      error,
      loading,
    } = this.props;
    return (
      <Loader isLoading={loading}>
        <ErrorPage
          error={!_isEmpty(error)}
          errorCode={error?.response.status}
          errorMessage={error?.response.data}
        >
          <Grid stackable>
            <Grid.Row columns="2">
              <Grid.Column verticalAlign="middle">
                <Header as="h1">{data?.title}</Header>
                <Header.Subheader>{data?.description}</Header.Subheader>
              </Grid.Column>
              <Grid.Column
                verticalAlign="middle"
                floated="right"
                textAlign="right"
              >
                <Button.Group size="tiny" className="relaxed">
                  <Actions
                    title={data?.title}
                    resourceName={resourceName}
                    apiEndpoint={apiEndpoint}
                    editUrl={AdminUIRoutes.editView(
                      listUIEndpoint,
                      data,
                      idKeyPath
                    )}
                    actions={actions}
                    displayEdit={displayEdit}
                    displayDelete={displayDelete}
                    resource={data}
                    idKeyPath={idKeyPath}
                    successCallback={this.handleDelete}
                    listUIEndpoint={listUIEndpoint}
                  />
                </Button.Group>
              </Grid.Column>
            </Grid.Row>
          </Grid>
          <Divider />
        </ErrorPage>
      </Loader>
    );
  }
}

JobRunsHeader.propTypes = {
  jobId: PropTypes.string.isRequired,
};
