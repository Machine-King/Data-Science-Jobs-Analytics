"""
Funciones de carga de datos desde PostgreSQL y utilidades de ubicación.
"""
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

_POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR")

# Conexión para pandas (SQLAlchemy) — convierte psycopg2 DSN a URL de SQLAlchemy
POSTGRES_CONN_STR = _POSTGRES_CONN_STR  # Exponer para uso directo con psycopg2 en otros módulos
_SQLALCHEMY_URL = _POSTGRES_CONN_STR.replace("postgresql://", "postgresql+psycopg2://") if _POSTGRES_CONN_STR else None


def split_city_province(loc):
    """
    Separa una ubicación en ciudad y provincia/comunidad.
    
    Parameters:
        loc (str): String con la ubicación.
        
    Returns:
        tuple: (ciudad, provincia)
    """
    if isinstance(loc, str) and ',' in loc:
        parts = [x.strip() for x in loc.split(',')]
        if len(parts) >= 2:
            return parts[0], parts[1]
    if isinstance(loc, str) and loc in [
        'Andalucía', 'Aragón', 'Asturias', 'Islas Baleares', 'Canarias', 'Cantabria',
        'Castilla y León', 'Castilla-La Mancha', 'Cataluña', 'Comunidad Valenciana',
        'Extremadura', 'Galicia', 'Madrid', 'Murcia', 'Navarra', 'País Vasco',
        'La Rioja', 'Ceuta', 'Melilla']:
        return 'Ciudad no especificada', loc
    return None, loc


def extraer_provincia(loc):
    """
    Extrae la provincia/comunidad de una ubicación.
    Si hay coma, la segunda parte es la provincia.
    
    Parameters:
        loc (str): String con la ubicación.
        
    Returns:
        str: Provincia o la ubicación original si no tiene coma.
    """
    if isinstance(loc, str) and ',' in loc:
        parts = [x.strip() for x in loc.split(',')]
        if len(parts) >= 2:
            return parts[1]
    return loc


def load_jooble_data_postgres(table='jobs_jooble'):
    """
    Carga datos desde jobs_jooble (actual) o jobs_jooble_history (histórico).
    
    Parameters:
        table (str): Nombre de la tabla PostgreSQL.
        
    Returns:
        dict: Diccionario con technology_counts, unified_jobs y metadata.
    """
    engine = create_engine(_SQLALCHEMY_URL)
    with engine.connect() as conn:
        jobs_df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    engine.dispose()

    unified_jobs = jobs_df.to_dict(orient='records')
    
    from collections import Counter
    tech_counter = Counter(t for j in unified_jobs for t in j.get('technologies', []))
    technology_counts = dict(tech_counter)

    total_jobs_raw = len(jobs_df)
    total_technologies = len(technology_counts)
    
    unique_companies = jobs_df['company'].replace('N/A', pd.NA).dropna().nunique() if 'company' in jobs_df else 0
    unique_locations = jobs_df['location'].replace('N/A', pd.NA).dropna().nunique() if 'location' in jobs_df else 0
    
    if 'salary' in jobs_df:
        jobs_with_salary = len(jobs_df[(jobs_df['salary'] != 'N/A') & (jobs_df['salary'].notnull())])
    else:
        jobs_with_salary = 0
        
    max_job_date = jobs_df['created'].max() if not jobs_df.empty and 'created' in jobs_df else '2025-12-08'

    all_technologies = sorted(list(tech_counter.keys()))
    jobs_with_salary_list = [j for j in unified_jobs if j.get('salary') and j.get('salary') != 'N/A']
    multi_tech_jobs = [j for j in unified_jobs if len(j.get('technologies', [])) > 1]
    jobs_for_charts = [j for j in unified_jobs if len(j.get('technologies', [])) >= 4]

    return {
        'technology_counts': technology_counts,
        'tech_counter': tech_counter,
        'all_technologies': all_technologies,
        'unified_jobs': unified_jobs,
        'jobs_with_salary': jobs_with_salary_list,
        'multi_tech_jobs': multi_tech_jobs,
        'jobs_for_charts': jobs_for_charts,
        'metadata': {
            'analysis_date': max_job_date,
            'week_range': "Últimos 7 días" if table == 'jobs_jooble' else "Histórico",
            'source': 'Jooble API',
            'jobs_file': 'remoto',
            'tech_file': 'remoto',
            'tech_file_type': 'postgres',
            'total_jobs': total_jobs_raw,
            'total_technologies': total_technologies,
            'unique_companies': unique_companies,
            'unique_locations': unique_locations,
            'jobs_with_salary': jobs_with_salary
        }
    }


@st.cache_data(ttl=604800)
def load_jooble_data(table='jobs_jooble'):
    """Carga datos con caché de 7 días."""
    return load_jooble_data_postgres(table)
