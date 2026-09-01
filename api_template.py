import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from modulos.jooble_api.configuracion import MAX_WORKERS, DAYS_FILTER
from modulos.jooble_api.api_cliente import get_job_data, _validate_config
from modulos.jooble_api.analisis import (
    _calculate_tech_combinations,
    _print_summary,
    _process_technology_results
)
from modulos.jooble_api import base_datos, ubicaciones
from modulos.jooble_api.procesamiento_texto import technologies

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar el análisis completo de trabajos de Data Science."""
    # Validar configuración antes de iniciar
    _validate_config()
    
    logger.info("Iniciando ANÁLISIS COMPLETO de Trabajos de Data Science con la API de Jooble")
    logger.info(f"FILTROS: Últimos {DAYS_FILTER} días, títulos de Data Science, ubicación España")
    logger.info(f"Procesamiento paralelo con {MAX_WORKERS} workers")
    logger.info("=" * 75)
    
    tech_counts = {}
    tech_totals = {}
    jobs_by_id = {}
    results = {}
    
    limpiador = ubicaciones.LimpiadorUbicaciones()
    
    # Procesamiento paralelo de tecnologías
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Enviar todas las tareas
        future_to_tech = {
            executor.submit(get_job_data, tech): tech 
            for tech in technologies
        }
        
        # Recoger resultados a medida que se completan
        for future in as_completed(future_to_tech):
            tech = future_to_tech[future]
            try:
                count, jobs, total_available = future.result()
                results[tech] = (count, jobs, total_available)
                logger.info(f"Completado: {tech}")
            except Exception as e:
                logger.error(f"Error en {tech}: {e}")
                results[tech] = (0, [], 0)
    
    # Procesar resultados manteniendo el orden original de technologies
    ordered_results = {tech: results[tech] for tech in technologies if tech in results}
    _process_technology_results(ordered_results, tech_counts, tech_totals, jobs_by_id)
    
    all_jobs_unified = list(jobs_by_id.values())

    # En ejecución desatendida (GitHub Actions), no vaciar las tablas si la API no devolvió nada.
    if not all_jobs_unified:
        logger.error("No se obtuvo ninguna oferta; se omite la escritura en base de datos.")
        raise SystemExit(1)

    logger.info("-" * 30)
    _print_summary(tech_counts, tech_totals, len(all_jobs_unified))

    # Limpiar y normalizar ubicaciones
    for job in all_jobs_unified:
        job.location = limpiador.normalizar_ubicacion(job.location)

    # Calcular y guardar combinaciones de tecnologías
    logger.info("\nCalculando combinaciones de tecnologías...")
    tech_combination_counts = _calculate_tech_combinations(all_jobs_unified)
    base_datos.save_tech_combinations(tech_combination_counts)
    
    # Convertir Jobs a diccionarios para PostgreSQL
    jobs_as_dicts = [job.to_dict() for job in all_jobs_unified]
    base_datos.insert_jobs_to_postgres(jobs_as_dicts)
    
    logger.info("\nAnálisis completado exitosamente")

if __name__ == "__main__":
    main()
