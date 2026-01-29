from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """Модель информации о проекте"""
    name: str = Field(description="Название проекта")
    description: str = Field(default="", description="Описание проекта")
    tech_stack: List[str] = Field(default_factory=list, description="Технологический стек")
    database: Dict[str, str] = Field(default_factory=dict, description="Информация о базе данных")
    path: str = Field(description="Путь к проекту")


class AgentResponse(BaseModel):
    """Базовая модель ответа агента"""
    agent_name: str = Field(description="Имя агента, который предоставил ответ")
    content: str = Field(description="Содержание ответа")
    timestamp: str = Field(description="Время получения ответа")


class TaskOutput(BaseModel):
    """Базовая модель вывода задачи"""
    task_type: str = Field(description="Тип задачи")
    description: str = Field(description="Описание выполненной работы")
    result: str = Field(description="Результат выполнения задачи")
    success: bool = Field(default=True, description="Успешность выполнения")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")


class DWHProjectAnalysis(TaskOutput):
    """Модель для анализа DWH проекта"""
    project_structure: Dict[str, Any] = Field(default_factory=dict, description="Структура проекта")
    key_files: List[str] = Field(default_factory=list, description="Ключевые файлы")
    technologies_used: List[str] = Field(default_factory=list, description="Используемые технологии")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации")


class PythonCodeSolution(TaskOutput):
    """Модель для Python кода"""
    code: str = Field(description="Сгенерированный Python код")
    file_path: Optional[str] = Field(default=None, description="Путь к файлу для сохранения")
    dependencies: List[str] = Field(default_factory=list, description="Необходимые зависимости")
    explanation: str = Field(default="", description="Объяснение кода")


class SQLQuerySolution(TaskOutput):
    """Модель для SQL запросов"""
    query: str = Field(description="SQL запрос")
    explanation: str = Field(default="", description="Объяснение запроса")
    optimization_notes: Optional[str] = Field(default=None, description="Заметки по оптимизации")
    performance_impact: Optional[str] = Field(default=None, description="Влияние на производительность")


class ArchitectureDesign(TaskOutput):
    """Модель для архитектурных решений"""
    architecture_type: str = Field(description="Тип архитектуры")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="Компоненты архитектуры")
    data_flow: Optional[str] = Field(default=None, description="Поток данных")
    scalability_considerations: List[str] = Field(default_factory=list, description="Соображения масштабируемости")
    implementation_steps: List[str] = Field(default_factory=list, description="Шаги реализации")


class TestRecommendations(TaskOutput):
    """Модель для тестовых рекомендаций"""
    test_types: List[str] = Field(default_factory=list, description="Типы тестов")
    test_framework: str = Field(description="Тестовый фреймворк")
    test_coverage: Optional[float] = Field(default=None, description="Ожидаемое покрытие тестами")
    quality_metrics: List[Dict[str, Any]] = Field(default_factory=list, description="Метрики качества")


class DWHTeamResponse(BaseModel):
    """Итоговая модель ответа всей DWH команды"""
    project_info: ProjectInfo = Field(description="Информация о проекте")
    user_request: str = Field(description="Исходный запрос пользователя")
    agent_responses: List[AgentResponse] = Field(default_factory=list, description="Ответы отдельных агентов")
    final_answer: str = Field(description="Финальный ответ")
    analysis_result: Optional[DWHProjectAnalysis] = Field(default=None, description="Результат анализа")
    python_solutions: List[PythonCodeSolution] = Field(default_factory=list, description="Python решения")
    sql_solutions: List[SQLQuerySolution] = Field(default_factory=list, description="SQL решения")
    architecture_designs: List[ArchitectureDesign] = Field(default_factory=list, description="Архитектурные решения")
    test_recommendations: List[TestRecommendations] = Field(default_factory=list, description="Рекомендации по тестированию")
    success: bool = Field(default=True, description="Успешность выполнения")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные выполнения")


class ResearchTeamResponse(BaseModel):
    """Модель ответа исследовательской команды"""
    topic: str = Field(description="Исследуемая тема")
    research_content: str = Field(description="Содержание исследования")
    article_content: str = Field(description="Сгенерированная статья")
    success: bool = Field(default=True, description="Успешность выполнения")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные выполнения")