// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
// Copyright (C) 2025 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  Label,
  Container,
  Divider,
  Grid,
  Header,
  Icon,
  List,
  Message,
  Segment,
} from "semantic-ui-react";
import { http, withCancel } from "react-invenio-forms";
import { DateTime } from "luxon";
import { i18next } from "@translations/invenio_jobs/i18next";

/**
 * TaskGroup component - displays logs for a single task group
 * @param {Object} taskGroup - Task group containing taskId, taskName, parentTaskId, and logs
 * @param {Object} levelClass - Mapping of log levels to CSS classes
 */
const TaskGroup = ({ taskGroup, levelClass }) => (
  <div className={taskGroup.parentTaskId ? "subtask-container" : ""}>
    {taskGroup.logs.map((log) => (
      <div
        key={`${log.timestamp}-${log.level}-${log.message}`}
        className={`log-line ${log.level.toLowerCase()}`}
      >
        <span className="log-timestamp">[{log.formatted_timestamp}]</span>{" "}
        <span className={levelClass[log.level] || ""}>{log.level}</span>{" "}
        <span className="log-message">{log.message}</span>
      </div>
    ))}
  </div>
);

TaskGroup.propTypes = {
  taskGroup: PropTypes.shape({
    taskId: PropTypes.string.isRequired,
    taskName: PropTypes.string.isRequired,
    parentTaskId: PropTypes.string,
    logs: PropTypes.array.isRequired,
  }).isRequired,
  levelClass: PropTypes.object.isRequired,
};

export class RunsLogs extends Component {
  constructor(props) {
    super(props);

    const { logs, run, sort, warnings } = props;

    const formattedLogs = logs.map((log) => ({
      ...log,
      formatted_timestamp: DateTime.fromISO(log.timestamp).toFormat(
        "yyyy-MM-dd HH:mm"
      ),
    }));

    this.state = {
      error: null,
      logs: formattedLogs,
      run,
      sort,
      warnings: warnings || [],
      runDuration: this.getDurationInMinutes(run.started_at, run.finished_at),
      formatted_started_at: this.formatDatetime(run.started_at),
    };

    // Cache for memoized log tree
    this.logTreeCache = {
      logs: null,
      tree: null,
    };
  }

  componentDidMount() {
    this.logsInterval = setInterval(async () => {
      const { run, sort } = this.state;
      if (run.status === "RUNNING") {
        await this.fetchLogs(run.id, sort);
        await this.checkRunStatus(run.id, run.job_id);
      }
    }, 2000);
  }

  componentWillUnmount() {
    clearInterval(this.logsInterval);
    this.logsFetchCancel?.cancel();
    this.statusFetchCancel?.cancel();
  }

  getLogTree() {
    const { logs } = this.state;
    // Return cached tree if logs haven't changed
    if (this.logTreeCache.logs === logs) {
      return this.logTreeCache.tree;
    }
    // Rebuild tree and update cache
    const tree = this.buildLogTree(logs);
    this.logTreeCache = { logs, tree };
    return tree;
  }

  getDurationInMinutes(startedAt, finishedAt) {
    if (!startedAt) return 0;
    const start = DateTime.fromISO(startedAt);
    const end = finishedAt ? DateTime.fromISO(finishedAt) : DateTime.now();
    return Math.floor(end.diff(start, "minutes").minutes);
  }

  formatDatetime(ts) {
    return ts ? DateTime.fromISO(ts).toFormat("yyyy-MM-dd HH:mm") : null;
  }

  buildLogTree = (logs) => {
    /**
     * Build hierarchical tree from flat log list.
     * Returns array of root tasks, each containing children tasks.
     *
     * Task hierarchy explanation:
     * - root_task_id: The top-level task in the entire execution chain.
     *                 This never changes throughout the hierarchy.
     * - parent_task_id: The immediate parent that spawned this task.
     *                   Used to identify direct parent-child relationships.
     * - task_id: The unique identifier for the current task.
     *
     * Example: If Task A spawns Task B, which spawns Task C:
     *   Task A: task_id=A, parent_task_id=null, root_task_id=A
     *   Task B: task_id=B, parent_task_id=A, root_task_id=A
     *   Task C: task_id=C, parent_task_id=B, root_task_id=A
     */
    const taskGroups = {};

    logs.forEach((log) => {
      const context = log.context || {};
      const rootTaskId = context.root_task_id || context.task_id || "unknown";
      const taskId = context.task_id || "unknown";

      // Create root group if doesn't exist
      if (!taskGroups[rootTaskId]) {
        taskGroups[rootTaskId] = {
          rootTaskId,
          taskName: context.task_name || "Root Task",
          children: {},
        };
      }

      // Create task subgroup if doesn't exist
      if (!taskGroups[rootTaskId].children[taskId]) {
        taskGroups[rootTaskId].children[taskId] = {
          taskId,
          taskName: context.task_name || "Task",
          parentTaskId: context.parent_task_id,
          logs: [],
        };
      }

      // Add log to task subgroup
      taskGroups[rootTaskId].children[taskId].logs.push(log);
    });

    return Object.values(taskGroups);
  };

  fetchLogs = async (runId, sort) => {
    try {
      const searchAfterParams = (sort || [])
        .map((value) => `search_after=${value}`)
        .join("&");

      // own cancel token for this request
      const cancellableFetch = withCancel(
        http.get(`/api/logs/jobs?q=${runId}&${searchAfterParams}`)
      );
      this.logsFetchCancel = cancellableFetch;

      const res = await cancellableFetch.promise;
      if (res.status !== 200)
        throw new Error(`Failed to fetch logs: ${res.statusText}`);

      const incoming = res.data.hits.hits.map((log) => ({
        ...log,
        formatted_timestamp: DateTime.fromISO(log.timestamp).toFormat(
          "yyyy-MM-dd HH:mm"
        ),
      }));
      const newSort = res.data.hits.sort;

      /* dedup by timestamp|level|msg combo */
      this.setState((prev) => {
        const seen = new Set(
          prev.logs.map((l) => `${l.timestamp}|${l.level}|${l.message ?? ""}`)
        );
        const unique = incoming.filter(
          (l) => !seen.has(`${l.timestamp}|${l.level}|${l.message ?? ""}`)
        );
        return {
          logs: [...prev.logs, ...unique],
          error: null,
          sort: newSort || prev.sort,
        };
      });
    } catch (err) {
      console.error("Error fetching logs:", err);
      this.setState({ error: err.message });
    }
  };

  checkRunStatus = async (runId, jobId) => {
    try {
      // own cancel token for this request
      const cancellable = withCancel(
        http.get(`/api/jobs/${jobId}/runs/${runId}`)
      );
      this.statusFetchCancel = cancellable;

      const res = await cancellable.promise;
      if (res.status !== 200)
        throw new Error(`Failed to fetch run status: ${res.statusText}`);

      const run = res.data;

      this.setState({
        run,
        runDuration: this.getDurationInMinutes(run.started_at, run.finished_at),
        formatted_started_at: this.formatDatetime(run.started_at),
      });

      if (["SUCCESS", "FAILED", "PARTIAL_SUCCESS"].includes(run.status)) {
        clearInterval(this.logsInterval);
      }
    } catch (err) {
      console.error("Error checking run status:", err);
      this.setState({ error: err.message });
    }
  };

  render() {
    const {
      error,
      logs,
      run,
      runDuration,
      formatted_started_at: formattedStartedAt,
      warnings,
    } = this.state;
    const logTree = this.getLogTree();
    const levelClass = {
      DEBUG: "",
      INFO: "primary",
      WARNING: "warning",
      ERROR: "negative",
      CRITICAL: "negative",
    };

    const statusIcon = {
      SUCCESS: { name: "check circle", color: "green" },
      FAILED: { name: "times circle", color: "red" },
      RUNNING: { name: "spinner", color: "blue" },
      PARTIAL_SUCCESS: { name: "exclamation circle", color: "orange" },
    };

    const iconProps = statusIcon[run.status] || {
      name: "clock outline",
      color: "grey",
    };

    return (
      <Container>
        {logs.length === 0 && (
          <Message info>
            <Message.Header className="mb-5">
              {i18next.t("No logs to display")}
            </Message.Header>
            {i18next.t("Possible reasons include:")}
            <Message.List>
              <Message.Item>
                {i18next.t("The job has not produced any logs yet.")}
              </Message.Item>
              <Message.Item>
                {i18next.t("Logs were deleted due to the retention policy.")}
              </Message.Item>
            </Message.List>
          </Message>
        )}
        {logs.length > 0 && (
          <>
            <Header as="h2" className="mt-20">
              {run.title}
            </Header>
            <Divider />
            {warnings.length > 0 && (
              <Message warning icon>
                <Icon name="exclamation triangle" />
                <Message.Content>
                  <Message.Header>
                    {i18next.t("Log results truncated")}
                  </Message.Header>
                  {warnings.map((warning) => (
                    <p key={warning.message}>{warning.message}</p>
                  ))}
                </Message.Content>
              </Message>
            )}
            {error && (
              <Message negative>
                <Message.Header>
                  {i18next.t("Error Fetching Logs")}
                </Message.Header>
                <p>{error}</p>
              </Message>
            )}
            <Grid celled>
              <Grid.Row>
                <Grid.Column width={3}>
                  <Header as="h4" color="grey">
                    {i18next.t("Job run")}
                  </Header>
                  <List>
                    <List.Item>
                      <Icon name={iconProps.name} color={iconProps.color} />
                      <List.Content>
                        {formattedStartedAt ? (
                          <>
                            <p>
                              <strong>{formattedStartedAt}</strong>
                            </p>
                            <p className="description">
                              {runDuration} {i18next.t("mins")}
                            </p>
                          </>
                        ) : (
                          <p className="description">
                            {i18next.t("Not yet started")}
                          </p>
                        )}
                        {/* Only show run.message for non-error statuses */}
                        {run.message &&
                          run.status !== "FAILED" &&
                          run.status !== "PARTIAL_SUCCESS" && (
                            <Label basic color={iconProps.color}>
                              {run.message}
                            </Label>
                          )}
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>
                <Grid.Column className="job-log-table" width={13}>
                  {/* Display error message for failed jobs */}
                  {(run.status === "FAILED" ||
                    run.status === "PARTIAL_SUCCESS") && (
                    <Message negative icon>
                      <Icon name="times circle" />
                      <Message.Content>
                        <Message.Header>
                          {run.status === "FAILED"
                            ? i18next.t("Job failed")
                            : i18next.t("Job partially succeeded")}
                        </Message.Header>
                        {run.message && <pre>{run.message}</pre>}
                        {logs.filter((log) => log.level === "ERROR").length >
                          0 && (
                          <p className="text-muted">
                            {logs.filter((log) => log.level === "ERROR").length}{" "}
                            {i18next.t("error(s) found in logs below")}
                          </p>
                        )}
                      </Message.Content>
                    </Message>
                  )}
                  <Segment>
                    {logTree.map((rootGroup, groupIndex) => (
                      <div key={rootGroup.rootTaskId}>
                        {groupIndex > 0 && <Divider />}
                        {Object.values(rootGroup.children).map((taskGroup) => (
                          <TaskGroup
                            key={taskGroup.taskId}
                            taskGroup={taskGroup}
                            levelClass={levelClass}
                          />
                        ))}
                      </div>
                    ))}
                  </Segment>
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </>
        )}
      </Container>
    );
  }
}

RunsLogs.propTypes = {
  run: PropTypes.object.isRequired,
  logs: PropTypes.array.isRequired,
  sort: PropTypes.array.isRequired,
  warnings: PropTypes.array,
};

RunsLogs.defaultProps = {
  warnings: [],
};
