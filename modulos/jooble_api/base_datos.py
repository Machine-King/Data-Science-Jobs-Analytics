import logging
import psycopg2
from psycopg2.extras import execute_values
import os

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# --- CONEXIÓN DIRECTA A POSTGRESQL (SUPABASE) ---
POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR")

BATCH_SIZE = 1000  # Tamaño del batch para inserciones

def insert_jobs_to_postgres(jobs):
    """
    Inserts a list of job dictionaries into the jobs_jooble and jobs_jooble_history tables in a PostgreSQL database.
    """
    conn = None
    try:
        conn = psycopg2.connect(POSTGRES_CONN_STR)
        cur = conn.cursor()

        cur.execute('DELETE FROM jobs_jooble;')
        logger.info("Tabla jobs_jooble vaciada correctamente.")

        jobs_data = [
            (
                job.get('title'),
                job.get('company'),
                job.get('url'),
                job.get('description'),
                job.get('location'),
                job.get('salary'),
                job.get('created'),
                job.get('source'),
                job.get('job_type'),
                job.get('jooble_id'),
                job.get('technologies', [])
            )
            for job in jobs
        ]

        execute_values(
            cur,
            '''
            INSERT INTO jobs_jooble (title, company, url, description, location, salary, created, source, job_type, jooble_id, technologies)
            VALUES %s
            ON CONFLICT (jooble_id) DO NOTHING
            ''',
            jobs_data,
            page_size=BATCH_SIZE
        )

        execute_values(
            cur,
            '''
            INSERT INTO jobs_jooble_history (title, company, url, description, location, salary, created, source, job_type, jooble_id, technologies, inserted_at)
            VALUES %s
            ON CONFLICT (jooble_id) DO NOTHING
            ''',
            jobs_data,
            template='(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())',
            page_size=BATCH_SIZE
        )

        conn.commit()
        cur.close()
        logger.info(f"{len(jobs)} ofertas insertadas en jobs_jooble y jobs_jooble_history correctamente.")
    except Exception as e:
        logger.error(f"Error al insertar en PostgreSQL: {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()

def save_tech_combinations(tech_combination_counts):
    """
    Guarda las combinaciones de tecnologías en la tabla occurrences_tech.
    """
    conn = None
    try:
        conn = psycopg2.connect(POSTGRES_CONN_STR)
        cur = conn.cursor()

        cur.execute('DELETE FROM occurrences_tech;')
        logger.info("Tabla occurrences_tech vaciada correctamente.")

        logger.info(f"Guardando {len(tech_combination_counts)} combinaciones de tecnologías...")
        
        tech_data = [
            (list(tech_combination), len(tech_combination), count)
            for tech_combination, count in tech_combination_counts.items()
        ]

        execute_values(
            cur,
            '''
            INSERT INTO occurrences_tech (technologies, num_tech, occurrences)
            VALUES %s
            ''',
            tech_data,
            page_size=BATCH_SIZE
        )

        conn.commit()
        cur.close()
        logger.info("tech_occurrences insertadas en occurrences_tech correctamente.")
    except Exception as e:
        logger.error(f"Error al insertar en PostgreSQL: {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()
