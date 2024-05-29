/*
 * This file is part of Invenio.
 * Copyright (C) 2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { BoolFormatter } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { UserListItemCompact, toRelativeTime } from "react-invenio-forms";
import { withState } from "react-searchkit";
import { Popup, Table, Button, Icon } from "semantic-ui-react";
// import { RunButton } from "./RunButton";
import { StatusFormatter } from "./StatusFormatter";
import { http } from "react-invenio-forms";

class SearchResultItemComponent extends Component {
  render() {
    const { result } = this.props;

    return (
      <Table.Row>
        <Table.Cell
          key={`job-name-${result.title}`}
          data-label={i18next.t("Name")}
          collapsing
          className="word-break-all"
        >
          <a href={`/administration/jobs/${result.id}`}>{result.title}</a>
          &nbsp;
          <BoolFormatter
            tooltip={i18next.t("Inactive")}
            icon="ban"
            color="grey"
            value={result.active === false}
          />
        </Table.Cell>
        <Table.Cell
          key={`job-last-run-${result.created}`}
          data-label={i18next.t("Last run")}
          collapsing
          className=""
        >
          {result.last_run && (
            <StatusFormatter status={result.last_run.status} />
          )}
          {result.last_run ? (
            <Popup
              content={result.last_run.created}
              trigger={
                <span>
                  {toRelativeTime(result.last_run.created, i18next.language)}
                </span>
              }
            />
          ) : (
            "−"
          )}
        </Table.Cell>
        {result.last_run && result.last_run.started_by ? (
          <Table.Cell
            key={`job-user-${result.last_run.started_by.id}`}
            data-label={i18next.t("Started by")}
            collapsing
            className="word-break-all"
          >
            <UserListItemCompact
              user={result.last_run.started_by}
              id={result.last_run.started_by.id}
            />
          </Table.Cell>
        ) : (
          <Table.Cell
            key="job-user"
            data-label={i18next.t("Started by")}
            collapsing
            className="word-break-all"
          >
            System
          </Table.Cell>
        )}
        <Table.Cell
          collapsing
          key={`job-next-run${result.next_run}`}
          data-label={i18next.t("Next run")}
          className="word-break-all"
        >
          {result.active === false
            ? "Inactive"
            : toRelativeTime(result.next_run, i18next.language) ?? "−"}
        </Table.Cell>
        <Table.Cell collapsing>
          <Button
            icon
            fluid
            basic
            labelPosition="left"
            onClick={() => {
              http.post("/api/jobs/" + result.id + "/runs");
            }}
          >
            <Icon name="play" />
            Run
          </Button>
          {/* <RunButton jobId={result.id} config={result.default_args ?? {}} /> */}
        </Table.Cell>
      </Table.Row>
    );
  }
}

SearchResultItemComponent.propTypes = {
  result: PropTypes.object.isRequired,
};

SearchResultItemComponent.defaultProps = {};

export const SearchResultItemLayout = withState(SearchResultItemComponent);
