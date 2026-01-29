import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"
import streamlit as st
from crew import create_crew, create_dwh_crew
from utils.file_utils import get_project_list, get_project_info, is_path_valid

st.set_page_config(page_title="Multi-Agent DWH System", page_icon="🤖")

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "dwh_result" not in st.session_state:
    st.session_state.dwh_result = None

st.title("🤖 Мультиагентная система DWH команды")

tab1, tab2 = st.tabs(["Исследовательская команда", "DWH Команда"])

with tab1:
    st.write("Система с двумя агентами: Исследователь и Писатель")
    
    if st.session_state.research_result:
        st.success("✅ Последний результат:")
        st.markdown("## Результат:")
        st.markdown(st.session_state.research_result)
    
    if st.button("Очистить результаты", key="clear_research"):
        st.session_state.research_result = None
        st.rerun()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "Введите тему для исследования:",
            placeholder="Искусственный интеллект в современном мире",
            key="research_topic"
        )
    
    with col2:
        provider = st.selectbox(
            "Провайдер LLM:",
            ["zai", "vllm", "ollama"],
            index=2,
            key="research_provider"
        )
    
    structured_output = st.checkbox("Структурированный ответ (JSON)", value=False, key="research_structured_output")
    
    if st.button("Запустить исследовательских агентов", key="run_research"):
        if topic:
            with st.spinner(f"Агенты работают ({provider})..."):
                try:
                    crew = create_crew(topic, provider, structured_output=structured_output)
                    result = crew.kickoff()
                    st.session_state.research_result = result
                    
                    st.success("✅ Работа завершена!")
                    st.markdown("## Результат:")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
        else:
            st.warning("Пожалуйста, введите тему")

with tab2:
    st.write("DWH команда: Python Developer, SQL Developer, Architect, Tester, Researcher")
    
    if st.session_state.dwh_result:
        st.success("✅ Последний результат:")
        st.markdown("## Результат:")
        st.markdown(st.session_state.dwh_result)
    
    if st.button("Очистить результаты", key="clear_dwh"):
        st.session_state.dwh_result = None
        st.rerun()
    
    try:
        projects = get_project_list()
    except FileNotFoundError:
        projects = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if projects:
            selected_project = st.selectbox(
                "Выберите проект:",
                projects,
                index=0,
                key="dwh_project"
            )
            
            if selected_project:
                project_info = get_project_info(selected_project)
                if project_info:
                    st.info(f"""
                    **Описание:** {project_info.get('description', 'Нет описания')}
                    **Технологии:** {', '.join(project_info.get('tech_stack', []))}
                    **База данных:** {project_info.get('database', {}).get('type', 'Не указана')}
                    **Путь:** `{project_info.get('path', 'Не указан')}`
                    """)
                    
                    if not is_path_valid(project_info.get('path', '')):
                        st.warning(f"⚠️ Путь к проекту не существует: {project_info.get('path', '')}")
        else:
            st.warning("⚠️ Проекты не найдены. Добавьте проекты в файл `config.yaml`")
            selected_project = None
    
    with col2:
        provider = st.selectbox(
            "Провайдер LLM:",
            ["zai", "vllm", "ollama"],
            index=2,
            key="dwh_provider"
        )
    
    user_request = st.text_area(
        "Ваш запрос к DWH команде:",
        placeholder="Опишите что нужно сделать: оптимизировать SQL запрос, создать Python скрипт ETL, проверить архитектуру...",
        height=120,
        key="dwh_request"
    )
    
    col3, col4 = st.columns(2)
    
    with col3:
        use_all_agents = st.checkbox("Использовать всех агентов", value=True, key="use_all_agents")
    
    with col4:
        selected_agents = None
        if not use_all_agents:
            selected_agents = st.multiselect(
                "Выберите агентов:",
                ["Исследователь", "Architect", "Python Developer", "SQL Developer", "Tester"],
                default=["Исследователь", "Python Developer"],
                key="dwh_agents"
            )
    
    if st.button("Запустить DWH команду", key="run_dwh"):
        if selected_project:
            if user_request:
                with st.spinner(f"DWH команда работает ({provider})..."):
                    try:
                        crew = create_dwh_crew(selected_project, user_request, provider, selected_agents=selected_agents)
                        result = crew.kickoff()
                        st.session_state.dwh_result = result
                        
                        st.success("✅ DWH команда завершила работу!")
                        st.markdown("## Результат:")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
            else:
                st.warning("Пожалуйста, введите запрос")
        else:
            st.warning("Пожалуйста, выберите проект")
