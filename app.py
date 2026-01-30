"""Multi-Agent DWH System - Modern Streamlit Chat Interface.

Combines research team and DWH team in a unified chat experience.
"""

import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"

import streamlit as st
from crew import create_crew, create_dwh_crew
from utils.file_utils import get_project_list, get_project_info, is_path_valid


# === PAGE CONFIG ===
st.set_page_config(
    page_title="Multi-Agent DWH System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# === MODERN CSS ===
st.markdown("""
<style>
:root {
    --bg: #0e1117;
    --surface: rgba(255, 255, 255, 0.05);
    --surface-hover: rgba(255, 255, 255, 0.08);
    --border: rgba(255, 255, 255, 0.10);
    --text: rgba(255, 255, 255, 0.92);
    --muted: rgba(255, 255, 255, 0.65);
    --accent: #7c5cff;
    --accent2: #34d399;
    --danger: #fb7185;
    --radius: 14px;
}

/* Background gradient */
.stApp {
    background: radial-gradient(ellipse 1200px 600px at 15% 0%, rgba(124,92,255,0.18), transparent 55%),
                radial-gradient(ellipse 900px 500px at 85% 5%, rgba(52,211,153,0.12), transparent 50%),
                var(--bg);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(7, 11, 20, 0.85);
    border-right: 1px solid var(--border);
    backdrop-filter: blur(12px);
}

/* Hide footer */
footer { visibility: hidden; }

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    margin-bottom: 16px;
}

.card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 8px;
}

/* Status chips */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--surface);
    font-size: 0.85rem;
    color: var(--muted);
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--muted);
}
.dot.ok { background: var(--accent2); }
.dot.warn { background: #fbbf24; }
.dot.bad { background: var(--danger); }

/* Buttons */
.stButton button {
    border-radius: 12px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    transition: all 0.15s ease;
}
.stButton button:hover {
    background: var(--surface-hover);
    border-color: rgba(124,92,255,0.4);
    transform: translateY(-1px);
}

/* Inputs */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.03);
    padding: 1rem;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(124,92,255,0.06);
    border-color: rgba(124,92,255,0.15);
}

/* Top header bar */
.header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: var(--surface);
    margin-bottom: 20px;
}

.header-title {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0;
}

.header-subtitle {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: 4px;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    color: var(--muted);
    text-align: center;
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 16px;
    opacity: 0.5;
}

/* Reduce padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Divider */
hr {
    border-color: var(--border);
    margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)


# === SESSION STATE ===
def init_session_state():
    defaults = {
        "messages": [],
        "team_mode": "research",
        "connected": False,
        "selected_project": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# === HELPER FUNCTIONS ===
def get_status_chip(connected: bool, team: str) -> str:
    if connected:
        return f'<span class="chip"><span class="dot ok"></span> {team}</span>'
    return '<span class="chip"><span class="dot bad"></span> Не подключено</span>'


def render_empty_state():
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div style="font-size: 1.2rem; margin-bottom: 8px;">Начните диалог</div>
            <div style="font-size: 0.9rem; opacity: 0.7;">
                Введите сообщение в поле ниже или используйте быстрые команды
            </div>
        </div>
    """, unsafe_allow_html=True)


def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})


def clear_chat():
    st.session_state.messages = []


# === SIDEBAR ===
def render_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Настройки")
        
        # Team selector
        st.markdown('<div class="card"><div class="card-title">👥 Команда</div></div>', 
                    unsafe_allow_html=True)
        
        team = st.radio(
            "Выберите команду:",
            ["🔬 Исследовательская", "🏗️ DWH"],
            horizontal=True,
            label_visibility="collapsed"
        )
        st.session_state.team_mode = "research" if "Исследовательская" in team else "dwh"
        
        st.divider()
        
        # LLM Provider
        st.markdown('<div class="card"><div class="card-title">🔌 Провайдер LLM</div></div>', 
                    unsafe_allow_html=True)
        
        provider = st.selectbox(
            "Провайдер:",
            ["ollama", "vllm", "zai"],
            index=0,
            label_visibility="collapsed",
            help="ollama - локальный, vllm - высокопроизводительный, zai - облачный"
        )
        
        verbose = st.toggle("📝 Подробные логи", value=False)
        
        # Thinking mode для vLLM (Qwen3, DeepSeek и др.)
        thinking_enabled = False
        thinking_budget = 4096
        if provider == "vllm":
            st.divider()
            st.markdown('<div class="card"><div class="card-title">🧠 Режим мышления</div></div>', 
                        unsafe_allow_html=True)
            thinking_enabled = st.toggle(
                "💭 Включить thinking mode", 
                value=False,
                help="Для моделей с reasoning (Qwen3, DeepSeek R1). Модель будет 'думать' перед ответом."
            )
            if thinking_enabled:
                thinking_budget = st.slider(
                    "Бюджет токенов на размышления:",
                    min_value=1024,
                    max_value=16384,
                    value=4096,
                    step=512,
                    help="Количество токенов для внутренних рассуждений модели"
                )
        
        st.divider()
        
        # Team-specific settings
        if st.session_state.team_mode == "research":
            st.markdown('<div class="card"><div class="card-title">🔬 Настройки исследования</div></div>', 
                        unsafe_allow_html=True)
            
            structured = st.toggle("📋 JSON ответ", value=False)
            selected_project = None
            selected_agents = None
            
        else:  # DWH
            st.markdown('<div class="card"><div class="card-title">🏗️ Настройки DWH</div></div>', 
                        unsafe_allow_html=True)
            
            structured = False
            
            # Project selection
            try:
                projects = get_project_list()
            except FileNotFoundError:
                projects = []
            
            if projects:
                selected_project = st.selectbox(
                    "📁 Проект:",
                    projects,
                    index=0,
                    label_visibility="collapsed"
                )
                
                project_info = get_project_info(selected_project)
                if project_info:
                    path_valid = is_path_valid(project_info.get("path", ""))
                    
                    with st.expander("ℹ️ Информация о проекте"):
                        st.markdown(f"**Описание:** {project_info.get('description', '—')}")
                        st.markdown(f"**Стек:** {', '.join(project_info.get('tech_stack', []))}")
                        st.markdown(f"**БД:** {project_info.get('database', {}).get('type', '—')}")
                        st.code(project_info.get('path', ''), language=None)
                        
                        if not path_valid:
                            st.error("⚠️ Путь не существует")
                
                st.session_state.connected = path_valid
                st.session_state.selected_project = selected_project
            else:
                st.warning("Проекты не найдены в config.yaml")
                selected_project = None
                st.session_state.connected = False
            
            # Agent selection
            st.divider()
            use_all = st.toggle("👥 Все агенты", value=True)
            
            selected_agents = None
            if not use_all:
                selected_agents = st.multiselect(
                    "Выберите агентов:",
                    ["Исследователь", "Architect", "Python Developer", "SQL Developer", "Tester"],
                    default=["Исследователь", "Python Developer"]
                )
        
        st.divider()
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Очистить", use_container_width=True):
                clear_chat()
                st.rerun()
        with col2:
            st.metric("💬", len(st.session_state.messages))
        
        # Quick actions for DWH
        if st.session_state.team_mode == "dwh" and st.session_state.connected:
            st.divider()
            st.markdown('<div class="card"><div class="card-title">🚀 Быстрые команды</div></div>', 
                        unsafe_allow_html=True)
            
            if st.button("📊 Анализ архитектуры", use_container_width=True):
                add_message("user", "Проанализируй архитектуру проекта")
                st.rerun()
            
            if st.button("🔍 Code Review", use_container_width=True):
                add_message("user", "Сделай code review проекта")
                st.rerun()
            
            if st.button("📝 Документация", use_container_width=True):
                add_message("user", "Сгенерируй документацию для проекта")
                st.rerun()
    
    return provider, verbose, structured, selected_project if st.session_state.team_mode == "dwh" else None, selected_agents if st.session_state.team_mode == "dwh" else None, thinking_enabled, thinking_budget


# === MAIN CHAT ===
def render_chat(provider: str, verbose: bool, structured: bool, 
                selected_project: str | None, selected_agents: list | None,
                thinking_enabled: bool = False, thinking_budget: int = 4096):
    
    # Устанавливаем переменные окружения для thinking mode
    import os
    os.environ["VLLM_ENABLE_THINKING"] = "true" if thinking_enabled else "false"
    os.environ["VLLM_THINKING_BUDGET"] = str(thinking_budget)
    
    # Header
    team_name = "Исследовательская команда" if st.session_state.team_mode == "research" else "DWH Команда"
    status = get_status_chip(
        st.session_state.connected if st.session_state.team_mode == "dwh" else True,
        team_name
    )
    
    st.markdown(f"""
        <div class="header-bar">
            <div>
                <div class="header-title">🤖 Multi-Agent System</div>
                <div class="header-subtitle">{team_name} • {provider.upper()}{' 🧠 Thinking' if thinking_enabled else ''}</div>
            </div>
            <div>{status}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container(height=500)
    
    with chat_container:
        if not st.session_state.messages:
            render_empty_state()
        else:
            for msg in st.session_state.messages:
                avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("💬 Введите сообщение..."):
        add_message("user", prompt)
        
        # Show user message immediately
        with chat_container:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔄 Обрабатываю запрос..."):
                    try:
                        if st.session_state.team_mode == "research":
                            crew = create_crew(
                                prompt,
                                provider,
                                structured_output=structured,
                                verbose=verbose
                            )
                        else:
                            if not selected_project:
                                raise ValueError("Выберите проект в настройках")
                            crew = create_dwh_crew(
                                selected_project,
                                prompt,
                                provider,
                                selected_agents=selected_agents,
                                verbose=verbose
                            )
                        
                        result = crew.kickoff()
                        response = str(result)
                        
                    except Exception as e:
                        response = f"❌ **Ошибка:** {str(e)}"
                
                st.markdown(response)
                add_message("assistant", response)
        
        st.rerun()


# === MAIN ===
def main():
    settings = render_sidebar()
    render_chat(*settings)


if __name__ == "__main__":
    main()
