import os
from dotenv import load_dotenv

load_dotenv(override=True)

os.environ["CREWAI_TELEMETRY_OPT_OUT"] = 'false'
os.environ["LITELLM_LOG"] = "ERROR"

from crewai import Agent, Task, Crew, LLM

def get_llm(provider: str) -> LLM:
    if provider == "zai":
        return LLM(
            model=os.getenv("ZAI_MODEL", "zai/zai-model"),
            api_key=os.getenv("ZAI_API_KEY"),
            api_base=os.getenv("ZAI_BASE_URL", "https://api.zai.ai/v1"),
            temperature=0.7
        )
    elif provider == "ollama":
        return LLM(
            model=os.getenv("OLLAMA_MODEL", "mistral"),
            api_base=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="dummy",
            provider="openai",
            temperature=0.7
        )
    elif provider == "vllm":
        return LLM(
            model=os.getenv("VLLM_MODEL", "openai/meta-llama/Llama-2-7b-chat-hf"),
            api_key=os.getenv("VLLM_API_KEY", "dummy"),
            api_base=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
            temperature=0.7
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

def create_agents(llm):
    researcher = Agent(
        role="Исследователь",
        goal="Проводить глубокий анализ и исследование заданной темы",
        backstory="Ты опытный исследователь с аналитическим мышлением, который умеет находить и структурировать информацию",
        verbose=True,
        llm=llm
    )
    
    writer = Agent(
        role="Писатель",
        goal="Создавать качественный контент на основе предоставленной информации",
        backstory="Ты талантливый писатель, который превращает исследования в понятный и привлекательный текст",
        verbose=True,
        llm=llm
    )
    
    return researcher, writer

def create_crew(topic: str, provider: str = "ollama") -> Crew:
    llm = get_llm(provider)
    researcher, writer = create_agents(llm)
    
    research_task = Task(
        description=f"Провести исследование темы: {topic}. Найти ключевые факты и информацию.",
        expected_output="Структурированный отчет с основными фактами и информацией по теме.",
        agent=researcher
    )
    
    write_task = Task(
        description=f"Написать статью на основе результатов исследования по теме: {topic}",
        expected_output="Готовая статья, понятная и информативная.",
        agent=writer
    )
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=True
    )
    
    return crew

if __name__ == "__main__":
    topic = "Искусственный интеллект в современном мире"
    provider = "ollama"
    crew = create_crew(topic, provider)
    result = crew.kickoff()
    print(result)
