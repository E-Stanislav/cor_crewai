# AGENTS Module

Factory for creating DWH team agents with delegation support.

## OVERVIEW
Creates 6 agents: Manager (coordinates), Python Dev, SQL Dev, Architect, Tester, Researcher.

## WHERE TO LOOK
| Function | Purpose |
|-----------|---------|
| create_manager_agent() | Technical lead, coordinates team |
| create_python_developer() | Python ETL/data scripts |
| create_sql_developer() | SQL queries & data models |
| create_architect() | DWH architecture design |
| create_tester() | QA & data quality checks |
| create_researcher() | Code analysis & solution finding |
| create_dwh_agents() | Creates all agents with tools |

## CONVENTIONS
- Factory functions return Agent objects
- allow_delegation=True for all agents (enables cross-agent delegation)
- Tools parameter: DirectoryReadTool + FileReadTool passed to each agent
- Russian language in all role/goal/backstory fields
