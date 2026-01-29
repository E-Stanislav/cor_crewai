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
from utils.file_utils import get_project_info, is_path_valid, scan_project_structure, find_key_files
from models.schemas import ResearchTeamResponse


def get_llm(provider: str, temperature: float = 0.7) -> LLM:
    if provider == "zai":
        api_key = os.getenv("ZAI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("Для провайдера 'zai' нужно указать ZAI_API_KEY в .env")
        return LLM(
            model=os.getenv("ZAI_MODEL", "zai/zai-model"),
            api_key=api_key,
            api_base=os.getenv("ZAI_BASE_URL", "https://api.zai.ai/v1"),
            temperature=temperature
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
            temperature=temperature
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
            temperature=temperature
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Оптимальные температуры для разных ролей
AGENT_TEMPERATURES = {
    "manager": 0.4,      # Точные решения, координация
    "researcher": 0.6,   # Анализ, поиск паттернов
    "architect": 0.7,    # Креативные архитектурные решения
    "python_dev": 0.3,   # Точный код без галлюцинаций
    "sql_dev": 0.2,      # SQL должен быть максимально точным
    "tester": 0.4,       # Точные тест-кейсы
    "writer": 0.85,      # Креативный текст
}


def create_agents(provider: str, project_path: Optional[str] = None, verbose: bool = True):
    # Исследователь: средняя температура для баланса точности и креативности
    researcher_llm = get_llm(provider, temperature=AGENT_TEMPERATURES["researcher"])
    researcher = Agent(
        role="Исследователь",
        goal="Проводить глубокий анализ и исследование заданной темы и отвечать на русском языке",
        backstory="Ты опытный исследователь с аналитическим мышлением, который умеет находить и структурировать информацию. Всегда отвечай на русском языке.",
        verbose=verbose,
        llm=researcher_llm
    )
    
    # Писатель: высокая температура для креативного текста
    writer_llm = get_llm(provider, temperature=AGENT_TEMPERATURES["writer"])
    writer = Agent(
        role="Писатель",
        goal="Создавать качественный контент на основе предоставленной информации на русском языке",
        backstory="Ты талантливый писатель, который превращает исследования в понятный и привлекательный текст. Всегда пиши на русском языке.",
        verbose=verbose,
        llm=writer_llm
    )
    
    return researcher, writer


def create_crew(topic: str, provider: str = "ollama", structured_output: bool = False, verbose: bool = True) -> Crew:
    researcher, writer = create_agents(provider, verbose=verbose)
    
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
    project_info = get_project_info(project_name)
    if not project_info:
        raise ValueError(f"Проект '{project_name}' не найден в конфигурации")

    project_path = project_info["path"]
    if not is_path_valid(project_path):
        raise ValueError(f"Путь к проекту не существует: {project_path}")

    file_read_tool = FileReadTool()
    tools = [file_read_tool]

    # Создаём фабрику LLM с нужной температурой
    def llm_factory(temperature: float):
        return get_llm(provider, temperature)

    agents = create_dwh_agents(llm_factory, project_path, tools, verbose)
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

    # Автоматическое сканирование структуры проекта
    project_structure = scan_project_structure(project_path, max_depth=2, max_files=40)
    
    # Автоматическое определение ключевых файлов
    key_files = find_key_files(project_path, max_files=12)
    key_files_list = "\n    ".join(f"- {f}" for f in key_files) if key_files else "- (не найдены)"

    context = f"""
    Проект: {project_name}
    Описание: {project_info.get('description', 'Нет описания')}
    Технологии: {', '.join(project_info.get('tech_stack', []))}
    База данных: {project_info.get('database', {}).get('type', 'Не указана')}
    Путь к проекту: {project_path}

    Структура проекта:
    {project_structure}

    Ключевые файлы (автоматически определены, можно читать через FileReadTool):
    {key_files_list}

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

        КРИТИЧЕСКИ ВАЖНО для экономии токенов:
        1. Читай файлы ТОЛЬКО ты (Manager) через FileReadTool — другие агенты НЕ имеют доступа к файлам
        2. Если нужно делегировать — СНАЧАЛА прочитай нужный файл, ЗАТЕМ передай его СОДЕРЖИМОЕ агенту в тексте задачи
        3. Читай максимум 2-3 файла за запрос, только самые релевантные
        4. НЕ сканируй директории рекурсивно — структура проекта уже дана выше
        5. Для простых вопросов ("что это за проект") — отвечай сам по контексту, без чтения файлов

        Формат делегирования (если нужно):
        "Проанализируй следующий код и [задача]:
        ```python
        [вставь сюда содержимое файла]
        ```"

        Финальный ответ: на русском, структурировано, кратко.
        """,
        expected_output="Координированный результат с решениями и рекомендациями на русском языке.",
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
