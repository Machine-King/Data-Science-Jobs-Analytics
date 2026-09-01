# Proyecto Empleabilidad - Análisis de Datos

Este proyecto analiza datos de empleabilidad en Python, procesando y visualizando ofertas de empleo para identificar tendencias tecnológicas y patrones relevantes en el mercado laboral. Utiliza una arquitectura modular para facilitar el mantenimiento y la reutilización del código.

## Estructura del Proyecto

- `api_template.py`: Script orquestador para consumir la API de Jooble de forma concurrente y cargar datos en la base de datos (Supabase/PostgreSQL).
- `dashboard_comparison.py`: Dashboard interactivo (punto de entrada principal) para visualizar y comparar tendencias del mercado laboral usando registros de la base de datos.
- `modulos/`: Carpeta que concentra la lógica de la aplicación agrupada por contexto:
  - `modulos/jooble_api/`: Módulos orientados a la interacción con la API de Jooble y el tratamiento de los textos y base de datos (`api_cliente.py`, `analisis.py`, `base_datos.py`, `configuracion.py`, `modelos.py`, `procesamiento_texto.py`, `ubicaciones.py`).
  - `modulos/dashboard/`: Módulos que actúan como componentes visuales acoplados a Streamlit (`charts.py`, `data_loader.py`, `insights.py`, `job_list.py`, `metrics.py`, `sidebar.py`, `styles.py`).

## Automatización con GitHub Actions

La descarga de datos está automatizada mediante el workflow [`.github/workflows/descarga_datos.yml`](.github/workflows/descarga_datos.yml), que se ejecuta **semanalmente (lunes a las 06:00 UTC)** y también puede lanzarse manualmente desde la pestaña **Actions → Descarga de datos Jooble → Run workflow**.

El workflow instala las dependencias mínimas (`requirements-api.txt`), ejecuta `api_template.py` y vuelca las ofertas en la base de datos PostgreSQL. Si la API no devuelve ninguna oferta, el script termina con error sin tocar las tablas existentes.

Para que funcione, es necesario configurar dos secretos en el repositorio (**Settings → Secrets and variables → Actions**):

| Secreto | Contenido |
|---|---|
| `JOOBLE_API_KEYS` | Una o varias API keys de Jooble, separadas por comas |
| `POSTGRES_CONN_STR` | Cadena de conexión a PostgreSQL (Supabase) |

> **Nota:** GitHub desactiva los workflows programados si el repositorio pasa ~60 días sin actividad; en ese caso basta con reactivarlos desde la pestaña Actions.

Como alternativa para ejecución local, el archivo `ejecutar_api.bat` permite programar la descarga con el Programador de tareas de Windows (edita antes la ruta del proyecto dentro del .bat).

## Uso

1. Ejecuta indirectamente mediante el bat, o directamente el script `api_template.py` para obtener datos desde la API de Jooble y volcarlos a la base de datos PostgreSQL.
2. Levanta la visualización de los datos empleando comandos de Streamlit localmente:
   ```powershell
   streamlit run dashboard_comparison.py
   ```
   *Alternativamente, puedes desplegar este dashboard en la nube de forma gratuita vinculando tu repositorio a [streamlit.io](https://streamlit.io/) (Streamlit Community Cloud).*


## Requisitos

- Python 3.11 o superior
- Dependencias completas (dashboard + descarga): `requirements.txt`
- Dependencias mínimas para solo la descarga de datos: `requirements-api.txt`

Para instalar las dependencias vía *pip*:

```powershell
pip install -r requirements.txt
```

> **Nota:** Para ejecutar en local se requiere un archivo `.env` con las variables `JOOBLE_API_KEYS` (una o varias keys separadas por comas; también se acepta `JOOBLE_API_KEY` con una sola) y `POSTGRES_CONN_STR`.

## Creador
Carlos Luis Rodríguez Brito

## Licencia
Este proyecto es de uso personal y educativo.
