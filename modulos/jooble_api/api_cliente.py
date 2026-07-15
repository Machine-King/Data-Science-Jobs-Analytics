import json
import http.client
import time
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from modulos.jooble_api.configuracion import (
    JOOBLE_HOST, JOOBLE_API_KEYS, MAX_PAGES, DAYS_FILTER, API_DELAY
)
from modulos.jooble_api.modelos import Job
from modulos.jooble_api.procesamiento_texto import is_data_science_related, technology_appears_in_text

logger = logging.getLogger(__name__)

def _validate_config():
    """Valida que las variables de entorno necesarias estén configuradas."""
    if not JOOBLE_API_KEYS:
        raise ValueError(
            "No hay API keys de Jooble configuradas. "
            "Define JOOBLE_API_KEYS (separadas por comas) o JOOBLE_API_KEY en tu archivo .env"
        )
    logger.info(f"Configuración validada correctamente ({len(JOOBLE_API_KEYS)} API key(s) disponibles)")

@contextmanager
def http_connection(host):
    """Context manager para conexiones HTTP."""
    conn = http.client.HTTPSConnection(host)
    try:
        yield conn
    finally:
        conn.close()

def _make_api_request(page, keywords, api_key, location="España"):
    try:
        with http_connection(JOOBLE_HOST) as connection:
            headers = {"Content-type": "application/json"}
            body = json.dumps({
                "keywords": keywords,
                "location": location,
                "page": page
            })

            connection.request('POST', f'/api/{api_key}', body, headers)
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

    api_keys = list(JOOBLE_API_KEYS)
    key_index = 0
    consecutive_failures = 0

    try:
        while page <= MAX_PAGES:
            logger.info(f"  Fetching page {page}...")

            jobs_data = _make_api_request(page, technology, api_keys[key_index])

            if jobs_data is None:
                consecutive_failures += 1
                if consecutive_failures >= len(api_keys):
                    logger.error(
                        f"Error persistente en página {page} tras probar las {len(api_keys)} API key(s), "
                        f"deteniendo búsqueda de '{technology}'"
                    )
                    break
                key_index = (key_index + 1) % len(api_keys)
                logger.warning(
                    f"Error en página {page}, rotando API key ({key_index + 1}/{len(api_keys)})..."
                )
                continue

            consecutive_failures = 0
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
