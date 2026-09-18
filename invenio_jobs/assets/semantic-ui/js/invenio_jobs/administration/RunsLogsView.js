/*
 * SPDX-FileCopyrightText: 2024 CERN.
 * SPDX-FileCopyrightText: 2025 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";

import { RunsLogs } from "./RunsLogs";

const detailsConfig = document.getElementById("runs-logs-config");

if (detailsConfig) {
  const logs = JSON.parse(detailsConfig.dataset.logs);
  const run = JSON.parse(detailsConfig.dataset.run);
  const sort = JSON.parse(detailsConfig.dataset.sort);
  const warnings = JSON.parse(detailsConfig.dataset.warnings || "[]");
  createRoot(detailsConfig).render(
    <RunsLogs logs={logs} run={run} sort={sort} warnings={warnings} />
  );
}
