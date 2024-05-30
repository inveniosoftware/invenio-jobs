// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { http } from "react-invenio-forms";
import {
  Button,
  Dropdown,
  DropdownMenu,
  Form,
  FormInput,
} from "semantic-ui-react";

export const RunButton = ({ jobId, config, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await http.post("/api/jobs/" + jobId + "/runs");
      setLoading(false);
    } catch (error) {
      setLoading(false);
      onError(error);
    }
  };

  return (
    <Dropdown
      text={i18next.t("Run now")}
      icon="play"
      floating
      labeled
      button
      className="icon"
      basic
      closeOnBlur={false}
      direction="left"
    >
      <DropdownMenu>
        <Form className="p-10">
          {Object.keys(config).map((key) => (
            <FormInput
              key={key}
              label={key}
              defaultValue={config[key]}
              onClick={(e) => e.stopPropagation()}
            />
          ))}
          <Button
            type="submit"
            content="Run"
            onClick={handleClick}
            loading={loading}
          />
        </Form>
      </DropdownMenu>
    </Dropdown>
  );
};

RunButton.propTypes = {
  jobId: PropTypes.string.isRequired,
  config: PropTypes.object,
  onError: PropTypes.func.isRequired,
};

RunButton.defaultProps = {
  config: {},
};
