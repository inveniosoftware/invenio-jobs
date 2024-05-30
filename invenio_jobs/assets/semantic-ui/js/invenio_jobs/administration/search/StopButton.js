// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import { Icon, Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { http } from "react-invenio-forms";
import PropTypes from "prop-types";

export const StopButton = ({ stopURL }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await http.post(stopURL);
      setLoading(false);
    } catch (error) {
      setLoading(false);
      // onError(error.response.data.message);
    }
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
};
