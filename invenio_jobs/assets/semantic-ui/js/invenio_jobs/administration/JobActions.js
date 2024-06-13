import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Modal, Icon } from "semantic-ui-react";
import { ActionModal, ActionForm } from "@js/invenio_administration";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import ScheduleJobModal from "./ScheduleJobModal";

export class JobActions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    };
  }

  onModalTriggerClick = (e, { payloadSchema, dataName, dataActionKey }) => {
    const { resource } = this.props;
    const { modalOpen } = this.state;

    if (dataActionKey === "schedule") {
      this.setState({
        modalOpen: true,
        modalHeader: i18next.t("Schedule Job"),
        modalBody: (
          <ScheduleJobModal
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            modalOpen={modalOpen}
            data={resource}
            payloadSchema={payloadSchema}
            apiUrl={`/api/jobs/${resource.id}`}
          />
        ),
      });
    } else {
      this.setState({
        modalOpen: true,
        modalHeader: dataName,
        modalBody: (
          <ActionForm
            actionKey={dataActionKey}
            actionSchema={payloadSchema}
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
          />
        ),
      });
    }
  };

  closeModal = () => {
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
  };

  handleSuccess = () => {
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  };

  render() {
    const { actions, Element, resource } = this.props;
    const { modalOpen, modalHeader, modalBody } = this.state;
    return (
      <>
        {Object.entries(actions).map(([actionKey, actionConfig]) => {
          if (actionKey === "schedule") {
            return (
              <Element
                key={actionKey}
                onClick={this.onModalTriggerClick}
                payloadSchema={actionConfig.payload_schema}
                dataName={actionConfig.text}
                dataActionKey={actionKey}
                icon
                labelPosition="left"
              >
                <Icon name="calendar" />
                {actionConfig.text}
              </Element>
            );
          } else {
            return (
              <Element
                key={actionKey}
                onClick={this.onModalTriggerClick}
                payloadSchema={actionConfig.payload_schema}
                dataName={actionConfig.text}
                dataActionKey={actionKey}
              >
                {actionConfig.text}
              </Element>
            );
          }
        })}
        <ActionModal modalOpen={modalOpen} resource={resource}>
          {modalHeader && <Modal.Header>{modalHeader}</Modal.Header>}
          {!_isEmpty(modalBody) && modalBody}
        </ActionModal>
      </>
    );
  }
}

JobActions.propTypes = {
  resource: PropTypes.object.isRequired,
  actions: PropTypes.shape({
    text: PropTypes.string.isRequired,
    payload_schema: PropTypes.object.isRequired,
    order: PropTypes.number.isRequired,
  }),
  Element: PropTypes.node,
};

JobActions.defaultProps = {
  Element: Button,
  actions: undefined,
};
