/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { BoolFormatter } from "@js/invenio_administration";
import { SystemJobActions } from "./SystemJobActions";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table, Popup } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { UserListItemCompact, toRelativeTime } from "react-invenio-forms";

class SearchResultItemComponent extends Component {
  render() {
    const { result } = this.props;

    return (
      <Table.Row>
        <Table.Cell
          key={`job-active-${result.active}`}
          data-label={i18next.t("Active")}
          collapsing
          className=""
        >
          <BoolFormatter
            tooltip={i18next.t("Active")}
            icon="check"
            color="green"
            value={result.active === true}
          />
          <BoolFormatter
            tooltip={i18next.t("Inactive")}
            icon="ban"
            color="grey"
            value={result.active === false}
          />
        </Table.Cell>
        <Table.Cell
          key={`job-name-${result.title}`}
          data-label={i18next.t("Name")}
          collapsing
          className="word-break-all"
        >
          <a href={`/administration/jobs/${result.id}`}>{result.title}</a>
        </Table.Cell>
        <Table.Cell
          key={`job-last-run-${result.created}`}
          data-label={i18next.t("Last run")}
          collapsing
          className=""
        >
          {result.last_run && (
            <BoolFormatter
              tooltip={i18next.t("Status")}
              icon="check"
              color="green"
              value={result.last_run.status === "Success"}
            />
          )}
          {result.last_run && (
            <BoolFormatter
              tooltip={i18next.t("Status")}
              icon="ban"
              color="red"
              value={result.last_run.status === "Failed"}
            />
          )}
          {result.last_run ? (
            <Popup
              content={result.last_run.created}
              trigger={
                <div>
                  {toRelativeTime(result.last_run.created, i18next.language)}
                </div>
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
          {toRelativeTime(result.next_run, i18next.language) ?? "−"}
        </Table.Cell>
        <Table.Cell collapsing>
          <SystemJobActions runArgs={result.default_args ?? {}} />
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
