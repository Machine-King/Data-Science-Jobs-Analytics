# Proyecto Empleabilidad - Análisis de Datos

Este proyecto analiza datos de empleabilidad en Python, procesando y visualizando ofertas de empleo para identificar tendencias tecnológicas y patrones relevantes en el mercado laboral. Utiliza una arquitectura modular para facilitar el mantenimiento y la reutilización del código.

## Estructura del Proyecto

- `api_template.py`: Script orquestador para consumir la API de Jooble de forma concurrente y cargar datos en la base de datos (Supabase/PostgreSQL).
- `dashboard_comparison.py`: Dashboard interactivo (punto de entrada principal) para visualizar y comparar tendencias del mercado laboral usando registros de la base de datos.
- `modulos/`: Carpeta que concentra la lógica de la aplicación agrupada por contexto:
  - `modulos/jooble_api/`: Módulos orientados a la interacción con la API de Jooble y el tratamiento de los textos y base de datos (`api_cliente.py`, `analisis.py`, `base_datos.py`, `configuracion.py`, `modelos.py`, `procesamiento_texto.py`, `ubicaciones.py`).
  - `modulos/dashboard/`: Módulos que actúan como componentes visuales acoplados a Streamlit (`charts.py`, `data_loader.py`, `insights.py`, `job_list.py`, `metrics.py`, `sidebar.py`, `styles.py`).

## Automatización recomendada

Para mantener los datos actualizados y la base de datos disponible automáticamente, se aconseja crear una tarea programada en Windows (o configurar rutinas Cron):

1. Edita el archivo `ejecutar_api.bat` y reemplaza la ruta dura genérica por la de tu entorno local.
2. Fija estas instrucciones abriendo el Programador de tareas de Windows. Se sugiere configurar la descarga semanal de registros con *ejecutar_api*.

Esto garantizará que los datos de las ofertas se actualicen sin requerir intervención manual constante.

## Uso

1. Ejecuta indirectamente mediante el bat, o directamente el script `api_template.py` para obtener datos desde la API de Jooble y volcarlos a la base de datos PostgreSQL.
2. Levanta la visualización de los datos empleando comandos de Streamlit localmente:
   ```powershell
   streamlit run dashboard_comparison.py
   ```
   *Alternativamente, puedes desplegar este dashboard en la nube de forma gratuita vinculando tu repositorio a [streamlit.io](https://streamlit.io/) (Streamlit Community Cloud).*


## Requisitos

- Python 3.11 o superior
- Bibliotecas necesarias: `pandas`, `streamlit`, `plotly`, `psycopg2`, `python-dotenv`, `requests`

Para instalar las dependencias vía *pip*:

```powershell
pip install pandas streamlit plotly psycopg2 python-dotenv requests
```

> **Nota:** Se requiere configurar las variables de entorno para funcionar (`JOOBLE_API_KEY`, `POSTGRES_CONN_STR`) dentro de un correspondiente archivo local `.env`.

## Creador
Carlos Luis Rodríguez Brito

## Licencia
Este proyecto es de uso personal y educativo.
