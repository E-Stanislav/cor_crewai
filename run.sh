#!/bin/bash

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости
echo "Установка зависимостей..."
pip install -r requirements.txt

# Запускаем Streamlit приложение
echo "Запуск приложения..."
export CREWAI_TELEMETRY_OPT_OUT=true
export OTEL_SDK_DISABLED=true
export LITELLM_LOG=ERROR
streamlit run app.py
