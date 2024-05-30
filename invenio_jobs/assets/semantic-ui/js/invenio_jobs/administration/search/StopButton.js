// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { http } from "react-invenio-forms";
import { Button, Icon } from "semantic-ui-react";

export const StopButton = ({ stopURL, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    await http.post(stopURL).catch((error) => {
      if (error.response) {
        onError(error.response.data);
      } else {
        onError(error);
      }
    });
    setLoading(false);
  };

  return (
    <Button
      fluid
      className="error outline"
      size="medium"
      onClick={handleClick}
      loading={loading}
      icon
      labelPosition="left"
    >
      <Icon name="stop" />
      {i18next.t("Stop")}
    </Button>
  );
};

StopButton.propTypes = {
  stopURL: PropTypes.string.isRequired,
  onError: PropTypes.func.isRequired,
};
