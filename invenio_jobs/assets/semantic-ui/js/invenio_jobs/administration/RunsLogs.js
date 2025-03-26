import React, { Component } from "react";
import PropTypes from "prop-types";
import { Label, Container, Divider, Grid, Header, Icon, List, Message, Segment } from "semantic-ui-react";
import { http } from "react-invenio-forms";
import { withCancel, ErrorMessage } from "react-invenio-forms";
import { DateTime } from "luxon";

export class RunsLogs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      logs: this.props.logs,
      run: this.props.run,
      sort: this.props.sort,
      runDuration: this.props.runDuration,
    };
  }

  fetchLogs = async (runId, sort) => {
    try {
      const searchAfterParams = (sort || []).map((value) => `search_after=${value}`).join("&");
      this.cancellableFetch = withCancel(
        http.get(`/api/logs/jobs?q=${runId}&${searchAfterParams}`)
      );
      const response = await this.cancellableFetch.promise;
      if (response.status !== 200) {
        throw new Error(`Failed to fetch logs: ${response.statusText}`);
      }

      const formattedLogs = response.data.hits.hits.map((log) => ({
        ...log,
        formatted_timestamp: DateTime.fromISO(log.timestamp).toFormat("yyyy-MM-dd HH:mm"),
      }));
      const newSort = response.data.hits.sort;

      this.setState((prevState) => ({
        logs: [...prevState.logs, ...formattedLogs],
        error: null,
        sort: newSort || prevState.sort, // Update sort only if newSort exists
      })); // Append logs and clear error
    } catch (err) {
      console.error("Error fetching logs:", err);
      this.setState({ error: err.message });
    }
  };

  getDurationInMinutes(startedAt, finishedAt) {
    if (!startedAt) return 0;

    const start = DateTime.fromISO(startedAt);
    const end = finishedAt
      ? DateTime.fromISO(finishedAt)
      : DateTime.now();

    const duration = end.diff(start, "minutes").minutes;

    return Math.floor(duration);
  }

  formatDatetime(timestamp) {
    if (!timestamp) return null;

    return DateTime.fromISO(timestamp).toFormat("yyyy-MM-dd HH:mm");
  }

  checkRunStatus = async (runId, jobId) => {
    try {
      this.cancellableFetch = withCancel(
        http.get(`/api/jobs/${jobId}/runs/${runId}`)
      );
      const response = await this.cancellableFetch.promise;
      if (response.status !== 200) {
        throw new Error(`Failed to fetch run status: ${response.statusText}`);
      }

      const run = response.data;
      run.formatted_started_at = this.formatDatetime(run.started_at);
      const runDuration = this.getDurationInMinutes(run.started_at, run.finished_at);
      this.setState({ run: run, runDuration: runDuration });
      if (run.status === "SUCCESS" || run.status === "FAILED" || run.status === "PARTIAL_SUCCESS") {
        clearInterval(this.logsInterval); // Stop fetching logs if run finihsed
      }
    } catch (err) {
      console.error("Error checking run status:", err);
      this.setState({ error: err.message });
    }
  };

  componentDidMount() {
    this.logsInterval = setInterval(async () => {
      const { run, sort } = this.state;
      if (run.status === "RUNNING") {
        await this.fetchLogs(run.id, sort); // Fetch logs only if the run is running
        await this.checkRunStatus(run.id, run.job_id); // Check the run status
      }
    }, 2000);
  }

  componentWillUnmount() {
    clearInterval(this.logsInterval);
  }

  render() {
    const { error, logs, run, runDuration, sort } = this.state;
    const levelClassMapping = {
      DEBUG: "",
      INFO: "primary",
      WARNING: "warning",
      ERROR: "negative",
      CRITICAL: "negative",
    };

    const getClassForLogLevel = (level) => levelClassMapping[level] || "";
    return (
      <Container>
      <Header as="h2" className="mt-20">
        {run.title}
      </Header>
      <Divider />
      {error && (
        <Message negative>
        <Message.Header>Error Fetching Logs</Message.Header>
        <p>{error}</p>
        </Message>
      )}
      <Grid celled>
        <Grid.Row>
        <Grid.Column width={3}>
          <Header as="h4" color="grey">
          Job run
          </Header>
          <List>
          <List.Item>
            <Icon
            name={
              run.status === "SUCCESS"
              ? "check circle"
              : run.status === "FAILED"
                ? "times circle"
                : run.status === "RUNNING"
                ? "spinner"
                : run.status === "PARTIAL_SUCCESS"
                  ? "exclamation circle"
                  : "clock outline"
            }
            color={
              run.status === "SUCCESS"
              ? "green"
              : run.status === "FAILED"
                ? "red"
                : run.status === "RUNNING"
                ? "blue"
                : run.status === "PARTIAL_SUCCESS"
                  ? "orange"
                  : "grey"
            }
            />
            <List.Content>
            {run.formatted_started_at ? (
              <>
              <p>
                <strong>{run.formatted_started_at}</strong>
              </p>
              <p className="description">{runDuration} mins</p>
              </>
            ) : (
              <p className="description">Not yet started</p>
            )}
                  {run.message && (
        <Label basic
          color={
            run.status === "SUCCESS"
              ? "green"
              : run.status === "FAILED"
              ? "red"
              : run.status === "PARTIAL_SUCCESS"
              ? "orange"
              : "blue"
          }
        >
        <p>{run.message}</p>
        </Label>
      )}
            </List.Content>
          </List.Item>
          </List>
        </Grid.Column>
        <Grid.Column className="log-table" width={13}>
          <Segment>
            {logs.map((log, index) => (
              <div key={index} className={`log-line ${log.level.toLowerCase()}`}>
                <span className="log-timestamp">[{log.formatted_timestamp}]</span>{" "}
                <span className={getClassForLogLevel(log.level)}>{log.level}</span>{" "}
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </Segment>
        </Grid.Column>
        </Grid.Row>
      </Grid>
      </Container>
    );
  }
}

RunsLogs.propTypes = {
  run: PropTypes.object.isRequired,
  logs: PropTypes.array.isRequired,
  runDuration: PropTypes.number.isRequired,
  sort: PropTypes.array.isRequired,
};
