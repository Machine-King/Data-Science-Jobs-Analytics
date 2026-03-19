import logging
from itertools import combinations
from collections import Counter

from modulos.jooble_api.configuracion import MIN_COMBO_OCCURRENCES
from modulos.jooble_api.procesamiento_texto import technologies
from modulos.jooble_api.modelos import Job

logger = logging.getLogger(__name__)

def _calculate_tech_combinations(jobs):
    tech_combination_counts = Counter()
    
    for job in jobs:
        job_technologies = job.technologies if isinstance(job, Job) else job.get('technologies', [])
        if len(job_technologies) >= 2:
            sorted_techs = sorted(job_technologies, key=lambda t: technologies.index(t))
            tech_combination_counts.update(
                combo for size in range(2, len(sorted_techs) + 1)
                for combo in combinations(sorted_techs, size)
            )
            
    return {combo: count for combo, count in tech_combination_counts.items() 
            if count >= MIN_COMBO_OCCURRENCES}

def _print_summary(tech_counts, tech_totals, total_unique_jobs):
    total_jobs_available = sum(tech_totals.values())
    
    logger.info("\n" + "=" * 75)
    logger.info("RESUMEN:")
    logger.info(f"Total de trabajos únicos encontrados: {total_unique_jobs}")
    logger.info(f"Total de trabajos disponibles en todas las búsquedas: {total_jobs_available:,}")
    logger.info("\nDesglose por tecnología:")
    
    for tech, count in tech_counts.items():
        total_for_tech = tech_totals[tech]
        percentage = (total_for_tech / total_jobs_available * 100) if total_jobs_available > 0 else 0
        logger.info(f"  {tech}: {count} filtrados ({total_for_tech:,} disponibles, {percentage:.1f}%)")

def _process_technology_results(results, tech_counts, tech_totals, jobs_by_id):
    for tech, (count, jobs, total_available) in results.items():
        tech_counts[tech] = count
        tech_totals[tech] = total_available
        logger.info(f"{tech}: {count} trabajos encontrados ({total_available} disponibles)")
        
        for job in jobs:
            job_id = f"{job.title}_{job.company}"
            if job_id not in jobs_by_id:
                job.technologies = [tech]
                jobs_by_id[job_id] = job
            else:
                jobs_by_id[job_id].technologies.append(tech)
