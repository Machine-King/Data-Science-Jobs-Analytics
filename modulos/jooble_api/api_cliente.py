import json
import http.client
import time
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from modulos.jooble_api.configuracion import (
    JOOBLE_HOST, JOOBLE_API_KEY, MAX_PAGES, DAYS_FILTER, 
    API_DELAY, ERROR_WAIT_TIME
)
from modulos.jooble_api.modelos import Job
from modulos.jooble_api.procesamiento_texto import is_data_science_related, technology_appears_in_text

logger = logging.getLogger(__name__)

def _validate_config():
    """Valida que las variables de entorno necesarias estén configuradas."""
    if not JOOBLE_API_KEY:
        raise ValueError(
            "JOOBLE_API_KEY no está configurada. "
            "Asegúrate de tener un archivo .env con JOOBLE_API_KEY=tu_clave"
        )
    logger.info("Configuración validada correctamente")

@contextmanager
def http_connection(host):
    """Context manager para conexiones HTTP."""
    conn = http.client.HTTPConnection(host)
    try:
        yield conn
    finally:
        conn.close()

def _make_api_request(page, keywords, location="España"):
    try:
        with http_connection(JOOBLE_HOST) as connection:
            headers = {"Content-type": "application/json"}
            body = json.dumps({
                "keywords": keywords,
                "location": location,
                "page": page
            })
            
            connection.request('POST', f'/api/{JOOBLE_API_KEY}', body, headers)
            response = connection.getresponse()
            
            if response.status == 200:
                data = response.read().decode('utf-8')
                return json.loads(data)
            else:
                logger.error(f"Error en página {page}: {response.status} {response.reason}")
                return None
    except Exception as e:
        logger.error(f"Error en petición API: {e}")
        return None

def _process_job(job, technology, cutoff_date):
    job_title = job.get('title', '').strip()
    job_company = job.get('company', '').strip()
    job_updated = job.get('updated', '').strip()
    
    if not is_data_science_related(job_title):
        return None
    
    job_snippet = job.get('snippet', '').strip()
    if not (technology_appears_in_text(technology, job_title) or 
            technology_appears_in_text(technology, job_snippet)):
        return None
    
    if job_updated:
        try:
            job_date = datetime.fromisoformat(job_updated.split('T')[0])
            if job_date < cutoff_date:
                return None
        except ValueError:
            pass
    
    processed_job = Job(
        title=job_title or 'N/A',
        company=job_company or 'N/A',
        url=job.get('link', 'N/A'),
        description=job_snippet or 'N/A',
        location=job.get('location', '').strip() or 'N/A',
        salary=job.get('salary', '') or 'N/A',
        created=job_updated.split('T')[0] if job_updated else 'N/A',
        source=job.get('source', 'N/A'),
        job_type=job.get('type', 'N/A'),
        jooble_id=str(job.get('id', '')) or 'N/A'
    )
    job_id = f"{job_title}_{job_company}"
    
    return processed_job, job_id

def get_job_data(technology): 
    logger.info(f"Buscando trabajos de '{technology}' utilizando la API de Jooble...")

    all_jobs = []
    all_job_ids = set()
    total_available = 0
    page = 1
    
    cutoff_date = datetime.now() - timedelta(days=DAYS_FILTER)
    
    try:
        while page <= MAX_PAGES:
            logger.info(f"  Fetching page {page}...")
            
            jobs_data = _make_api_request(page, technology)
            
            if jobs_data is None:
                logger.warning(f"Error en página {page}, esperando antes de reintentar...")
                time.sleep(ERROR_WAIT_TIME)
                break
            
            jobs_list = jobs_data.get('jobs', [])
            
            if page == 1:
                total_available = jobs_data.get('totalCount', 0)

            logger.info(f"Encontrado {len(jobs_list)} trabajos en la página {page}")

            if not jobs_list:
                logger.info(f"Página vacía {page} - deteniendo búsqueda")
                break

            jobs_added = 0
            for job in jobs_list:
                result = _process_job(job, technology, cutoff_date)
                
                if result is None:
                    continue
                
                processed_job, job_id = result
                if job_id and job_id not in all_job_ids:
                    all_job_ids.add(job_id)
                    all_jobs.append(processed_job)
                    jobs_added += 1
            
            if jobs_added > 0:
                logger.info(f"  Añadidos {jobs_added} trabajos únicos de página {page}")

            time.sleep(API_DELAY)
            page += 1
        
        if page > MAX_PAGES:
            logger.warning(f"Alcanzado límite de {MAX_PAGES} páginas, deteniendo búsqueda")
        
    except Exception as e:
        logger.error(f"Error en '{technology}': {e}")
        return 0, [], 0
    
    final_count = len(all_jobs)
    logger.info(f"Total de trabajos de Data Science para '{technology}': {final_count} (de {total_available} disponibles, {page-1} páginas)")

    return final_count, all_jobs, total_available
