/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { UserListItemCompact, toRelativeTime } from "react-invenio-forms";
import { withState } from "react-searchkit";
import { Table } from "semantic-ui-react";
import { StatusFormatter } from "./StatusFormatter";
import { SystemRunActions } from "./SystemRunActions";

class SearchResultItemComponent extends Component {
  render() {
    const { result } = this.props;

    return (
      <Table.Row>
        <Table.Cell
          key={`run-name-${result.started_at}`}
          data-label={i18next.t("Run")}
          collapsing
          className="word-break-all"
        >
          <StatusFormatter status={result.status} />
          <a href={result.links.self}>{result.created.slice(0, 16)}</a>
        </Table.Cell>
        <Table.Cell
          key={`run-last-run-${result.status}`}
          data-label={i18next.t("Duration")}
          collapsing
          className=""
        >
          {result.started_at === null
            ? "Waiting..."
            : toRelativeTime(result.started_at, i18next.language)}
        </Table.Cell>
        <Table.Cell
          key={`run-last-run-${result.message}`}
          data-label={i18next.t("Message")}
          collapsing
          className=""
        >
          {result.title}
        </Table.Cell>
        {result.started_by ? (
          <Table.Cell
            key={`job-user-${result.started_by.id}`}
            data-label={i18next.t("Started by")}
            collapsing
            className="word-break-all"
          >
            <UserListItemCompact
              user={result.started_by}
              id={result.started_by.id}
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
        <Table.Cell collapsing>
          {result.status === "RUNNING" || result.status === "PENDING" ? (
            <SystemRunActions result={result} />
          ) : (
            ""
          )}
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
