@echo off
REM Archivo batch para iniciar la aplicación de códigos de barras
REM Autor: Sistema automatizado
REM Fecha: 22/12/2025

echo ========================================
echo  EMERGENCIAS GRAU - CODIGO DE BARRAS
echo ========================================
echo.
echo Iniciando aplicación web...
echo.

REM Cambiar al directorio de la aplicación
cd /d "D:\Usuarios\RPA.007LABORA3\Documents\web_grau_barras\web_app"

REM Iniciar la aplicación Streamlit
echo Abriendo aplicación en el navegador...
streamlit run app.py

REM Si hay error, pausar para ver el mensaje
if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar la aplicación
    echo Verifica que Streamlit esté instalado: pip install streamlit
    pause
)
