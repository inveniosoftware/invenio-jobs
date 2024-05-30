// This file is part of Invenio
// Copyright (C) 2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "react-invenio-forms";
import React from "react";

import { ErrorMessage } from "@js/invenio_administration";

export const stopRun = async (url) => {
  try {
    await http.post(url);
  } catch (error) {
    console.error(error);
    return (
      <ErrorMessage
        {...error}
        id="error"
        header="hello"
        content="errormessage"
      />
    );
  }
};
