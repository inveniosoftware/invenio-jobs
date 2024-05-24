/*
 * This file is part of Invenio.
 * Copyright (C) 2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Button, Icon } from "semantic-ui-react";
import { RunButton } from "./RunButton";

export class SystemJobActions extends Component {
  handleAction = async (action) => {
    const actionConfig = {
      restore: {
        label: i18next.t("Settings"),
        icon: "cogwheel",
        notificationTitle: i18next.t("Settings"),
      },
      block: {
        label: i18next.t("Schedule"),
        icon: "calendar",
        notificationTitle: i18next.t("Schedule"),
      },
    }[action];

    return actionConfig;
  };

  render() {
    const actionItems = [
      { key: "settings", label: "Settings", icon: "cog" },
      { key: "schedule", label: "Schedule", icon: "calendar" },
    ];

    const { runArgs } = this.props.runArgs;

    const generateActions = () => {
      return (
        <>
          {actionItems.map((actionItem) => (
            <Button key={actionItem.key} icon fluid basic labelPosition="left">
              <Icon name={actionItem.icon} />
              {i18next.t(actionItem.label)}
            </Button>
          ))}
          <RunButton config={runArgs} />
        </>
      );
    };
    return (
      <div>
        <Button.Group basic widths={5} compact className="margined">
          {generateActions()}
        </Button.Group>
      </div>
    );
  }
}

SystemJobActions.propTypes = {
  runArgs: PropTypes.object.isRequired,
};

SystemJobActions.defaultProps = {};
