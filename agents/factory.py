import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"
from typing import Optional, List, Dict, Callable
from crewai import Agent


def create_manager_agent(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    backstory_text = "Ты технический руководитель DWH команды. {} Твоя задача - координировать работу агентов, делегировать задачи и обеспечивать синергию между ними. Всегда отвечай на русском языке.".format(
        f"Проект находится по пути: {project_path}" if project_path else "Ты координируешь работу по проекту"
    )
    return Agent(
        role="Технический руководитель DWH команды",
        goal="Координировать работу DWH команды, делегировать задачи подходящим агентам и обеспечивать синергию. Всегда отвечай на русском языке.",
        backstory=backstory_text,
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or []
    )


def create_python_developer(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    _ = project_path
    return Agent(
        role="Python Developer",
        goal="Разрабатывать качественный Python код для DWH решений и отвечать на русском языке. Используй доступные инструменты для чтения файлов и директорий проекта. Делегируй задачи SQL Developer если нужна работа с базой данных.",
        backstory="Ты опытный Python разработчик специализирующийся на DWH, ETL процессах и обработке больших данных. Знаешь все лучшие практики работы с pandas, numpy, airflow, dbt. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or []
    )


def create_sql_developer(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    _ = project_path
    return Agent(
        role="SQL Developer",
        goal="Писать оптимизированные SQL запросы и модели данных для хранилища данных на русском языке. Используй доступные инструменты для чтения файлов и директорий проекта. Делегируй задачи Architect если нужны архитектурные решения.",
        backstory="Ты эксперт по SQL и дизайну баз данных. Знаешь PostgreSQL, Snowflake, MySQL, BigQuery. Специализируешься на OLAP системах, хранилищах данных, оптимизации запросов и моделировании данных. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or []
    )


def create_architect(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    _ = project_path
    return Agent(
        role="Data Warehouse Architect",
        goal="Проектировать архитектуру DWH систем и обеспечивать качество решений на русском языке. Используй доступные инструменты для чтения файлов и директорий проекта. Делегируй задачи Python Developer если нужна реализация на Python.",
        backstory="Ты архитектор хранилищ данных с многолетним опытом. Знаешь методологии Data Vault, Kimball, Inmon. Эксперт в ETL/ELT процессах, data lakehouse, микросервисной архитектуре. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or []
    )


def create_tester(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    _ = project_path
    return Agent(
        role="QA Tester",
        goal="Обеспечивать качество кода и данных через тестирование и проверку на русском языке. Используй доступные инструменты для чтения файлов и директорий проекта. Делегируй задачи Python Developer если нужно написать тесты.",
        backstory="Ты QA инженер специализирующийся на тестировании DWH и data pipelines. Знаешь pytest, dbt tests, data quality checks. Умеешь находить аномалии в данных и проблемы производительности. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or []
    )


def create_researcher(llm, project_path: Optional[str] = None, tools: Optional[List] = None, verbose: bool = True) -> Agent:
    backstory_text = "Ты опытный исследователь кода. {} и находишь лучшие решения. Используй доступные инструменты для чтения файлов и директорий проекта. Делегируй задачи Python Developer если нужен анализ Python кода, или SQL Developer если нужен анализ SQL. Всегда отвечай на русском языке.".format(
        f"Проект находится по пути: {project_path}" if project_path else "Ты анализируешь предоставленный код"
    )
    return Agent(
        role="Исследователь",
        goal="Анализировать код проекта и находить решения на русском языке",
        backstory=backstory_text,
        verbose=verbose,
        llm=llm,
        allow_delegation=True,
        tools=tools or []
    )


def create_dwh_agents(
    llm_factory: Callable[[float], object],
    project_path: Optional[str] = None,
    tools: Optional[List] = None,
    verbose: bool = True,
    temperatures: Optional[Dict[str, float]] = None
) -> Dict[str, Agent]:
    """Создаёт всех агентов DWH команды с индивидуальными температурами.
    
    Args:
        llm_factory: Функция, создающая LLM с заданной температурой
        project_path: Путь к проекту
        tools: Инструменты для агентов
        verbose: Подробный вывод
        temperatures: Словарь с температурами для каждой роли
    """
    # Дефолтные температуры оптимизированы под задачи агентов
    default_temps = {
        "manager": 0.4,      # Точные решения, координация
        "researcher": 0.6,   # Анализ, поиск паттернов
        "architect": 0.7,    # Креативные архитектурные решения
        "python_dev": 0.3,   # Точный код без галлюцинаций
        "sql_dev": 0.2,      # SQL должен быть максимально точным
        "tester": 0.4,       # Точные тест-кейсы
    }
    
    temps = {**default_temps, **(temperatures or {})}
    
    return {
        "manager": create_manager_agent(llm_factory(temps["manager"]), project_path, tools, verbose),
        "python_dev": create_python_developer(llm_factory(temps["python_dev"]), project_path, tools, verbose),
        "sql_dev": create_sql_developer(llm_factory(temps["sql_dev"]), project_path, tools, verbose),
        "architect": create_architect(llm_factory(temps["architect"]), project_path, tools, verbose),
        "tester": create_tester(llm_factory(temps["tester"]), project_path, tools, verbose),
        "researcher": create_researcher(llm_factory(temps["researcher"]), project_path, tools, verbose)
    }
