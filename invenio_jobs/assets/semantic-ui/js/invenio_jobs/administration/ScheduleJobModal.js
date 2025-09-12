// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import _get from "lodash/get";
import PropTypes from "prop-types";
import {
  Modal,
  Dropdown,
  Input,
  Button,
  Icon,
  Accordion,
  Divider,
  Message,
  Header,
} from "semantic-ui-react";
import { i18next } from "@translations/invenio_jobs/i18next";
import { Trans } from "react-i18next";
import { Formik, Form, Field } from "formik";
import { http, withCancel, ErrorMessage, TextArea } from "react-invenio-forms";
import {
  NotificationContext,
  mapFormFields,
  generateFieldProps,
  DynamicSubFormField,
  generateDynamicFieldProps,
} from "@js/invenio_administration";
import ReactJson from "@microlink/react-json-view";
import { Form as SemanticForm } from "semantic-ui-react";

export class ScheduleJobModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      error: undefined,
      jsonError: undefined,
      activeIndex: -1,
    };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  static contextType = NotificationContext;

  handleSubmit = async (values) => {
    const { addNotification } = this.context;
    this.setState({ loading: true });
    const { apiUrl, data, actionSuccessCallback, payloadSchema } = this.props;
    const { selectedOption } = values;

    // Filter out the values based on the schema for the selected option
    const selectedOptionSchema = payloadSchema[selectedOption];
    const filteredValues = Object.keys(values).reduce((acc, key) => {
      if (
        key !== "selectedOption" && // Exclude the selectedOption itself
        Object.prototype.hasOwnProperty.call(
          selectedOptionSchema?.properties,
          key
        ) // Include only fields present in the schema
      ) {
        acc[key] = values[key];
      }
      return acc;
    }, {});

    let jsonCustomArgs = {};
    if (values.custom_args != null) {
      try {
        jsonCustomArgs = JSON.parse(values.custom_args);
      } catch (error) {
        this.setState({
          loading: false,
          jsonError:
            "Invalid JSON in Custom Args field. Please fix the format.",
        });
        return;
      }
    }

    const payload = {
      ...data,
      schedule: {
        type: selectedOption,
        ...filteredValues,
      },
      run_args: {
        custom_args: jsonCustomArgs,
        ...values.args,
      },
    };

    this.cancellableAction = withCancel(http.put(apiUrl, payload));
    try {
      await this.cancellableAction.promise;
      this.setState({ loading: false });
      addNotification({
        title: i18next.t("Success"),
        content: i18next.t("Job {{title}} has been scheduled.", {
          id: data.title,
        }),
        type: "success",
      });
      actionSuccessCallback();
    } catch (error) {
      const errorMessage = error?.response?.data?.message || error?.message;
      this.setState({
        error: errorMessage,
        loading: false,
      });
    }
  };

  handleClick = (e, titleProps) => {
    const { index } = titleProps;
    const { activeIndex } = this.state;
    const newIndex = activeIndex === index ? -1 : index;

    this.setState({ activeIndex: newIndex });
  };

  render() {
    const { data, payloadSchema, actionCancelCallback } = this.props;
    const { error, loading } = this.state;

    const options = payloadSchema
      ? Object.entries(payloadSchema)
          .filter(([key, _]) => !key.includes("args"))
          .map(([key, _]) => key)
          .map((type) => ({
            key: type,
            text: type.charAt(0).toUpperCase() + type.slice(1),
            value: type,
          }))
      : [];

    const initialValues = {
      selectedOption: data?.schedule?.type || "",
      task: data.task,
      ...data.schedule,
    };

    const jsonData = JSON.parse(data?.default_args);
    const { activeIndex } = this.state;

    return (
      <Formik initialValues={initialValues} onSubmit={this.handleSubmit}>
        {(formikProps) => {
          const { values, setFieldValue, handleSubmit } = formikProps;

          return (
            <Form>
              {error && (
                <Modal.Content>
                  <ErrorMessage
                    header={i18next.t("Unable to set schedule.")}
                    content={i18next.t(error)}
                    icon="exclamation"
                    className="text-align-left"
                    negative
                  />
                </Modal.Content>
              )}
              <Modal.Content>
                <Dropdown
                  placeholder="Select a schedule type"
                  fluid
                  selection
                  options={options}
                  className="mb-10"
                  onChange={(e, { value }) =>
                    setFieldValue("selectedOption", value)
                  }
                  value={values.selectedOption}
                />
                {values.selectedOption &&
                  payloadSchema[values.selectedOption] && (
                    <>
                      {Object.keys(
                        payloadSchema[values.selectedOption].properties
                      )
                        .sort(
                          (a, b) =>
                            payloadSchema[values.selectedOption].properties[a]
                              .metadata.order -
                            payloadSchema[values.selectedOption].properties[b]
                              .metadata.order
                        )
                        .map((property) => (
                          <Field
                            key={property}
                            name={property}
                            render={({ field }) => (
                              <Input
                                {...field}
                                label={
                                  payloadSchema[values.selectedOption]
                                    .properties[property].metadata?.title
                                }
                                className="m-5"
                                type={
                                  payloadSchema[values.selectedOption]
                                    .properties[property].type === "string"
                                    ? "text"
                                    : "number"
                                }
                              />
                            )}
                          />
                        ))}
                    </>
                  )}
                <SemanticForm
                  as={Form}
                  id="action-form"
                  onSubmit={handleSubmit}
                >
                  <DynamicSubFormField
                    {...generateDynamicFieldProps(
                      "args",
                      _get(payloadSchema, "args"),
                      undefined,
                      true,
                      payloadSchema["args"],
                      formikProps,
                      payloadSchema,
                      data,
                      mapFormFields
                    )}
                    fieldSchema={_get(payloadSchema, "args")}
                  />
                  <Accordion fluid styled>
                    <Accordion.Title
                      active={activeIndex === 0}
                      index={0}
                      onClick={this.handleClick}
                    >
                      <Icon name="dropdown" />
                      {i18next.t("Advanced configuration")}
                    </Accordion.Title>
                    <Accordion.Content active={activeIndex === 0}>
                      <Header size="tiny">
                        {i18next.t("Reference configuration of this job:")}
                      </Header>
                      <ReactJson src={jsonData} name={null} />
                    </Accordion.Content>
                    <Accordion.Content active={activeIndex === 0}>
                      <Divider />
                      <Message info>
                        <Trans>
                          <b>Custom args:</b> when provided, the input below
                          will override any arguments specified above.
                        </Trans>
                      </Message>
                      <Message info>
                        <Trans>
                          <p>
                            Leaving the field empty will reset the job to the
                            default arguments.
                          </p>
                          <p>Current set custom arguments:</p>
                          <pre>
                            {JSON.stringify(
                              data?.run_args?.custom_args,
                              null,
                              2
                            )}
                          </pre>
                        </Trans>
                      </Message>
                      <TextArea
                        {...generateFieldProps(
                          "custom_args",
                          _get(payloadSchema, "custom_args"),
                          undefined,
                          true,
                          payloadSchema["custom_args"],
                          formikProps,
                          payloadSchema,
                          data,
                          mapFormFields
                        )}
                        fieldSchema={_get(payloadSchema, "custom_args")}
                      />
                    </Accordion.Content>
                    {this.state.jsonError && (
                      <Message negative>
                        <Message.Header>
                          {i18next.t("JSON Error")}
                        </Message.Header>
                        <p>{this.state.jsonError}</p>
                      </Message>
                    )}
                  </Accordion>
                </SemanticForm>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  icon="cancel"
                  onClick={actionCancelCallback}
                  content={i18next.t("Cancel")}
                  loading={loading}
                  floated="left"
                  size="medium"
                />
                <Button positive type="submit" onClick={handleSubmit}>
                  <Icon name="check" />
                  {i18next.t("Save")}
                </Button>
              </Modal.Actions>
            </Form>
          );
        }}
      </Formik>
    );
  }
}

ScheduleJobModal.propTypes = {
  modalOpen: PropTypes.bool.isRequired,
  data: PropTypes.object.isRequired,
  payloadSchema: PropTypes.object.isRequired,
  apiUrl: PropTypes.string.isRequired,
  actionCancelCallback: PropTypes.func.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
};

export default ScheduleJobModal;
