REM Cambia al directorio del proyecto
echo Ejecutando api_template.py...
cd "ruta_proyecto"
REM Activa el entorno virtual si usas venv (descomenta la siguiente linea si es necesario)
call .venv\Scripts\activate
REM Ejecuta el script
python api_template.py
PAUSE
