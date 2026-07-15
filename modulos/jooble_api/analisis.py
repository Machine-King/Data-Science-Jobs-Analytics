import logging
from itertools import combinations
from collections import Counter

from modulos.jooble_api.configuracion import MIN_COMBO_OCCURRENCES
from modulos.jooble_api.procesamiento_texto import technologies
from modulos.jooble_api.modelos import Job

logger = logging.getLogger(__name__)

def _calculate_tech_combinations(jobs):
    if not jobs:
        return {}

    tech_order = {tech: idx for idx, tech in enumerate(technologies)}
    min_occurrences = MIN_COMBO_OCCURRENCES

    # Primer pase: normaliza y cuenta tecnologías individuales para filtrar ruido.
    normalized_job_techs = []
    tech_occurrences = Counter()

    for job in jobs:
        job_technologies = job.technologies if isinstance(job, Job) else job.get('technologies', [])

        # Deduplicar por oferta evita inflar combinaciones y consumo de memoria.
        unique_known_techs = {tech for tech in job_technologies if tech in tech_order}
        if len(unique_known_techs) < 2:
            continue

        normalized_job_techs.append(unique_known_techs)
        tech_occurrences.update(unique_known_techs)

    if not normalized_job_techs:
        return {}

    # Cualquier combinación que incluya una tecnología con baja frecuencia
    # no puede alcanzar el umbral mínimo.
    eligible_techs = {
        tech for tech, count in tech_occurrences.items()
        if count >= min_occurrences
    }

    if len(eligible_techs) < 2:
        return {}

    transactions = []
    for tech_set in normalized_job_techs:
        filtered_techs = [tech for tech in tech_set if tech in eligible_techs]
        if len(filtered_techs) < 2:
            continue

        sorted_techs = tuple(sorted(filtered_techs, key=tech_order.__getitem__))
        transactions.append(sorted_techs)

    if not transactions:
        return {}

    frequent_combination_counts = {}

    # Nivel 2 (pares)
    pair_counts = Counter()
    for techs in transactions:
        pair_counts.update(combinations(techs, 2))

    frequent_k = {
        pair: count for pair, count in pair_counts.items()
        if count >= min_occurrences
    }
    frequent_combination_counts.update(frequent_k)

    k = 3
    while frequent_k:
        prev_itemsets = sorted(frequent_k.keys())
        prev_set = set(prev_itemsets)

        # Join step: combina itemsets frecuentes de tamaño k-1 con prefijo común.
        grouped_by_prefix = {}
        for itemset in prev_itemsets:
            prefix = itemset[:-1]
            grouped_by_prefix.setdefault(prefix, []).append(itemset[-1])

        candidate_set = set()
        for prefix, suffixes in grouped_by_prefix.items():
            suffixes.sort(key=tech_order.__getitem__)
            for i in range(len(suffixes)):
                for j in range(i + 1, len(suffixes)):
                    candidate = prefix + (suffixes[i], suffixes[j])

                    # Prune step: todos los subconjuntos de tamaño k-1 deben ser frecuentes.
                    if all(candidate[:idx] + candidate[idx + 1:] in prev_set for idx in range(k)):
                        candidate_set.add(candidate)

        if not candidate_set:
            break

        candidate_counts = Counter()
        for techs in transactions:
            if len(techs) < k:
                continue
            for combo in combinations(techs, k):
                if combo in candidate_set:
                    candidate_counts[combo] += 1

        frequent_k = {
            combo: count for combo, count in candidate_counts.items()
            if count >= min_occurrences
        }
        frequent_combination_counts.update(frequent_k)
        k += 1

    return frequent_combination_counts

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
