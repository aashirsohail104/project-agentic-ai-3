# Spec: Student Ops Desk

## Objective

Build a production-quality Saylani Student Operations Desk — an AI-powered front door for student questions about a bootcamp. A student asks a question in plain language; the Desk determines whether it's about an assignment, a career question, or course administration, answers it from real course data, and closes every conversation with a structured ticket that downstream systems can file.

The Desk refuses anything unrelated to the course, knows who is asking without being told in the prompt, and every run can be audited after the fact. The implementation demonstrates specification-driven AI-agent engineering using the OpenAI Agents SDK with Gemini through an OpenAI-compatible client.

**User**: Bootcamp students seeking course information
**Success**: Student gets accurate answer from course data + typed ticket; off-topic questions politely refused; full audit trail available

## Tech Stack

- **Language**: Python 3.11+
- **Agent Framework**: OpenAI Agents SDK (with OpenAI-compatible client for Gemini)
- **Model**: gemini-2.5-flash via OpenAI-compatible endpoint
- **UI**: Chainlit (browser interface with per-session memory)
- **Data**: JSON file (courses.json) for course information
- **Tracing**: OpenAI Agents SDK built-in tracing (exported under own key)
- **Testing**: pytest
- **Environment**: python-dotenv for .env management

**Key Dependencies** (to be pinned in pyproject.toml):
- openai-agents-sdk
- chainlit
- pydantic
- python-dotenv
- pytest
- pytest-asyncio

## Commands

```bash
# Install dependencies
pip install -e .

# Run tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Lint
ruff check src tests
ruff format src tests

# Type check
mypy src

# Start Chainlit UI
chainlit run src/ui/app.py

# Run CLI demo (terminal)
python -m src.cli
```

## Project Structure

```
src/
├── config/           # Environment config, model setup, secrets
│   ├── __init__.py
│   ├── settings.py
│   └── model.py
├── models/           # Typed data models (Pydantic)
│   ├── __init__.py
│   ├── student.py    # StudentProfile
│   ├── course.py     # Course, Assignment, Schedule, Policies
│   └── ticket.py     # Ticket model
├── data/             # Course repository and tools
│   ├── __init__.py
│   ├── courses.json  # Course data source
│   ├── repository.py # CourseRepository class
│   └── tools.py      # Course lookup tools (list, fetch, assignment)
├── context/          # Student runtime context
│   ├── __init__.py
│   └── runtime.py    # StudentContext, injection logic
├── agents/           # Agent definitions
│   ├── __init__.py
│   ├── base.py       # BaseStudentSupportAgent
│   ├── assignments.py # AssignmentsSpecialist
│   ├── careers.py    # CareersSpecialist
│   └── handoffs.py   # Handoff logic
├── tools/            # Agent tools
│   ├── __init__.py
│   ├── course_tools.py      # Course lookup tools
│   ├── summarizer.py        # Summarizer tool
│   └── ticket_tools.py      # close_ticket tool
├── guardrails/       # Input guardrail, tool gating, turn ceiling
│   ├── __init__.py
│   ├── input_guardrail.py
│   ├── tool_gating.py
│   └── turn_ceiling.py
├── hooks/            # Run-level and agent-level hooks
│   ├── __init__.py
│   ├── run_hooks.py
│   ├── agent_hooks.py
│   └── audit.py
├── runner/           # Custom runner
│   ├── __init__.py
│   └── custom_runner.py
├── tracing/          # Tracing configuration
│   ├── __init__.py
│   └── setup.py
├── ui/               # Chainlit interface
│   ├── __init__.py
│   ├── app.py        # Chainlit app
│   └── session.py    # Per-session state management
└── cli.py            # Terminal entry point

tests/
├── unit/             # Unit tests (models, tools, repository, context)
├── integration/      # Integration tests (agent workflows, handoffs)
├── failure/          # Failure path tests (guardrail, turn limit, etc.)
└── conftest.py       # Pytest fixtures

.specify/memory/constitution.md
specs/001-student-ops-desk/
  ├── spec.md
  ├── plan.md
  └── tasks.md
tasks/todo.md
.env.example
README.md
pyproject.toml
```

## Code Style

- **Async-first**: All agent entry points and I/O operations are async
- **Type hints**: Full type annotations on all public functions
- **Pydantic models**: For all data crossing boundaries
- **Descriptive names**: `StudentProfile`, `CourseRepository`, `close_ticket`
- **Small functions**: Single responsibility, <50 lines
- **Docstrings**: Google-style on all public classes/functions

```python
# Example: Course lookup tool
async def get_course_schedule(course_id: str) -> CourseSchedule:
    """Fetch the schedule for a specific course.
    
    Args:
        course_id: The unique course identifier (e.g., "agentic-ai-w4")
        
    Returns:
        CourseSchedule with days, times, and timezone
        
    Raises:
        CourseNotFoundError: If course_id not in courses.json
    """
    repo = CourseRepository()
    course = await repo.get_course(course_id)
    if not course:
        raise CourseNotFoundError(f"Course {course_id} not found")
    return course.schedule
```

## Testing Strategy

- **Framework**: pytest with pytest-asyncio
- **Test locations**: `tests/unit/`, `tests/integration/`, `tests/failure/`
- **Coverage target**: >80% on pure logic (models, repository, tools, context)
- **Test pyramid**: 80% unit, 15% integration, 5% E2E
- **Test sizes**: Small (no I/O) → Medium (local DB/API) → Large (full agent runs)

**Test conventions**:
- Test state, not interactions (assert outcomes, not method calls)
- DAMP over DRY in tests (self-contained, readable)
- Prefer real implementations over mocks
- Arrange-Act-Assert pattern
- One assertion per concept
- Descriptive names: `test_rejects_off_topic_question`, `test_handoff_to_assignments_specialist`

## Boundaries

### Always Do
- Run tests before commits (`pytest -v`)
- Follow type hints and Pydantic models
- Validate all tool inputs and outputs
- Keep secrets in `.env` only
- Write tests for new behavior (TDD)
- Commit specification artifacts before code

### Ask First
- Database schema changes (not applicable — using JSON)
- Adding new external dependencies
- Changing agent model configuration
- Modifying handoff contracts
- Changing ticket schema

### Never Do
- Commit secrets, API keys, or `.env` files
- Hardcode student data in prompts or source
- Embed course knowledge in system prompts
- Replace required tools with prompt text
- Replace handoffs with if/else logic
- Remove guardrails, turn ceiling, or tracing
- Swallow errors silently
- Merge agents into one monolithic agent

## Success Criteria

| Requirement | Verification |
|-------------|--------------|
| FR-1: Gemini agent at agent level | `grep -r "set_default_openai_client" src/` returns nothing; entry point is `async def main()` |
| FR-2: Course data via tools only | Delete course from courses.json → answer changes; agent refuses invented assignment IDs |
| FR-3: Student context at runtime | Tool schema has no wrapper param; `grep -r "student_name" src/` only finds constructed object |
| FR-4: Dynamic instructions per turn | Three profiles → three different resolved prompts; prompt printable before model call |
| FR-5: Specialists via handoff from base | Answering agent identifiable in code; handoff in run items; specialists share base model config |
| FR-6: Summarizer as tool | Desk keeps conversation, speaks in own voice after summarization |
| FR-7: Typed Ticket output | `type(result.final_output) is Ticket`; `resolved` used in Python `if`; impossible request → SDK parsing error |
| FR-8: Input guardrail rejects off-topic | Polite refusal; no billed call at Desk model; exception caught in code |
| FR-9: Tool gating, close_ticket, turn ceiling | Regular vs scholarship → different tool sets; close_ticket ends run; ceiling raises and is caught |
| FR-10: Run + specialist hooks | One question → one timeline naming both agents; agent hooks go quiet at handoff |
| FR-11: Custom runner with request ID + time | Wrapper output for Desk and specialist runs; no agent file mentions runner |
| FR-12: Chainlit with per-session memory | Second message refers to first → understood; two windows → isolated history; handler awaits run |
| FR-13: One trace per conversation | Trace opened, every span named; one Desk call identified as unnecessary |

## Open Questions

1. **Chainlit session storage**: In-memory vs persistent? (Default: in-memory for demo, document how to swap)
2. **Tracing export destination**: Console, file, or external service? (Default: console + file for demo)
3. **Turn ceiling number**: What value? (Default: 10 turns, documented rationale)
3. **Course data schema**: Exact fields beyond brief example? (Extend minimally from brief)
4. **Scholarship-only tool**: Which tool is gated? (Default: `close_ticket` or a "priority support" tool)