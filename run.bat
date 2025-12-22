@echo off
REM Script para ejecutar la aplicación web
echo.
echo ========================================
echo   Generador de Codigos de Barras Web
echo   Versión Streamlit
echo ========================================
echo.
echo Iniciando aplicacion...
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Verificar que Streamlit esté instalado
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Streamlit no está instalado. Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Ejecutar la aplicación
streamlit run app.py

pause
