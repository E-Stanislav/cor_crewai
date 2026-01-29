import os
from typing import Optional, List
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool
from agents.factory import create_dwh_agents
from utils.file_utils import get_project_info, is_path_valid
from models.schemas import ResearchTeamResponse


def get_llm(provider: str) -> LLM:
    if provider == "zai":
        api_key = os.getenv("ZAI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("Для провайдера 'zai' нужно указать ZAI_API_KEY в .env")
        return LLM(
            model=os.getenv("ZAI_MODEL", "zai/zai-model"),
            api_key=api_key,
            api_base=os.getenv("ZAI_BASE_URL", "https://api.zai.ai/v1"),
            temperature=0.7
        )
    elif provider == "ollama":
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        if base.endswith("/"):
            base = base[:-1]
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return LLM(
            model=os.getenv("OLLAMA_MODEL", "mistral"),
            api_base=base,
            api_key="dummy",
            provider="openai",
            temperature=0.7
        )
    elif provider == "vllm":
        base = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
        if base.endswith("/"):
            base = base[:-1]
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return LLM(
            model=os.getenv("VLLM_MODEL", "openai/meta-llama/Llama-2-7b-chat-hf"),
            api_key=os.getenv("VLLM_API_KEY", "dummy"),
            api_base=base,
            temperature=0.7
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


def create_agents(llm, project_path: Optional[str] = None, verbose: bool = True):
    researcher = Agent(
        role="Исследователь",
        goal="Проводить глубокий анализ и исследование заданной темы и отвечать на русском языке",
        backstory="Ты опытный исследователь с аналитическим мышлением, который умеет находить и структурировать информацию. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=llm
    )
    
    writer = Agent(
        role="Писатель",
        goal="Создавать качественный контент на основе предоставленной информации на русском языке",
        backstory="Ты талантливый писатель, который превращает исследования в понятный и привлекательный текст. Всегда пиши на русском языке.",
        verbose=verbose,
        llm=llm
    )
    
    return researcher, writer


def create_crew(topic: str, provider: str = "ollama", structured_output: bool = False, verbose: bool = True) -> Crew:
    llm = get_llm(provider)
    researcher, writer = create_agents(llm, verbose=verbose)
    
    if structured_output:
        research_task = Task(
            description=f'Проведи исследование темы "{topic}". Верни ТОЛЬКО валидный JSON по схеме: topic, research_content, article_content, success, metadata.',
            expected_output="JSON с исследованием и статьей на русском языке.",
            agent=researcher,
            output_pydantic=ResearchTeamResponse
        )
    else:
        research_task = Task(
            description=f'Проведи исследование темы "{topic}". Дай 7-10 пунктов: факты/идеи/термины + короткие источники (если знаешь).',
            expected_output="Краткое исследование по теме в виде пунктов.",
            agent=researcher
        )
    
    write_task = Task(
        description=f'Напиши короткую статью на русском по теме "{topic}" на основе исследования выше. Структура: 1) Введение 2) Основные тезисы 3) Вывод.',
        expected_output="Готовая статья, понятная и информативная.",
        agent=writer
    )
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=verbose
    )
    
    return crew


def create_dwh_crew(project_name: str, user_request: str, provider: str = "ollama", selected_agents: Optional[List[str]] = None, verbose: bool = True) -> Crew:
    llm = get_llm(provider)

    project_info = get_project_info(project_name)
    if not project_info:
        raise ValueError(f"Проект '{project_name}' не найден в конфигурации")

    project_path = project_info["path"]
    if not is_path_valid(project_path):
        raise ValueError(f"Путь к проекту не существует: {project_path}")

    file_read_tool = FileReadTool()
    tools = [file_read_tool]

    agents = create_dwh_agents(llm, project_path, tools, verbose)
    if selected_agents:
        label_to_key = {
            "Исследователь": "researcher",
            "Architect": "architect",
            "Python Developer": "python_dev",
            "SQL Developer": "sql_dev",
            "Tester": "tester"
        }
        keep = {"manager"}
        for label in selected_agents:
            key = label_to_key.get(label)
            if key:
                keep.add(key)
        agents = {k: v for k, v in agents.items() if k in keep}

    manager_agent = agents["manager"]

    try:
        root_entries = sorted(os.listdir(project_path))
    except Exception:
        root_entries = []
    ignored = {".git", "venv", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode"}
    root_entries = [e for e in root_entries if e not in ignored]
    if len(root_entries) > 60:
        root_listing = ", ".join(root_entries[:60]) + ", …"
    else:
        root_listing = ", ".join(root_entries)

    context = f"""
    Проект: {project_name}
    Описание: {project_info.get('description', 'Нет описания')}
    Технологии: {', '.join(project_info.get('tech_stack', []))}
    База данных: {project_info.get('database', {}).get('type', 'Не указана')}
    Путь к проекту: {project_path}

    Корень проекта (без .git/venv): {root_listing}

    Ключевые файлы (их можно читать через FileReadTool по полному пути):
    - {project_path}/README.md
    - {project_path}/app.py
    - {project_path}/crew.py
    - {project_path}/config.yaml
    - {project_path}/requirements.txt
    - {project_path}/agents/factory.py

    Доступные агенты:
    - Исследователь: анализирует структуру проекта и код
    - Architect: проектирует архитектуру DWH
    - Python Developer: разрабатывает Python код для ETL и обработки данных
    - SQL Developer: оптимизирует SQL запросы и моделирует данные
    - QA Tester: обеспечивает качество кода и данных
    """

    main_task = Task(
        description=f"""
        Ты технический руководитель DWH команды. Выполни запрос пользователя максимально быстро и по делу.

        Контекст проекта:
        {context}

        Запрос пользователя: {user_request}

        Правила:
        - Если вопрос "что это за проект" (или близко) — ответь сам кратко (5-8 пунктов), без делегирования.
        - Иначе делегируй максимум 1-2 агентам (если они доступны) и попроси их выполнить узкую часть задачи.
        - Не перечисляй весь проект рекурсивно. Читай только 1-3 конкретных файла через FileReadTool.
        - У тебя ЕСТЬ доступ к инструментам чтения файлов. Никогда не отвечай фразами вида "I can't access files/tools".
        - Финальный ответ: на русском, структурировано, с конкретными шагами/рекомендациями.
        """,
        expected_output="Координированный результат работы всей команды с решениями, кодом и рекомендациями, или описание мультиагентной системы.",
        agent=manager_agent
    )

    crew = Crew(
        agents=list(agents.values()),
        tasks=[main_task],
        verbose=verbose
    )

    return crew


if __name__ == "__main__":
    topic = "Искусственный интеллект в современном мире"
    provider = "ollama"
    crew = create_crew(topic, provider)
    result = crew.kickoff()
    print(result)
