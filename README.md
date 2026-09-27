# Student Ops Desk

AI-powered student support system for Saylani Institute — built with Chainlit, OpenAI Agents SDK, and Google Gemini.

## Overview

Student Ops Desk is an intelligent agent system that helps students with:
- **Course scheduling & policies** — Look up course details, schedules, and academic policies
- **Assignment tracking** — Find assignment due dates and requirements
- **Career guidance** — Get career advice and planning assistance
- **Ticket management** — Submit and track support requests

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Chainlit 2.12 (React-based chat UI) |
| **Agent Framework** | OpenAI Agents SDK 0.22.3 |
| **LLM** | Google Gemini 3.6 Flash (via OpenAI-compatible API) |
| **Runtime** | Python 3.12 |
| **Deployment** | Vercel (serverless Python) |
| **Testing** | pytest + pytest-asyncio |

## Architecture

```
src/
├── agents/              # Specialist agents
│   ├── base.py          # Main triage agent (with guardrails & handoffs)
│   ├── assignments.py   # Assignment specialist
│   ├── careers.py       # Career guidance specialist
│   └── handoffs.py      # Handoff definitions
├── config/              # Configuration & settings
│   ├── settings.py      # Pydantic settings (env-driven)
│   └── model.py         # Gemini client factory
├── context/             # Runtime context & student profiles
├── data/                # Course/assignment repository & tools
├── guardrails/          # Input validation, tool gating, turn ceiling
├── hooks/               # Run hooks & agent hooks
├── runner/              # Custom runner with Gemini MultiProvider
├── tracing/             # OpenAI tracing setup
├── tools/               # Function tools (ticket creation, summarization)
├── ui/                  # Chainlit UI handlers
│   ├── app.py           # @cl.on_chat_start, @cl.on_message
│   └── session.py       # Per-session state management
└── support_agents/      # Project's internal agents package (renamed from agents/)
```

## Key Features

- **Multi-agent system** with handoffs between specialist agents
- **Input guardrails** for safety (blocks PII, off-topic, injection attempts)
- **Tool gating** — only assignment agent can call assignment tools, etc.
- **Turn ceiling** — prevents runaway conversations (max 8 turns)
- **Per-session state** — student profile, course context, ticket history
- **Custom Gemini runner** — injects API key/base URL via `MultiProvider`
- **429 quota handling** — user-friendly message when Gemini free-tier exhausted

## Quick Start

### Prerequisites
- Python 3.11+
- Google AI Studio API key (Gemini)

### Local Development

```bash
# Clone
git clone https://github.com/aashirsohail104/project-agentic-ai-3.git
cd project-agentic-ai-3

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Run Chainlit UI
python -m chainlit run src/ui/app.py --port 8000 --host 127.0.0.1
# Open http://localhost:8000

# Or run CLI
python -m src.cli "What's the schedule for Agentic AI week 4?"
```

### Run Tests
```bash
pytest -v --tb=short
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `OPENAI_BASE_URL` | Yes | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `TRACING_KEY` | No | OpenAI tracing export key |
| `CHAINLIT_HOST` | No | Default: `0.0.0.0` |
| `CHAINLIT_PORT` | No | Default: `8000` |
| `LOG_LEVEL` | No | Default: `INFO` |
| `CHAINLIT_APP_ROOT` | Vercel only | Set to `/tmp` for writable filesystem |

## Deployment (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

Required Vercel Environment Variables:
- `GEMINI_API_KEY`
- `OPENAI_BASE_URL` (pre-set in project)
- `CHAINLIT_APP_ROOT=/tmp` (for writable Chainlit config)

## Project Structure

```
.
├── api/
│   └── index.py          # ASGI entry point for Vercel
├── src/                  # Main package (see Architecture above)
├── tests/                # Unit & integration tests (39 tests)
├── chainlit.md           # Welcome screen content
├── pyproject.toml        # Project config (dependencies, build, tools)
├── requirements.txt      # Pinned dependencies for Vercel
├── setup.py              # Package metadata for editable install
├── vercel.json           # Vercel deployment config
├── .python-version       # Python 3.12 for Vercel
├── .vercelignore         # Files excluded from Vercel deploy
├── .env.example          # Environment template
└── .gitignore
```

## Agent Workflow

1. **User message** → Input guardrail (safety check)
2. **Triage agent** → Classifies intent, runs tools, or hands off
3. **Specialist agents** → Assignment, Career, or Base agent
4. **Tool calls** → Course lookup, ticket creation, summarization
5. **Output** → Formatted response with citations
6. **Turn ceiling** → Enforces max 8 turns per session

## Data

Course data lives in `src/data/courses.json`:
- `agentic-ai-w4` — Agentic AI, Weekdays Batch 4
- `web-dev-w2` — Web Development, Weekdays Batch 2  
- `data-sci-w1` — Data Science, Weekdays Batch 1

Each course has: schedule, policies, and assignments.

## License

MIT