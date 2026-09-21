# Tasks: Student Ops Desk

## Phase 1: Foundation

- [ ] **Task 1**: Project Setup & Configuration
  - Acceptance: pyproject.toml, .env.example, config module with validated settings and Gemini client
  - Verify: pytest tests/unit/config/ passes; settings load correctly
  - Files: pyproject.toml, .env.example, src/config/, tests/unit/config/
  - Depends on: None

- [ ] **Task 2**: Typed Data Models
  - Acceptance: StudentProfile, Course, Assignment, Schedule, Policies, Ticket models with validation
  - Verify: pytest tests/unit/models/ passes; serialization works
  - Files: src/models/, tests/unit/models/
  - Depends on: Task 1

- [ ] **Task 3**: Course Repository & courses.json
  - Acceptance: courses.json with sample data; CourseRepository with list/get methods; errors for missing data
  - Verify: pytest tests/unit/data/ passes; manual course removal test works
  - Files: src/data/courses.json, src/data/repository.py, src/data/tools.py, tests/unit/data/
  - Depends on: Task 2

- [ ] **Task 4**: Student Runtime Context
  - Acceptance: StudentContext via RunContextWrapper; tools read from context; no wrapper param in schema
  - Verify: pytest tests/unit/context/ passes; tool schema inspection
  - Files: src/context/runtime.py, tests/unit/context/
  - Depends on: Task 2

- [ ] **Task 5**: Base Agent with Dynamic Instructions
  - Acceptance: Base agent with gemini-2.5-flash at agent level; dynamic prompt per profile; guardrail stub; run hooks
  - Verify: pytest tests/unit/agents/test_base.py passes; 3 profiles → 3 different prompts
  - Files: src/agents/base.py, src/agents/handoffs.py, tests/unit/agents/
  - Depends on: Tasks 1, 2, 3, 4

## Checkpoint: Foundation
- [ ] All tests pass
- [ ] Base agent answers in terminal

## Phase 2: Core Features

- [ ] **Task 6**: Course Lookup Tools
  - Acceptance: list_courses, get_course_schedule, get_course_policies, get_assignment_by_id tools with typed returns
  - Verify: pytest tests/unit/data/test_tools.py, tests/integration/test_base_agent_tools.py
  - Files: src/data/tools.py, tests/
  - Depends on: Tasks 3, 5

- [ ] **Task 7**: Assignments Specialist + Handoff
  - Acceptance: Cloned from base, cold/factual instructions, handoff works, shares model config
  - Verify: pytest tests/integration/test_assignments_handoff.py
  - Files: src/agents/assignments.py, src/agents/handoffs.py, tests/integration/
  - Depends on: Task 5

- [ ] **Task 8**: Careers Specialist + Handoff
  - Acceptance: Cloned from base, warmer instructions, handoff works, shares model config
  - Verify: pytest tests/integration/test_careers_handoff.py
  - Files: src/agents/careers.py, tests/integration/
  - Depends on: Task 5

- [ ] **Task 9**: Summarizer Tool
  - Acceptance: Tool condenses to 3 lines; Desk calls tool, keeps conversation, speaks in own voice
  - Verify: pytest tests/unit/tools/test_summarizer.py, tests/integration/test_summarizer_tool.py
  - Files: src/tools/summarizer.py, tests/
  - Depends on: Task 5

- [ ] **Task 10**: Ticket System + close_ticket Tool
  - Acceptance: Typed Ticket model; close_ticket ends run; type(result.final_output) is Ticket; resolved used in if
  - Verify: pytest tests/unit/models/test_ticket.py, tests/unit/tools/test_ticket_tools.py, tests/integration/test_ticket_flow.py
  - Files: src/models/ticket.py, src/tools/ticket_tools.py, tests/
  - Depends on: Tasks 2, 5

## Checkpoint: Core Features
- [ ] End-to-end flow works
- [ ] All integration tests pass

## Phase 3: Reliability & Observability

- [ ] **Task 11**: Input Guardrail
  - Acceptance: Rejects off-topic before model; polite refusal; no billed call; exception caught
  - Verify: pytest tests/unit/guardrails/test_input_guardrail.py, tests/failure/test_guardrail_rejection.py
  - Files: src/guardrails/input_guardrail.py, tests/
  - Depends on: Task 5

- [ ] **Task 12**: Tool Gating + Turn Ceiling
  - Acceptance: Scholarship-only tool absent for regular; turn ceiling (10) raises caught exception
  - Verify: pytest tests/unit/guardrails/test_tool_gating.py, test_turn_ceiling.py, tests/failure/test_turn_ceiling.py
  - Files: src/guardrails/tool_gating.py, src/guardrails/turn_ceiling.py, tests/
  - Depends on: Task 5

- [ ] **Task 13**: Hooks + Audit Trail
  - Acceptance: Run hooks timeline all agents; agent hooks on one specialist; hooks quiet at handoff
  - Verify: pytest tests/unit/hooks/, tests/integration/test_audit_trail.py
  - Files: src/hooks/, tests/
  - Depends on: Tasks 5, 7, 8

- [ ] **Task 14**: Custom Runner + Request ID + Elapsed Time
  - Acceptance: CustomRunner wraps runs; request ID + elapsed time; registered once; no agent changes
  - Verify: pytest tests/unit/runner/, tests/integration/test_custom_runner.py
  - Files: src/runner/custom_runner.py, tests/
  - Depends on: Task 5

- [ ] **Task 15**: Tracing
  - Acceptance: One trace per conversation; spans named; one unnecessary Desk call identified
  - Verify: pytest tests/integration/test_tracing.py; manual trace inspection
  - Files: src/tracing/setup.py, tests/integration/
  - Depends on: Task 5

## Checkpoint: Reliability & Observability
- [ ] All guardrails, gating, ceiling working
- [ ] Audit trail captures full conversation
- [ ] Custom runner + tracing operational

## Phase 4: UI & Integration

- [ ] **Task 16**: Chainlit UI with Per-Session Memory
  - Acceptance: @cl.on_chat_start builds agent+profile once; session memory; windows isolated; handler awaits run
  - Verify: pytest tests/integration/test_chainlit_session.py; manual 2-window test
  - Files: src/ui/app.py, src/ui/session.py, tests/integration/
  - Depends on: Tasks 5, 10, 13, 14, 15

- [ ] **Task 17**: CLI Entry Point
  - Acceptance: Async main; drives agent; prints answer + ticket
  - Verify: python -m src.cli "question" works
  - Files: src/cli.py
  - Depends on: Task 5

## Phase 5: Testing & Verification

- [ ] **Task 18**: Integration Tests
  - Acceptance: All workflows tested (tools, handoffs, summarizer, ticket, Chainlit)
  - Verify: pytest tests/integration/ all pass
  - Files: tests/integration/
  - Depends on: All prior

- [ ] **Task 19**: Failure Path Tests
  - Acceptance: Invalid course, missing context, guardrail, turn limit, malformed ticket, missing env all tested
  - Verify: pytest tests/failure/ all pass
  - Files: tests/failure/
  - Depends on: All prior

- [ ] **Task 20**: Debugging & Stabilization
  - Acceptance: Full suite passes; no flaky tests; all FR/NFR verified
  - Verify: pytest -v passes completely
  - Files: Various fixes
  - Depends on: Tasks 18, 19

## Phase 6: Review & Documentation

- [ ] **Task 21**: Final Code Review
  - Acceptance: Correctness, security, architecture, maintainability, coverage all pass
  - Verify: Review checklist complete
  - Files: N/A
  - Depends on: Task 20

- [ ] **Task 22**: Simplification
  - Acceptance: No unused modules, no premature abstractions, clean prompts, no duplicated config
  - Verify: Code review confirms
  - Files: Various
  - Depends on: Task 21

- [ ] **Task 23**: Documentation
  - Acceptance: README (install, config, test, run, architecture), architecture.md, testing.md, troubleshooting.md
  - Verify: New developer can follow README to working system
  - Files: README.md, docs/
  - Depends on: Task 22

- [ ] **Task 24**: Final Verification
  - Acceptance: All 34 acceptance gates satisfied; clean git history; demo works
  - Verify: Manual verification of all gates
  - Files: N/A
  - Depends on: Task 23

---

**Total: 24 tasks across 6 phases**

*Next: Begin Task 1 - Project Setup & Configuration*