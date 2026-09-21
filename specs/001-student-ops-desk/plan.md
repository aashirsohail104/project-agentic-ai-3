# Implementation Plan: Student Ops Desk

## Overview

Build the Student Ops Desk as a multi-agent system using the OpenAI Agents SDK with Gemini. The architecture follows a base agent with two specialist agents (Assignments, Careers) reached via handoffs, plus a summarizer tool. All course data comes from `courses.json` through tools. Student context is injected at runtime. Chainlit provides the browser UI with per-session memory. Full observability via hooks, custom runner, and tracing.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| OpenAI Agents SDK with OpenAI-compatible Gemini | Brief requires Gemini via OpenAI-compatible client at agent level |
| Pydantic for all data models | Type safety, validation, serialization for Ticket and tool schemas |
| courses.json as course data source | Brief requires file-based source, tool-accessible only |
| Chainlit for UI | Brief requires browser interface with per-session memory |
| Handoffs for specialists | Brief requires cloned base agent, handoff-based transfer |
| Summarizer as tool (not handoff) | Brief explicitly requires tool, Desk keeps conversation |
| Input guardrail before model | Brief requires cheap rejection of off-topic questions |
| Custom runner wrapping all runs | Brief requires request ID and elapsed time per run |
| Run-level + one specialist agent hooks | Brief requires audit trail with both hook types |

## Task List

### Phase 1: Foundation (SLICES 0-3)

#### Task 1: Project Setup & Configuration
- **Description**: Create pyproject.toml, .env.example, config module with settings and model setup
- **Acceptance criteria**:
  - [ ] `pyproject.toml` with all dependencies pinned
  - [ ] `.env.example` with GEMINI_API_KEY, OPENAI_BASE_URL, TRACING_KEY
  - [ ] `config/settings.py` loads env, validates required keys, clear error on missing
  - [ ] `config/model.py` creates OpenAI-compatible client for Gemini, no global defaults
- **Verification**: `pytest tests/unit/config/` passes; `python -c "from src.config import settings; print(settings.gemini_api_key)"` shows masked key
- **Dependencies**: None
- **Files**: `pyproject.toml`, `.env.example`, `src/config/__init__.py`, `src/config/settings.py`, `src/config/model.py`, `tests/unit/config/test_settings.py`, `tests/unit/config/test_model.py`
- **Scope**: S

#### Task 2: Typed Data Models
- **Description**: Create Pydantic models for StudentProfile, Course, Assignment, Schedule, Policies, Ticket
- **Acceptance criteria**:
  - [ ] `models/student.py`: StudentProfile with name, roll_no, course_id, tier, open_tickets
  - [ ] `models/course.py`: Course, Schedule, Policies, Assignment with all fields from brief
  - [ ] `models/ticket.py`: Ticket with category (assignment/career/admin), summary, next_step, resolved, escalate
  - [ ] All models have validation, serialization, descriptive docstrings
- **Verification**: `pytest tests/unit/models/` passes; models serialize/deserialize correctly
- **Dependencies**: Task 1
- **Files**: `src/models/__init__.py`, `src/models/student.py`, `src/models/course.py`, `src/models/ticket.py`, `tests/unit/models/`
- **Scope**: S

#### Task 3: Course Repository & courses.json
- **Description**: Create courses.json with sample data and CourseRepository class with lookup methods
- **Acceptance criteria**:
  - [ ] `data/courses.json` matches brief structure (at least one course with schedule, policies, assignments)
  - [ ] `data/repository.py`: CourseRepository with `list_courses()`, `get_course(course_id)`, `get_assignment(course_id, assignment_id)`
  - [ ] Repository raises descriptive errors for missing data (CourseNotFoundError, AssignmentNotFoundError)
  - [ ] Deleting course from JSON removes it from answers without code change
- **Verification**: `pytest tests/unit/data/` passes; manual test shows course removal works
- **Dependencies**: Task 2
- **Files**: `src/data/courses.json`, `src/data/__init__.py`, `src/data/repository.py`, `src/data/tools.py`, `tests/unit/data/`
- **Scope**: S

#### Task 4: Student Runtime Context
- **Description**: Create context injection system — StudentContext passed to runs, tools read it, never in prompt
- **Acceptance criteria**:
  - [ ] `context/runtime.py`: StudentContext dataclass, context injection via OpenAI Agents SDK `RunContextWrapper`
  - [ ] Tools access student via context, not wrapper parameter
  - [ ] Schema for profile-reading tool has no wrapper parameter
  - [ ] Grep for student name finds only constructed object
- **Verification**: `pytest tests/unit/context/` passes; tool schema inspection confirms no wrapper
- **Dependencies**: Task 2
- **Files**: `src/context/__init__.py`, `src/context/runtime.py`, `tests/unit/context/`
- **Scope**: S

#### Task 5: Base Agent with Dynamic Instructions
- **Description**: Create BaseStudentSupportAgent with Gemini config, dynamic system prompt from profile, guardrails, hooks
- **Acceptance criteria**:
  - [ ] `agents/base.py`: Base agent class, model configured at agent level (gemini-2.5-flash)
  - [ ] System prompt built at request time: greets by name, names course, terser if open_tickets >= 3
  - [ ] Three profiles → three visibly different resolved prompts
  - [ ] Prompt printable before model call
  - [ ] Input guardrail attached (stub for now)
  - [ ] Run-level hooks attached
- **Verification**: `pytest tests/unit/agents/test_base.py` passes; manual test shows dynamic prompts
- **Dependencies**: Tasks 1, 2, 3, 4
- **Files**: `src/agents/__init__.py`, `src/agents/base.py`, `src/agents/handoffs.py`, `tests/unit/agents/`
- **Scope**: M

### Checkpoint: Foundation
- [ ] All tests pass
- [ ] Application builds without errors
- [ ] Base agent answers simple question in terminal

---

### Phase 2: Core Features (SLICES 4-8)

#### Task 6: Course Lookup Tools
- **Description**: Implement tools for listing courses, fetching schedule/policies, looking up assignments
- **Acceptance criteria**:
  - [ ] `data/tools.py`: `list_courses`, `get_course_schedule`, `get_course_policies`, `get_assignment_by_id` tools
  - [ ] Tools use CourseRepository, return typed models
  - [ ] Tools only offered to base agent (not specialists unless needed)
  - [ ] Invalid course/assignment ID returns actionable error sentence
- **Verification**: `pytest tests/unit/data/test_tools.py` passes; integration test with base agent
- **Dependencies**: Tasks 3, 5
- **Files**: `src/data/tools.py`, `tests/unit/data/test_tools.py`, `tests/integration/test_base_agent_tools.py`
- **Scope**: S

#### Task 7: Assignments Specialist + Handoff
- **Description**: Create AssignmentsSpecialist cloned from base, cold/factual, handoff from base agent
- **Acceptance criteria**:
  - [ ] `agents/assignments.py`: Cloned from base, different instructions (cold/factual), same model config
  - [ ] `agents/handoffs.py`: Handoff logic transfers to assignments specialist for assignment questions
  - [ ] Handoff appears in run items; answering agent identifiable after run
  - [ ] Specialist shares base model config without restating it
- **Verification**: `pytest tests/integration/test_assignments_handoff.py` passes
- **Dependencies**: Task 5
- **Files**: `src/agents/assignments.py`, `src/agents/handoffs.py`, `tests/integration/test_assignments_handoff.py`
- **Scope**: M

#### Task 8: Careers Specialist + Handoff
- **Description**: Create CareersSpecialist cloned from base, warmer tone, handoff from base agent
- **Acceptance criteria**:
  - [ ] `agents/careers.py`: Cloned from base, different instructions (warmer), same model config
  - [ ] Handoff logic transfers to careers specialist for career questions
  - [ ] Same verification as Task 7
- **Verification**: `pytest tests/integration/test_careers_handoff.py` passes
- **Dependencies**: Task 5
- **Files**: `src/agents/careers.py`, `tests/integration/test_careers_handoff.py`
- **Scope**: M

#### Task 9: Summarizer Tool
- **Description**: Create Summarizer tool that condenses long policy answers to 3 lines; Desk calls it, keeps conversation
- **Acceptance criteria**:
  - [ ] `tools/summarizer.py`: Summarizer tool with input (text), output (3-line summary)
  - [ ] Desk (base agent) calls tool, not handoff
  - [ ] Final message after summarization comes from Desk in its own voice
  - [ ] Can explain why tool vs handoff
- **Verification**: `pytest tests/unit/tools/test_summarizer.py` passes; integration test
- **Dependencies**: Task 5
- **Files**: `src/tools/summarizer.py`, `tests/unit/tools/test_summarizer.py`, `tests/integration/test_summarizer_tool.py`
- **Scope**: S

#### Task 10: Ticket System + close_ticket Tool
- **Description**: Implement typed Ticket model and close_ticket tool that ends run immediately
- **Acceptance criteria**:
  - [ ] `models/ticket.py`: Ticket with category (Literal), summary, next_step, resolved (bool), escalate (bool)
  - [ ] `tools/ticket_tools.py`: close_ticket tool returns Ticket, ends run (output becomes final result)
  - [ ] `type(result.final_output) is Ticket`; `resolved` used in Python `if`
  - [ ] Impossible request → SDK parsing error (not half-filled object)
- **Verification**: `pytest tests/unit/models/test_ticket.py`, `tests/unit/tools/test_ticket_tools.py`, `tests/integration/test_ticket_flow.py`
- **Dependencies**: Tasks 2, 5
- **Files**: `src/models/ticket.py`, `src/tools/ticket_tools.py`, `tests/unit/models/test_ticket.py`, `tests/unit/tools/test_ticket_tools.py`, `tests/integration/test_ticket_flow.py`
- **Scope**: M

### Checkpoint: Core Features
- [ ] End-to-end flow works: question → agent → tools/handoff → ticket
- [ ] All integration tests pass
- [ ] Specialists reachable via handoff, summarizer as tool, ticket produced

---

### Phase 3: Reliability & Observability (SLICES 9-13)

#### Task 11: Input Guardrail
- **Description**: Implement input guardrail that rejects non-course questions before Desk model runs
- **Acceptance criteria**:
  - [ ] `guardrails/input_guardrail.py`: Guardrail function checks if question relates to bootcamp
  - [ ] Off-topic → polite refusal, no billed call at Desk model
  - [ ] Exception caught in code, program doesn't crash
  - [ ] Deterministic, testable, documented
- **Verification**: `pytest tests/unit/guardrails/test_input_guardrail.py`, `tests/failure/test_guardrail_rejection.py`
- **Dependencies**: Task 5
- **Files**: `src/guardrails/input_guardrail.py`, `tests/unit/guardrails/`, `tests/failure/test_guardrail_rejection.py`
- **Scope**: S

#### Task 12: Tool Gating + Turn Ceiling
- **Description**: Implement tool gating (scholarship-only tool), turn ceiling (max turns, raises caught)
- **Acceptance criteria**:
  - [ ] `guardrails/tool_gating.py`: Tool only offered to scholarship tier (absent for regular)
  - [ ] `guardrails/turn_ceiling.py`: Max turns (e.g., 10), raises exception caught and reported
  - [ ] Same question as regular vs scholarship → different tool sets
  - [ ] Turn ceiling number documented with rationale
- **Verification**: `pytest tests/unit/guardrails/test_tool_gating.py`, `tests/unit/guardrails/test_turn_ceiling.py`, `tests/failure/test_turn_ceiling.py`
- **Dependencies**: Task 5
- **Files**: `src/guardrails/tool_gating.py`, `src/guardrails/turn_ceiling.py`, `tests/unit/guardrails/`, `tests/failure/test_turn_ceiling.py`
- **Scope**: S

#### Task 13: Hooks + Audit Trail
- **Description**: Run-level hooks (all agents), specialist-level hooks (one specialist), audit timeline
- **Acceptance criteria**:
  - [ ] `hooks/run_hooks.py`: Run hooks record ordered timeline (agent names, handoffs, tool calls)
  - [ ] `hooks/agent_hooks.py`: Agent hooks attached to exactly one specialist
  - [ ] One question → one timeline naming both agents in order
  - [ ] Agent hooks go quiet at handoff moment (explained in code)
- **Verification**: `pytest tests/unit/hooks/`, `tests/integration/test_audit_trail.py`
- **Dependencies**: Tasks 5, 7, 8
- **Files**: `src/hooks/__init__.py`, `src/hooks/run_hooks.py`, `src/hooks/agent_hooks.py`, `src/hooks/audit.py`, `tests/unit/hooks/`, `tests/integration/test_audit_trail.py`
- **Scope**: M

#### Task 14: Custom Runner + Request ID + Elapsed Time
- **Description**: Custom runner wraps every run with request ID and elapsed time, registered once at startup
- **Acceptance criteria**:
  - [ ] `runner/custom_runner.py`: CustomRunner class with request ID generation, elapsed time capture
  - [ ] Registered once at startup, no agent definition changes
  - [ ] Wrapper output appears for Desk run and specialist run
- **Verification**: `pytest tests/unit/runner/`, `tests/integration/test_custom_runner.py`
- **Dependencies**: Task 5
- **Files**: `src/runner/custom_runner.py`, `tests/unit/runner/`, `tests/integration/test_custom_runner.py`
- **Scope**: S

#### Task 15: Tracing
- **Description**: Enable tracing, export under own key, one conversation = one trace
- **Acceptance criteria**:
  - [ ] `tracing/setup.py`: Tracing configuration with custom exporter
  - [ ] Single student conversation appears as one trace
  - [ ] Can open trace, name every span, identify one unnecessary Desk call
- **Verification**: `pytest tests/integration/test_tracing.py`; manual trace inspection
- **Dependencies**: Task 5
- **Files**: `src/tracing/setup.py`, `tests/integration/test_tracing.py`
- **Scope**: S

### Checkpoint: Reliability & Observability
- [ ] Guardrails, gating, ceiling all working
- [ ] Audit trail captures full conversation
- [ ] Custom runner wraps all runs
- [ ] Tracing produces single trace per conversation

---

### Phase 4: UI & Integration (SLICES 14-16)

#### Task 16: Chainlit UI with Per-Session Memory
- **Description**: Chainlit browser interface; agent + profile built once per session; conversation memory
- **Acceptance criteria**:
  - [ ] `ui/app.py`: Chainlit app with `@cl.on_chat_start`, `@cl.on_message`
  - [ ] `ui/session.py`: Per-session state (agent, student profile, conversation history)
  - [ ] Second message refers to first → understood
  - [ ] Two browser windows → isolated history
  - [ ] Handler awaits run (not sync variant)
- **Verification**: `pytest tests/integration/test_chainlit_session.py`; manual browser test
- **Dependencies**: Tasks 5, 10, 13, 14, 15
- **Files**: `src/ui/app.py`, `src/ui/session.py`, `tests/integration/test_chainlit_session.py`
- **Scope**: M

#### Task 17: CLI Entry Point
- **Description**: Terminal entry point for demo (async main, drives agent directly)
- **Acceptance criteria**:
  - [ ] `cli.py`: Async main, accepts question, prints answer + ticket
  - [ ] Works for demo without Chainlit
- **Verification**: `python -m src.cli "What's my assignment due date?"` works
- **Dependencies**: Task 5
- **Files**: `src/cli.py`
- **Scope**: XS

---

### Phase 5: Testing & Verification (SLICES 17-18)

#### Task 18: Integration Tests
- **Description**: Complete workflow tests: base agent + tools, handoffs, ticket flow, Chainlit session
- **Acceptance criteria**:
  - [ ] Base agent + course tools
  - [ ] Base agent + assignments handoff
  - [ ] Base agent + careers handoff
  - [ ] Summarizer tool invocation
  - [ ] Complete ticket flow (resolved + escalated)
  - [ ] Chainlit session state
- **Verification**: `pytest tests/integration/` all pass
- **Dependencies**: All prior tasks
- **Files**: `tests/integration/`
- **Scope**: L

#### Task 19: Failure Path Tests
- **Description**: Tests for all failure modes: invalid course, missing context, guardrail, turn limit, model failure
- **Acceptance criteria**:
  - [ ] Invalid course ID → actionable error
  - [ ] Missing student context → clear error
  - [ ] Off-topic question → polite refusal, no model call
  - [ ] Turn ceiling → caught, reported
  - [ ] Malformed Ticket → SDK parsing error
  - [ ] Missing env config → clear startup error
- **Verification**: `pytest tests/failure/` all pass
- **Dependencies**: All prior tasks
- **Files**: `tests/failure/`
- **Scope**: M

#### Task 20: Debugging & Stabilization
- **Description**: Run full test suite, fix any failures, verify all acceptance criteria
- **Acceptance criteria**:
  - [ ] Full test suite passes (`pytest -v`)
  - [ ] No flaky tests
  - [ ] All FR-1 to FR-13 verified
  - [ ] All NFR-1 to NFR-5 verified
- **Verification**: `pytest -v` passes completely
- **Dependencies**: Tasks 18, 19
- **Files**: Various fixes
- **Scope**: M

---

### Phase 6: Review & Documentation (SLICES 19-20)

#### Task 21: Final Code Review
- **Description**: Code review for correctness, security, architecture, maintainability
- **Acceptance criteria**:
  - [ ] Correctness: all requirements met
  - [ ] Security: no secrets, safe tool boundaries, no prompt injection
  - [ ] Architecture: matches plan, clean boundaries
  - [ ] Maintainability: no unnecessary complexity, DRY where appropriate
  - [ ] Test coverage adequate
- **Verification**: Review checklist complete
- **Dependencies**: Task 20
- **Files**: N/A (review process)
- **Scope**: M

#### Task 22: Simplification
- **Description**: Remove unnecessary abstractions, duplicated code, over-engineering
- **Acceptance criteria**:
  - [ ] No unused modules
  - [ ] No premature abstractions
  - [ ] Agent prompts not overly complicated
  - [ ] No duplicated agent configuration
- **Verification**: Code review confirms simplification
- **Dependencies**: Task 21
- **Files**: Various
- **Scope**: S

#### Task 23: Documentation
- **Description**: Create README, setup instructions, architecture docs, troubleshooting
- **Acceptance criteria**:
  - [ ] README: install, configure Gemini, run tests, start Chainlit, understand architecture
  - [ ] Architecture doc: agent/handoff/ticket/hook/tracing docs
  - [ ] Testing doc: how to run tests, add tests
  - [ ] Troubleshooting: common issues
- **Verification**: Another developer can follow README to working system
- **Dependencies**: Task 22
- **Files**: `README.md`, `docs/architecture.md`, `docs/testing.md`, `docs/troubleshooting.md`
- **Scope**: M

#### Task 24: Final Verification
- **Description**: Complete final acceptance gate checklist
- **Acceptance criteria**:
  - [ ] All 34 final acceptance gates satisfied
  - [ ] Clean git history with spec before code
  - [ ] Demo works: one clean conversation, one trace, one ticket
- **Verification**: Manual verification of all gates
- **Dependencies**: Task 23
- **Files**: N/A
- **Scope**: S

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI Agents SDK API changes | High | Pin versions; use stable APIs; test early |
| Gemini OpenAI-compatible endpoint issues | High | Test model integration first (Task 1); have fallback config |
| Chainlit session state complexity | Medium | Build session management early (Task 16); test isolation thoroughly |
| Handoff context transfer | Medium | Design handoff input schema early; test with real conversations |
| Tracing integration | Low | Use SDK built-in tracing; configure exporter late |
| Turn ceiling / tool gating edge cases | Medium | Write failure tests early; define clear behaviors |

## Open Questions

1. Exact turn ceiling number (default 10, need rationale)
2. Which tool is scholarship-only? (close_ticket or priority tool)
3. Chainlit persistence: in-memory OK for demo?
4. Tracing export: console + file sufficient?
5. Course data: extend beyond brief example or keep minimal?

---

*Plan approved for implementation. Proceed to Task 1.*