# Student Ops Desk — Constitution

## Principles

1. **Specification Before Implementation** — No source file is written until Phase 0 artifacts (constitution, spec, plan, tasks) are complete and committed. Git history is the evidence.

2. **Agent-Level Model Configuration** — The Gemini model (gemini-2.5-flash) is configured at the agent level through an OpenAI-compatible client. No global or per-run model defaults. The entry point is asynchronous.

3. **Controlled Knowledge Boundaries** — Course information lives only in `courses.json` and is accessible exclusively through tools. The agent never has course knowledge embedded in its system prompt. Student information is provided as local runtime context, never hardcoded into prompts.

4. **Safe and Predictable Tool Behavior** — Every tool has a defined input schema, output schema, authorization boundary, and error behavior. Tools are gated by student tier (scholarship vs regular). The `close_ticket` tool ends the run immediately. A turn ceiling prevents unbounded loops.

5. **Guardrails, Cost Control, Structured Completion** — An input guardrail rejects non-course questions before the model runs. Every resolved conversation produces a typed `Ticket` object. Turn limits and model ceilings are enforced. Cost is controlled through bounded turns and deliberate model settings per agent.

6. **Auditable Agent Operations** — Run-level hooks record an ordered timeline covering every agent including handoffs. Agent-level hooks attach to exactly one specialist. A custom runner wraps every run with request ID and elapsed time. Tracing produces one trace per complete student conversation.

7. **Isolated Student Sessions** — Chainlit UI maintains per-session conversation memory. Sessions never share history. Student profile and agent are built once per session, not per message.

8. **Explainability and Maintainability** — Code is written for human review. Every architectural decision is documented. The viva assumes you can explain every diff. Complexity is minimized; the simplest thing that works is preferred.

## Mandatory Constraints

- **Secrets**: All API keys and credentials live in `.env` (gitignored). `.env.example` must exist. Missing keys produce clear startup errors.
- **No Hardcoded Data**: Student names, roll numbers, course IDs, and course knowledge never appear in source code or system prompts.
- **Typed Contracts**: All data crossing agent/tool boundaries uses Pydantic models or equivalent typed schemas.
- **Error Handling**: Tools return actionable sentences for the model, never raise into the runner. Guardrail rejections are polite and cheap (no billed model call).
- **Git Provenance**: Specification artifacts committed before first implementation commit. Each meaningful slice is a separate commit.

## Quality Gates

- [ ] All 13 functional requirements (FR-1 to FR-13) have acceptance criteria and tests
- [ ] All 5 non-functional requirements (NFR-1 to NFR-5) are verified
- [ ] Unit tests pass (target: >80% coverage on pure logic)
- [ ] Integration tests pass for agent workflows, handoffs, ticket generation
- [ ] Failure-path tests pass (guardrail, turn ceiling, tool failure, model failure)
- [ ] Code review completed (correctness, security, architecture, maintainability)
- [ ] No secrets in commits, logs, or tests
- [ ] Documentation complete (README, setup, architecture, troubleshooting)

## Non-Negotiable Architecture Rules

- Base agent, Assignments specialist, and Careers specialist share a common foundation (cloned, not duplicated)
- Summarizer is a TOOL, not a handoff specialist
- Handoffs are the only path to specialists from the base agent
- Student context is injected at runtime, not compile time
- Chainlit handler awaits the run (no synchronous variant)
- Tracing exports under own key; one conversation = one trace
- Custom runner registered once at startup, no agent definition changes

## Verification Requirements

Before any implementation commit:
- [ ] `.specify/memory/constitution.md` committed
- [ ] `specs/001-student-ops-desk/spec.md` committed
- [ ] `specs/001-student-ops-desk/plan.md` committed
- [ ] `specs/001-student-ops-desk/tasks.md` committed
- [ ] Git log shows spec artifacts before code

Before declaring a task complete:
- [ ] Task acceptance criteria met
- [ ] Tests written and passing
- [ ] Build succeeds
- [ ] No uncommitted changes outside task scope

Before project completion:
- [ ] All final acceptance gates from master prompt satisfied