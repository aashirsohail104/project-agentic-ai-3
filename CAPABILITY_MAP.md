# Capability Map: Student Ops Desk

| Module id | Responsibility | Depends on |
|---|---|---|
| config | Environment configuration, secrets management, model setup | — |
| models | Typed data models (StudentProfile, Course, Assignment, Ticket, etc.) | config |
| course-repo | courses.json data source and course lookup tools | models |
| student-context | Runtime student context injection and management | models |
| base-agent | Base student support agent with Gemini, dynamic instructions, guardrails, hooks | config, models, course-repo, student-context |
| assignments-specialist | Assignments specialist agent (cloned from base) | base-agent |
| careers-specialist | Careers specialist agent (cloned from base) | base-agent |
| handoffs | Handoff logic from base agent to specialists | base-agent, assignments-specialist, careers-specialist |
| summarizer-tool | Summarizer tool for condensing policy answers | base-agent |
| ticket-system | Typed Ticket model, close_ticket tool, completion logic | base-agent |
| guardrails | Input guardrail, tool gating, turn ceiling | base-agent |
| hooks-observability | Run-level hooks, specialist-level hooks, audit trail, custom runner, tracing | base-agent |
| chainlit-ui | Chainlit browser interface with per-session memory | base-agent, ticket-system, hooks-observability |

**Build order:**
config → models → course-repo → student-context → base-agent → (assignments-specialist, careers-specialist, summarizer-tool, ticket-system, guardrails) → handoffs → hooks-observability → chainlit-ui

**Notes:**
- The three specialist modules (assignments-specialist, careers-specialist, summarizer-tool) can be developed in parallel after base-agent
- hooks-observability depends on base-agent but can be developed alongside specialists
- chainlit-ui is the final integration point requiring all prior modules