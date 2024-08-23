import React, { Component } from "react";
import PropTypes from "prop-types";
import { ActionFormLayout } from "@js/invenio_administration";
import ReactJson from "react-json-view";
import { Accordion, Icon, Modal } from "semantic-ui-react";

export class RunActionForm extends Component {
  state = { activeIndex: -1 };

  handleClick = (e, titleProps) => {
    const { index } = titleProps;
    const { activeIndex } = this.state;
    const newIndex = activeIndex === index ? -1 : index;

    this.setState({ activeIndex: newIndex });
  };

  render() {
    const {
      actionSchema,
      actionCancelCallback,
      actionConfig,
      actionKey,
      loading,
      formData,
      error,
      resource,
      onSubmit,
    } = this.props;
    const jsonData = JSON.parse(resource.default_args);
    const { activeIndex } = this.state;
    return (
      <>
        <Modal.Content>
          <Accordion>
            <Accordion.Title
              active={activeIndex === 0}
              index={0}
              onClick={this.handleClick}
            >
              <Icon name="dropdown" />
              Check advanced arguments
            </Accordion.Title>
            <Accordion.Content active={activeIndex === 0}>
              <ReactJson src={jsonData} name={null} />
            </Accordion.Content>
          </Accordion>
        </Modal.Content>
        <ActionFormLayout
          actionSchema={actionSchema}
          actionCancelCallback={actionCancelCallback}
          actionConfig={actionConfig}
          actionKey={actionKey}
          loading={loading}
          formData={formData}
          error={error}
          onSubmit={onSubmit}
        />
      </>
    );
  }
}

RunActionForm.propTypes = {
  resource: PropTypes.object.isRequired,
  actionSchema: PropTypes.object.isRequired,
  actionKey: PropTypes.string.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
  actionCancelCallback: PropTypes.func.isRequired,
  formFields: PropTypes.object,
  actionConfig: PropTypes.object.isRequired,
  actionPayload: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
};

RunActionForm.defaultProps = {
  formFields: {},
  actionPayload: {},
};
