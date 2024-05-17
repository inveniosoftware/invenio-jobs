/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { BoolFormatter } from "@js/invenio_administration";
import { SystemRunActions } from "./SystemRunActions";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { UserListItemCompact, toRelativeTime } from "react-invenio-forms";

class SearchResultItemComponent extends Component {
  render() {
    const { result } = this.props;

    return (
      <Table.Row>
        <Table.Cell
          key={`run-name-${result.start_time}`}
          data-label={i18next.t("Run")}
          collapsing
          className="word-break-all"
        >
          {/* status formatter here for the icon */}
          <a href={result.links.admin_self_html}>{result.start_time}</a>
        </Table.Cell>
        <Table.Cell
          key={`run-last-run-${result.status}`}
          data-label={i18next.t("Duration")}
          collapsing
          className=""
        >
          {toRelativeTime(result.start_time, i18next.language)}
        </Table.Cell>
        <Table.Cell
          key={`run-last-run-${result.message}`}
          data-label={i18next.t("Message")}
          collapsing
          className=""
        >
          {result.message}
        </Table.Cell>
        <Table.Cell
          key={`run-user-${result.started_by.user.id}`}
          data-label={i18next.t("Started by")}
          collapsing
          className="word-break-all"
        >
          <UserListItemCompact
            user={result.started_by.user}
            id={result.started_by.user.id}
          />
        </Table.Cell>
        <Table.Cell collapsing>
          <SystemRunActions />
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
