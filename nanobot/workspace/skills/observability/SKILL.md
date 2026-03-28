---
name: observability
description: Use observability MCP tools for logs and traces
always: true
---

# Observability Skill

Use observability MCP tools to query VictoriaLogs and VictoriaTraces for system health monitoring.

## Available Tools

- `obs_logs` — Query VictoriaLogs for log entries
- `obs_traces` — Query VictoriaTraces for distributed traces
- `obs_health` — Check observability stack health

## Strategy

### When user asks about errors, failures, or system health:

1. Call `obs_logs` with appropriate time range and error filters
2. If traces are needed, call `obs_traces` to find related spans
3. Summarize findings concisely

### When user asks "any errors in the last hour?":

1. Call `obs_logs` with query for error level logs in the last hour
2. Report count and brief summary of any errors found
3. If no errors, confirm system is healthy

### Response formatting:

- Include timestamps for log entries
- Show error messages or stack traces when relevant
- Keep responses concise but actionable

## Examples

**User:** "any errors in the last hour?"
**You:** Call `obs_logs` with error filter → report findings

**User:** "what went wrong?"
**You:** Call `obs_logs` for recent errors → call `obs_traces` for context → summarize root cause
