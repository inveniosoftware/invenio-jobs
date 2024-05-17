/*
 * This file is part of Invenio.
 * Copyright (C) 2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

export class SystemRunActions extends Component {
  handleAction = async (action) => {
    const actionConfig = {
      deactivate: {
        label: i18next.t("Stop"),
        icon: "stop",
        notificationTitle: i18next.t("Stop"),
      },
    }[action];

    return actionConfig;
  };

  render() {
    const actionItems = [{ key: "stop", label: "Stop", icon: "stop" }];

    const generateActions = () => {
      return (
        <>
          {actionItems.map((actionItem) => (
            <Button key={actionItem.key} icon fluid basic labelPosition="left">
              <Icon name={actionItem.icon} />
              {i18next.t(actionItem.label)}
            </Button>
          ))}
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

SystemRunActions.propTypes = {};

SystemRunActions.defaultProps = {};
