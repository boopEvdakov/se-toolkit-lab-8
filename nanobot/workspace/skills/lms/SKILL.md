---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use LMS MCP tools to query live data from the Learning Management System backend.

## Available Tools

- `lms_health` — Check if the LMS backend is healthy and report the item count
- `lms_labs` — List all labs available in the LMS
- `lms_learners` — List all learners registered in the LMS
- `lms_pass_rates` — Get pass rates (avg score and attempt count per task) for a lab
- `lms_timeline` — Get submission timeline (date + submission count) for a lab
- `lms_groups` — Get group performance (avg score + student count per group) for a lab
- `lms_top_learners` — Get top learners by average score for a lab
- `lms_completion_rate` — Get completion rate (passed / total) for a lab
- `lms_sync_pipeline` — Trigger the LMS sync pipeline

## Strategy

### When user asks about scores, pass rates, completion, groups, timeline, or top learners WITHOUT naming a lab:

1. Call `lms_labs` first to get the list of available labs
2. If multiple labs are available, use the `structured-ui` skill to present a choice to the user
3. Use each lab's `title` field as the user-facing label in the choice UI
4. Pass the lab's `lab` identifier (e.g., `lab-01`) to the tool when the user selects

### When user asks "what can you do?":

Explain that you can query live data from the LMS backend:
- Check backend health and data status
- List available labs and learners
- Get pass rates, completion rates, timelines for specific labs
- Show group performance and top learners
- Trigger data sync if needed

### Response formatting:

- Format percentages with one decimal place (e.g., `89.1%`)
- Show counts as integers
- Present tabular data in a readable format
- Keep responses concise but informative

### Lab selection:

- When a lab parameter is needed but not provided, call `lms_labs` first
- Present labs using their `title` field as labels (e.g., "Lab 01 – Products, Architecture & Roles")
- Pass the `lab` field value (e.g., `lab-01`) to tools

## Examples

**User:** "Show me the scores"
**You:** Call `lms_labs` → present choice UI with lab options → after selection call `lms_pass_rates`

**User:** "Which lab has the lowest pass rate?"
**You:** Call `lms_labs` → call `lms_completion_rate` for each lab → compare and report

**User:** "Is the backend working?"
**You:** Call `lms_health` → report status and item count
