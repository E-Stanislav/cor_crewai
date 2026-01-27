# cor_crewai

Мультиагентная система на основе CrewAI с интерфейсом Streamlit. Поддерживает zai, Ollama и vLLM через LiteLLM.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройка провайдера:

**Ollama:**
```bash
# Установите Ollama: https://ollama.ai
# Запустите сервер Ollama
ollama serve
# Скачайте модель
ollama pull llama2
```

**vLLM:**
```bash
# Установите vLLM
pip install vllm
# Запустите сервер
python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-chat-hf
```

**Zai:**
```bash
# Получите API ключ на https://zai.ai
```

4. Создайте файл `.env`:
```bash
cp .env.example .env
```
Отредактируйте `.env` для выбранного провайдера.

## Запуск

**Через скрипт:**
```bash
./run.sh
```

**Или вручную:**
```bash
source venv/bin/activate
streamlit run app.py
```

Выберите провайдер в интерфейсе (Ollama, vLLM или Zai).

## Структура

- `crew.py` - Определение агентов и Crew (использует LiteLLM)
- `app.py` - Streamlit интерфейс
- `requirements.txt` - Зависимости проекта
- `run.sh` - Скрипт для запуска

## Агенты

1. **Исследователь** - Проводит анализ и исследование темы
2. **Писатель** - Создает контент на основе исследования

## LiteLLM

Проект использует LiteLLM для унифицированного доступа к различным LLM провайдерам. Модели указываются в формате:
- Ollama: `ollama/llama2`
- vLLM: `openai/meta-llama/Llama-2-7b-chat-hf`
- Zai: `zai/zai-model`
