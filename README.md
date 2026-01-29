# cor_crewai

Мультиагентная система на основе CrewAI с интерфейсом Streamlit. Поддерживает zai, Ollama и vLLM через LiteLLM.

## Возможности

- **Исследовательская команда**: Два агента (Исследователь и Писатель) для работы с любой темой
- **DWH команда**: Пять специализированных агентов для работы с Data Warehouse проектами:
  - **Python Developer**: Разработка Python кода для ETL, данных, pandas, airflow, dbt
  - **SQL Developer**: Оптимизация SQL запросов, моделирование данных
  - **Architect**: Проектирование архитектуры DWH (Data Vault, Kimball, Inmon)
  - **Tester**: QA тестирование, проверки качества данных, pytest, dbt tests
  - **Researcher**: Анализ кода проекта и поиск решений

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

5. Настройте DWH проекты в `config.yaml`:
```yaml
projects:
  - name: "my_dwh"
    path: "/path/to/your/dwh/project"
    description: "Мое хранилище данных"
    tech_stack:
      - "Python"
      - "SQL"
      - "dbt"
    database:
      type: "PostgreSQL"
      host: "localhost"
      port: 5432
```
Укажите реальные пути к вашим DWH проектам.

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
- `app.py` - Streamlit интерфейс с двумя вкладками
- `agents/factory.py` - Фабрика для создания агентов DWH команды
- `utils/file_utils.py` - Утилиты для работы с файловой системой и конфигурацией
- `config.yaml` - Конфигурация DWH проектов
- `requirements.txt` - Зависимости проекта
- `run.sh` - Скрипт для запуска

## Агенты

### Исследовательская команда
1. **Исследователь** - Проводит анализ и исследование темы
2. **Писатель** - Создает контент на основе исследования

### DWH Команда
1. **Технический руководитель DWH команды** - Координирует работу, делегирует задачи, обеспечивает синергию между агентами
2. **Python Developer** - Разработка Python кода для DWH решений
3. **SQL Developer** - Оптимизация SQL запросов и моделирование данных
4. **Architect** - Проектирование архитектуры DWH систем
5. **Tester** - QA тестирование и обеспечение качества данных
6. **Researcher** - Анализ кода проекта и поиск решений

## Инструменты DWH агентов

DWH агенты оснащены следующими инструментами для работы с файлами проекта:
- **DirectoryReadTool** - Читает содержимое директории проекта
- **FileReadTool** - Читает содержимое конкретных файлов

Эти инструменты позволяют агентам:
- Просматривать структуру проекта
- Анализировать существующие файлы (.py, .sql, .yaml)
- Понимать контекст проекта перед предоставлением рекомендаций

При каждом запросе DWH команда:
1. Анализирует структуру проекта через инструменты
2. Читает релевантные файлы
3. Предоставляет решения на основе реального кода проекта

## LiteLLM

Проект использует LiteLLM для унифицированного доступа к различным LLM провайдерам. Модели указываются в формате:
- Ollama: `ollama/llama2`
- vLLM: `openai/meta-llama/Llama-2-7b-chat-hf`
- Zai: `zai/zai-model`
