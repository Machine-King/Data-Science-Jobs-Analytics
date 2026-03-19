"""
Sidebar: filtros de tecnologías y estadísticas del dataset.
"""
import streamlit as st


def render_sidebar(data, all_technologies, tech_counter, all_jobs_unified):
    """
    Renderiza el sidebar con filtros y estadísticas.
    
    Parameters:
        data (dict): Datos cargados del dashboard.
        all_technologies (list): Lista de tecnologías disponibles.
        tech_counter (Counter): Conteos de tecnologías.
        all_jobs_unified (list): Lista de todos los trabajos.
        
    Returns:
        tuple: (selected_techs, charts_search_text)
    """
    st.sidebar.header("Filtros y Configuracion")

    # --- Filtrado de Tecnologías ---
    st.sidebar.subheader("Filtrado de Tecnologias")

    filter_type = st.sidebar.radio(
        "Tipo de filtro:",
        ["Mostrar todas", "Seleccionar especificas", "Excluir especificas", "Top N tecnologias"],
        help="Elige como filtrar las tecnologias para las graficas y analisis"
    )

    if filter_type == "Seleccionar especificas":
        selected_techs = st.sidebar.multiselect(
            "Tecnologías a mostrar:", all_technologies,
            default=all_technologies[:15],
            help="Solo las tecnologias seleccionadas apareceran en graficas y analisis."
        )
    elif filter_type == "Excluir especificas":
        excluded_techs = st.sidebar.multiselect("Tecnologías a excluir:", all_technologies)
        selected_techs = [tech for tech in all_technologies if tech not in excluded_techs]
    elif filter_type == "Top N tecnologias":
        top_n = st.sidebar.slider("Mostrar top N tecnologías:", 5, len(all_technologies), min(20, len(all_technologies)))
        sorted_all_techs = sorted(data['technology_counts'].items(), key=lambda x: x[1], reverse=True)
        selected_techs = [tech for tech, _ in sorted_all_techs[:top_n]]
    else:
        selected_techs = all_technologies

    # --- Filtros Adicionales ---
    st.sidebar.subheader("Filtros Adicionales")

    charts_search_text = st.sidebar.text_input(
        "Filtrar graficas por contenido:",
        placeholder="Ej: machine learning, senior, remote...",
        help="Filtra las tecnologias de las graficas basandose en ofertas que contengan este texto."
    )

    # --- Estadísticas del Dataset ---
    _render_sidebar_stats(data, all_technologies, all_jobs_unified)

    return selected_techs, charts_search_text


def _render_sidebar_stats(data, all_technologies, all_jobs_unified):
    """Renderiza las estadísticas del dataset en el sidebar."""
    from collections import Counter

    st.sidebar.markdown("---")
    st.sidebar.header("Estadisticas del Dataset")

    st.sidebar.metric("Total Ofertas Únicas", len(all_jobs_unified))
    st.sidebar.metric("Tecnologías Disponibles", len(all_technologies))

    st.sidebar.metric("Provincias", data['metadata'].get('unique_locations', 0))

    if 'limpieza_stats' in data['metadata']:
        location_counts = Counter(job['location'] for job in all_jobs_unified if job.get('location', 'N/A') != 'N/A')
        if location_counts:
            st.sidebar.markdown("**Top Provincias:**")
            for loc, count in location_counts.most_common(5):
                st.sidebar.write(f"• {loc}: {count}")

    st.sidebar.metric("Empresas", data['metadata'].get('unique_companies', 0))

    jobs_with_salary = data['metadata'].get('jobs_with_salary', 0)
    salary_pct = (jobs_with_salary / len(all_jobs_unified) * 100) if all_jobs_unified else 0
    st.sidebar.metric("Ofertas con Salario", f"{jobs_with_salary} ({salary_pct:.1f}%)")

    multi_tech_jobs = len(data.get('multi_tech_jobs', []))
    tech_pct = (multi_tech_jobs / len(all_jobs_unified) * 100) if all_jobs_unified else 0
    st.sidebar.metric("Ofertas Multi-tecnología", f"{multi_tech_jobs} ({tech_pct:.1f}%)")
