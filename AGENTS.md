# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-29
**Commit:** Not available
**Branch:** Not available

## OVERVIEW
CrewAI-based multi-agent DWH system with Streamlit UI. Two teams: Research (Researcher + Writer) and DWH (Manager + 5 specialists). Agents coordinate with delegation pattern and use file system tools.

## STRUCTURE
```
./
├── agents/              # DWH agent factory
├── utils/               # File system utilities & config loading
├── demo_dwh_project/   # Sample DWH project for testing
├── app.py               # Streamlit UI (2 tabs)
├── crew.py              # Business logic & orchestration
├── config.yaml          # DWH projects configuration
├── AGENTS.md            # This file
└── requirements.txt       # Python dependencies
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| UI logic | app.py | Streamlit components, session state |
| Agent creation | agents/factory.py | Factory functions for DWH agents |
| LLM/crew orchestration | crew.py | create_crew(), create_dwh_crew() |
| Config loading | utils/file_utils.py | YAML parsing, project validation |
| Project config | config.yaml | DWH project definitions |

## CONVENTIONS

**CRITICAL: Telemetry MUST be disabled before importing CrewAI**
```python
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"
```
Import order: stdlib → third-party → local (no blank lines)

**Agent language specification**: Russian in ALL agent goals and backstories

**No docstrings**: Minimal approach, only explain complex logic

## ANTI-PATTERNS (THIS PROJECT)
- NEVER import CrewAI before setting env vars (causes signal handler crash)
- NEVER mix UI logic with agent business logic
- ALWAYS specify Russian language in agent goal/backstory
- AVOID nested conditionals > 2 levels

## UNIQUE STYLES
**Factory pattern**: agents/factory.py returns Agent objects, not classes
**Manager agent**: Coordinates work, delegates to specialists
**Delegation enabled**: All agents can delegate to each other for synergy
**File tools**: DirectoryReadTool + FileReadTool passed to all DWH agents

## COMMANDS
```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run
streamlit run app.py
# or (REQUIRED for dev)
CREWAI_TELEMETRY_OPT_OUT=true OTEL_SDK_DISABLED=true streamlit run app.py
```

## NOTES
**Project state**: Early development, no tests, no CI/CD
**Missing**: pytest, pyproject.toml, .github/workflows/, code quality tools
**Demo project**: demo_dwh_project/ is a sample project, not real tests
