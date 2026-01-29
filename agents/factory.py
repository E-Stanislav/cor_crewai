import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"
from typing import Optional, List, Dict, Callable
from crewai import Agent


def create_manager_agent(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    """Manager — единственный агент с инструментами и делегированием."""
    backstory_text = "Ты технический руководитель DWH команды. {} Твоя задача - координировать работу агентов и делегировать задачи. Всегда отвечай на русском языке.".format(
        f"Проект находится по пути: {project_path}" if project_path else "Ты координируешь работу по проекту"
    )
    return Agent(
        role="Технический руководитель DWH команды",
        goal="Координировать работу DWH команды. Читай файлы ОДИН раз и передавай содержимое агентам в задаче. НЕ делегируй чтение файлов — читай сам и передавай контент. Отвечай на русском.",
        backstory=backstory_text,
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or [],
        max_iter=10,
        max_rpm=20
    )


def create_python_developer(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    """Python Developer — работает с контекстом от Manager, без своих tools."""
    _ = project_path
    _ = tools  # Не используем — получает контент от Manager
    return Agent(
        role="Python Developer",
        goal="Разрабатывать качественный Python код для DWH решений на основе предоставленного контекста. Отвечай на русском языке.",
        backstory="Ты опытный Python разработчик специализирующийся на DWH, ETL процессах и обработке больших данных. Знаешь pandas, numpy, airflow, dbt. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=False,  # Не делегирует дальше
        tools=[],  # Не читает файлы сам
        max_iter=5
    )


def create_sql_developer(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    """SQL Developer — работает с контекстом от Manager, без своих tools."""
    _ = project_path
    _ = tools
    return Agent(
        role="SQL Developer",
        goal="Писать оптимизированные SQL запросы и модели данных на основе предоставленного контекста. Отвечай на русском языке.",
        backstory="Ты эксперт по SQL и дизайну баз данных. Знаешь PostgreSQL, Snowflake, MySQL, BigQuery. Специализируешься на OLAP системах и моделировании данных. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=False,
        tools=[],
        max_iter=5
    )


def create_architect(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    """Architect — работает с контекстом от Manager, без своих tools."""
    _ = project_path
    _ = tools
    return Agent(
        role="Data Warehouse Architect",
        goal="Проектировать архитектуру DWH систем на основе предоставленного контекста. Отвечай на русском языке.",
        backstory="Ты архитектор хранилищ данных с многолетним опытом. Знаешь методологии Data Vault, Kimball, Inmon. Эксперт в ETL/ELT процессах. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=False,
        tools=[],
        max_iter=5
    )


def create_tester(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    """QA Tester — работает с контекстом от Manager, без своих tools."""
    _ = project_path
    _ = tools
    return Agent(
        role="QA Tester",
        goal="Обеспечивать качество кода и данных через тестирование на основе предоставленного контекста. Отвечай на русском языке.",
        backstory="Ты QA инженер специализирующийся на тестировании DWH и data pipelines. Знаешь pytest, dbt tests, data quality checks. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=False,
        tools=[],
        max_iter=5
    )


def create_researcher(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    """Researcher — может читать файлы, но не делегирует."""
    backstory_text = "Ты опытный исследователь кода. {} и находишь лучшие решения. Всегда отвечай на русском языке.".format(
        f"Проект находится по пути: {project_path}" if project_path else "Ты анализируешь предоставленный код"
    )
    return Agent(
        role="Исследователь",
        goal="Анализировать код проекта и находить решения. Читай только указанные файлы, не сканируй весь проект. Отвечай на русском языке.",
        backstory=backstory_text,
        verbose=verbose,
        llm=llm,
        allow_delegation=False,  # Не делегирует
        tools=tools or [],  # Может читать файлы
        max_iter=5
    )


def create_dwh_agents(
    llm_factory: Callable[[float], object],
    project_path: Optional[str] = None,
    tools: Optional[List] = None,
    verbose: bool = True,
    temperatures: Optional[Dict[str, float]] = None
) -> Dict[str, Agent]:
    """Создаёт всех агентов DWH команды с индивидуальными температурами.
    
    Архитектура оптимизирована для экономии токенов:
    - Manager: имеет tools, читает файлы, делегирует задачи с контекстом
    - Researcher: имеет tools, читает файлы, НЕ делегирует
    - Остальные: НЕ имеют tools, получают контент от Manager в задаче
    """
    default_temps = {
        "manager": 0.4,
        "researcher": 0.6,
        "architect": 0.7,
        "python_dev": 0.3,
        "sql_dev": 0.2,
        "tester": 0.4,
    }
    
    temps = {**default_temps, **(temperatures or {})}
    
    return {
        "manager": create_manager_agent(llm_factory(temps["manager"]), project_path, tools, verbose),
        "researcher": create_researcher(llm_factory(temps["researcher"]), project_path, tools, verbose),
        # Остальные агенты без tools — получают контекст от Manager
        "python_dev": create_python_developer(llm_factory(temps["python_dev"]), project_path, None, verbose),
        "sql_dev": create_sql_developer(llm_factory(temps["sql_dev"]), project_path, None, verbose),
        "architect": create_architect(llm_factory(temps["architect"]), project_path, None, verbose),
        "tester": create_tester(llm_factory(temps["tester"]), project_path, None, verbose),
    }
