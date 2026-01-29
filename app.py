import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"
import streamlit as st
from crew import create_crew, create_dwh_crew
from utils.file_utils import get_project_list, get_project_info, is_path_valid

st.set_page_config(
    page_title="Multi-Agent DWH System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Основной контейнер - занимает весь экран */
    .stMain {
        height: 100vh;
        overflow: hidden;
    }
    
    /* Основные стили чата */
    .stChatMessage {
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Скрыть дефолтный footer */
    footer {visibility: hidden;}
    
    /* Фиксированный input внизу */
    .stChatInput {
        position: fixed !important;
        bottom: 1rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: calc(100% - 2rem) !important;
        max-width: 800px !important;
        z-index: 1000 !important;
        background: var(--background-color, white) !important;
        padding: 0.5rem !important;
        border-radius: 1.5rem !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* При открытом сайдбаре смещаем input */
    [data-testid="stSidebar"][aria-expanded="true"] ~ .stMain .stChatInput {
        left: calc(50% + 150px) !important;
    }
    
    /* Контейнер чата с правильной высотой */
    [data-testid="stVerticalBlock"] > [data-testid="element-container"]:has(.stChatMessage) {
        max-height: calc(100vh - 200px) !important;
        overflow-y: auto !important;
    }
    
    /* Анимация печати */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .typing-indicator {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Убираем лишние отступы сверху */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 100px !important;
    }
    
    /* Темная тема */
    @media (prefers-color-scheme: dark) {
        .stChatInput {
            background: #262730 !important;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.3) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if "research_chat" not in st.session_state:
    st.session_state.research_chat = []
if "dwh_chat" not in st.session_state:
    st.session_state.dwh_chat = []
if "research_settings_open" not in st.session_state:
    st.session_state.research_settings_open = False
if "dwh_settings_open" not in st.session_state:
    st.session_state.dwh_settings_open = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "research"


def render_chat_messages(messages: list, container):
    with container:
        if not messages:
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; align-items: center; 
                            justify-content: center; height: 300px; color: #888;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
                    <div style="font-size: 1.1rem;">Начните диалог...</div>
                    <div style="font-size: 0.9rem; color: #aaa; margin-top: 0.5rem;">
                        Введите сообщение в поле ниже
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for msg in messages:
                with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
                    st.markdown(msg["content"])


# === SIDEBAR: Общие настройки ===
with st.sidebar:
    st.markdown("## ⚙️ Настройки")
    
    # Переключатель команды
    team_mode = st.radio(
        "Команда:",
        ["🔬 Исследовательская", "🏗️ DWH"],
        horizontal=True,
        key="team_mode"
    )
    
    st.divider()
    
    # Общие настройки провайдера
    provider = st.selectbox(
        "🔌 Провайдер LLM",
        ["zai", "vllm", "ollama"],
        index=2,
        key="llm_provider",
        help="Выберите провайдера для языковой модели"
    )
    
    verbose_logs = st.toggle(
        "📝 Подробные логи",
        value=True,
        key="verbose_logs"
    )
    
    st.divider()
    
    # Настройки для Исследовательской команды
    if team_mode == "🔬 Исследовательская":
        structured_output = st.toggle(
            "📋 Структурированный ответ (JSON)",
            value=False,
            key="research_structured_output"
        )
        selected_project = None
        selected_agents = None
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Очистить", use_container_width=True, key="clear_research"):
                st.session_state.research_chat = []
                st.rerun()
        with col2:
            msg_count = len(st.session_state.research_chat)
            st.metric("Сообщений", msg_count)
    
    # Настройки для DWH команды
    else:
        structured_output = False
        
        try:
            projects = get_project_list()
        except FileNotFoundError:
            projects = []
        
        if projects:
            selected_project = st.selectbox(
                "📁 Проект",
                projects,
                index=0,
                key="dwh_project"
            )
            project_info = get_project_info(selected_project) if selected_project else None
            if project_info:
                with st.expander("ℹ️ Информация о проекте", expanded=False):
                    st.markdown(f"**Описание:** {project_info.get('description', 'Нет описания')}")
                    st.markdown(f"**Стек:** {', '.join(project_info.get('tech_stack', []))}")
                    st.markdown(f"**БД:** {project_info.get('database', {}).get('type', 'Не указана')}")
                    st.code(project_info.get('path', 'Не указан'), language=None)
                if not is_path_valid(project_info.get("path", "")):
                    st.error(f"⚠️ Путь не существует")
        else:
            st.warning("Проекты не найдены в `config.yaml`")
            selected_project = None
        
        st.divider()
        
        use_all_agents = st.toggle(
            "👥 Все агенты",
            value=True,
            key="use_all_agents"
        )
        
        selected_agents = None
        if not use_all_agents:
            selected_agents = st.multiselect(
                "Выберите агентов:",
                ["Исследователь", "Architect", "Python Developer", "SQL Developer", "Tester"],
                default=["Исследователь", "Python Developer"],
                key="dwh_agents"
            )
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Очистить", use_container_width=True, key="clear_dwh"):
                st.session_state.dwh_chat = []
                st.rerun()
        with col2:
            msg_count = len(st.session_state.dwh_chat)
            st.metric("Сообщений", msg_count)


# Основной интерфейс
st.markdown("## 🤖 Multi-Agent DWH System")

# Показываем соответствующий чат в зависимости от выбранной команды
if team_mode == "🔬 Исследовательская":
    # Контейнер для чата
    chat_container = st.container()
    render_chat_messages(st.session_state.research_chat, chat_container)
    
    # Поле ввода
    if prompt := st.chat_input("💬 Введите тему для исследования..."):
        st.session_state.research_chat.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                status_placeholder = st.empty()
                status_placeholder.markdown("⏳ *Агенты анализируют запрос...*")
                
                try:
                    crew = create_crew(
                        prompt, 
                        provider, 
                        structured_output=structured_output, 
                        verbose=verbose_logs
                    )
                    status_placeholder.markdown("🔄 *Исследователь собирает информацию...*")
                    result = crew.kickoff()
                    content = str(result)
                    status_placeholder.empty()
                    st.markdown(content)
                    st.session_state.research_chat.append({"role": "assistant", "content": content})
                except Exception as e:
                    status_placeholder.empty()
                    err = f"❌ **Ошибка:** {str(e)}"
                    st.error(err)
                    st.session_state.research_chat.append({"role": "assistant", "content": err})
        
        st.rerun()

else:  # DWH Команда
    # Контейнер для чата
    chat_container = st.container()
    render_chat_messages(st.session_state.dwh_chat, chat_container)
    
    # Поле ввода
    if prompt := st.chat_input("💬 Опишите задачу для DWH команды..."):
        st.session_state.dwh_chat.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                if not selected_project:
                    err = "⚠️ Пожалуйста, выберите проект в боковой панели настроек."
                    st.warning(err)
                    st.session_state.dwh_chat.append({"role": "assistant", "content": err})
                else:
                    status_placeholder = st.empty()
                    status_placeholder.markdown("⏳ *DWH команда принимает задачу...*")
                    
                    try:
                        crew = create_dwh_crew(
                            selected_project,
                            prompt,
                            provider,
                            selected_agents=selected_agents,
                            verbose=verbose_logs
                        )
                        status_placeholder.markdown("🔄 *Менеджер распределяет задачи между агентами...*")
                        result = crew.kickoff()
                        content = str(result)
                        status_placeholder.empty()
                        st.markdown(content)
                        st.session_state.dwh_chat.append({"role": "assistant", "content": content})
                    except Exception as e:
                        status_placeholder.empty()
                        err = f"❌ **Ошибка:** {str(e)}"
                        st.error(err)
                        st.session_state.dwh_chat.append({"role": "assistant", "content": err})
        
        st.rerun()
