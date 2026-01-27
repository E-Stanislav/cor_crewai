# AGENTS.md

This file provides guidelines for agentic coding assistants working on this CrewAI-based multi-agent system.

## Build/Lint/Test Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Running the Application
```bash
# Using provided script
./run.sh

# Manual run with Streamlit
streamlit run app.py

# Run with telemetry disabled (recommended for development)
CREWAI_TELEMETRY_OPT_OUT=true OTEL_SDK_DISABLED=true streamlit run app.py
```

### Testing (Not Yet Implemented)
This project currently has no test framework. To add testing:
```bash
# Install pytest (recommended)
pip install pytest pytest-cov pytest-mock

# Run all tests (once added)
pytest

# Run specific test file
pytest tests/test_crew.py

# Run single test function
pytest tests/test_crew.py::test_create_agent

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality Tools (Not Yet Implemented)
Recommended tools to add to this project:
```bash
# Install tools
pip install black ruff mypy

# Format code
black .

# Lint code
ruff check .

# Type checking
mypy crew.py app.py

# Format and lint in one command
black . && ruff check .
```

## Code Style Guidelines

### Import Order and Formatting
1. Standard library imports first
2. Third-party imports second
3. Local imports third
4. No blank lines between import blocks (current project convention)

```python
import os
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, LLM
```

### Naming Conventions
- **Functions and variables**: `snake_case`
  - `get_llm()`, `create_agents()`, `topic`, `provider`
- **Classes**: `PascalCase` (if added)
- **Constants**: `UPPER_SNAKE_CASE`
  - `CREWAI_TELEMETRY_OPT_OUT`, `LITELLM_LOG`

### Type Hints
- **Required**: All function signatures must include type hints
  ```python
  def get_llm(provider: str) -> LLM:
  def create_crew(topic: str, provider: str = "ollama") -> Crew:
  ```
- Use descriptive types from typing module when needed
- Return `None` explicitly for functions that don't return values

### String Formatting
- Use **f-strings** for all string interpolation (not `.format()` or `%`)
  ```python
  f"Провести исследование темы: {topic}"
  f"Провайдер: {provider}"
  ```

### Environment Variables
- Use `python-dotenv` with `load_dotenv(override=True)`
- Provide fallback defaults with `os.getenv("KEY", "default_value")`
- Critical variables in `.env.example`:
  - `CREWAI_TELEMETRY_OPT_OUT=true` (Required to avoid signal handler errors)
  - `OTEL_SDK_DISABLED=true` (Required for Python 3.13 compatibility)
  - `LITELLM_LOG=ERROR`

### Telemetry Configuration
- **Always disable telemetry** before importing CrewAI to avoid signal handler errors:
  ```python
  import os
  from dotenv import load_dotenv
  
  load_dotenv(override=True)
  
  os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
  os.environ["OTEL_SDK_DISABLED"] = "true"
  os.environ["LITELLM_LOG"] = "ERROR"
  
  from crewai import Agent, Task, Crew, LLM  # Import after env vars
  ```

### Error Handling
- Use `try-except` blocks with specific exceptions when possible
- Provide user-friendly error messages in Russian (since UI is in Russian)
- Raise `ValueError` for invalid user input or configuration:
  ```python
  if provider not in ["zai", "ollama", "vllm"]:
      raise ValueError(f"Unknown provider: {provider}")
  ```

### Agent Configuration
- Each agent requires: `role`, `goal`, `backstory`, `verbose`, `llm`
- **Always specify Russian language** in agent goals and backstories:
  ```python
  researcher = Agent(
      role="Исследователь",
      goal="Проводить глубокий анализ и исследование заданной темы и отвечать на русском языке",
      backstory="Ты опытный исследователь с аналитическим мышлением. Всегда отвечай на русском языке.",
      verbose=True,
      llm=llm
  )
  ```
- Set `verbose=True` for debugging, can be `False` in production

### Crew Configuration
- `agents` parameter: List all agents (order doesn't matter)
- `tasks` parameter: Define task execution order (sequential)
- Each task must specify `agent=` parameter
- `verbose=True` for detailed execution logs:
  ```python
  crew = Crew(
      agents=[researcher, writer],
      tasks=[research_task, write_task],
      verbose=True
  )
  ```

### LLM Provider Configuration
- **Zai** (default): Uses glm-4.5-air model, requires API key
- **Ollama**: Uses local models (mistral, lfm2.5-thinking, etc.)
- **vLLM**: Uses OpenAI-compatible API
- Always provide fallback values for environment variables
- Use `provider="openai"` for Ollama with OpenAI-compatible endpoint

### Documentation
- **Required**: No docstrings in current codebase (minimal approach)
- **Comments**: Keep minimal, only explain complex logic
- **UI text**: Always in Russian
- **Code comments**: Can be in English or Russian (be consistent within file)

### File Organization
- `app.py`: Streamlit UI layer only
- `crew.py`: Business logic, agents, tasks, crew orchestration
- Keep concerns separated
- Avoid mixing UI logic with agent logic

### Code Style Patterns to Follow
1. Keep functions focused and single-purpose
2. Use descriptive variable and function names
3. Avoid nested conditionals deeper than 2 levels
4. Prefer early returns over deep nesting
5. Use default parameter values for optional arguments
6. Maintain consistent indentation (4 spaces)

## Project-Specific Notes

- **Language**: Application UI and agent responses are in Russian
- **Telemetry**: Must be disabled due to Python 3.13 signal handler restrictions
- **LLM providers**: Support Zai (cloud), Ollama (local), vLLM (local)
- **Current state**: Early development, no tests or CI/CD
- **Priority**: Functionality over polish, but maintain clean code structure

## Adding New Features

When adding new agents or tasks:
1. Define agent in `create_agents()` with Russian language specification
2. Create task with clear description and expected output
3. Add agent to Crew's `agents` list
4. Add task to Crew's `tasks` list in execution order
5. Update UI in `app.py` if user interaction needed
6. Test with telemetry disabled to avoid signal handler errors
