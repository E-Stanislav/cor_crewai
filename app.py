import streamlit as st
from crew import create_crew

st.set_page_config(page_title="Multi-Agent System", page_icon="🤖")

st.title("🤖 Мультиагентная система CrewAI")
st.write("Система с двумя агентами: Исследователь и Писатель")

col1, col2 = st.columns([3, 1])

with col1:
    topic = st.text_input("Введите тему для исследования:", placeholder="Искусственный интеллект в современном мире")

with col2:
    provider = st.selectbox(
        "Провайдер LLM:",
        ["zai", "vllm", "ollama"],
        index=0
    )

if st.button("Запустить агентов"):
    if topic:
        with st.spinner(f"Агенты работают ({provider})..."):
            try:
                crew = create_crew(topic, provider)
                result = crew.kickoff()
                
                st.success("✅ Работа завершена!")
                st.markdown("## Результат:")
                st.markdown(result)
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")
    else:
        st.warning("Пожалуйста, введите тему")
