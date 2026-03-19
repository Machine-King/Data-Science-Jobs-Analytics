"""
Listado de ofertas de trabajo: filtros, aplicación de filtros, paginación y distribución geográfica.
"""
import re
import streamlit as st

from modulos.dashboard.data_loader import extraer_provincia, split_city_province


def render_job_filters(all_jobs_unified, all_technologies):
    """
    Renderiza los filtros de búsqueda de ofertas.
    
    Parameters:
        all_jobs_unified (list): Lista de todos los trabajos.
        all_technologies (list): Lista de tecnologías disponibles.
        
    Returns:
        dict: Estado de todos los filtros aplicados.
    """
    st.header("Ofertas de Trabajo Encontradas")
    st.subheader("Filtros de Busqueda")

    col_tech1, col_tech2 = st.columns(2)
    with col_tech1:
        job_tech_filter = st.multiselect(
            "Filtrar ofertas por tecnologías específicas:",
            all_technologies,
            help="Mostrar solo ofertas que mencionen estas tecnologías específicas."
        )
    with col_tech2:
        tech_match_type = st.radio(
            "Tipo de coincidencia:",
            ["Cualquiera (OR)", "Todas (AND)"],
            help="'Cualquiera': al menos una tecnología. 'Todas': todas las tecnologías seleccionadas."
        )

    search_text = st.text_input(
        "Buscar en titulos y descripciones **(experimental)** :",
        placeholder="Ej: machine learning, senior, remote...",
        help="Busca texto específico en títulos y descripciones de ofertas."
    )

    if st.button("Limpiar todos los filtros", help="Elimina todos los filtros aplicados"):
        st.rerun()

    # Filtros avanzados en 4 columnas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        companies = sorted(list(set(job['company'] for job in all_jobs_unified if job['company'] != 'N/A')))
        st.markdown("**Filtrar por empresa:**")
        selected_company = st.selectbox("Empresa:", ["Todas"] + companies, help="Filtra por empresa")

    with col2:
        st.markdown("**Filtrar por número de tecnologías:**")
        max_techs = max(len(job['technologies']) for job in all_jobs_unified) if all_jobs_unified else 1
        min_techs = st.slider("Mínimo número de tecnologías:", 1, max_techs, 4,
                              help="Muestra solo ofertas con al menos N tecnologías")

    with col3:
        st.markdown("**Filtrar por ubicación:**")
        provinces = sorted(list(set(
            extraer_provincia(job['location']) for job in all_jobs_unified if job['location'] != 'N/A'
        )))
        selected_province = st.selectbox("Provincia/Comunidad:", ["Todas"] + provinces,
                                         help="Selecciona la provincia o comunidad autónoma")

        selected_city = "Todas las ciudades"
        if selected_province != "Todas":
            cities = [split_city_province(j.get('location_original', j.get('location', '')))[0] 
                      for j in all_jobs_unified if extraer_provincia(j.get('location', '')) == selected_province]
            unique_cities = sorted(list(set(c for c in cities if c and c != "Ciudad no especificada")))
            if unique_cities:
                selected_city = st.selectbox(
                    "Ciudad específica:", ["Todas las ciudades"] + unique_cities,
                    help=f"Ciudades disponibles en {selected_province}"
                )
            else:
                st.info(f"No hay ciudades específicas disponibles para {selected_province}")

    with col4:
        st.markdown("**Filtrar por salario:**")
        salary_option = st.selectbox("Salario:", ["Todos", "Con salario especificado", "Sin salario"],
                                     help="Filtra por información salarial")

    return {
        'job_tech_filter': job_tech_filter,
        'tech_match_type': tech_match_type,
        'search_text': search_text,
        'selected_company': selected_company,
        'min_techs': min_techs,
        'selected_province': selected_province,
        'selected_city': selected_city,
        'salary_option': salary_option,
    }


def apply_filters(all_jobs_unified, filters):
    """
    Aplica todos los filtros a la lista de trabajos.
    
    Parameters:
        all_jobs_unified (list): Lista de todos los trabajos.
        filters (dict): Estado de filtros retornado por render_job_filters.
        
    Returns:
        list: Lista de trabajos filtrados.
    """
    def match(j):
        techs = j.get('technologies', [])
        f_tech = filters['job_tech_filter']
        if f_tech:
            if filters['tech_match_type'] == "Todas (AND)" and not all(t in techs for t in f_tech): return False
            if filters['tech_match_type'] == "Cualquiera (OR)" and not any(t in techs for t in f_tech): return False
        
        if filters['search_text']:
            terms = [t.strip().lower() for t in filters['search_text'].split(',') if t.strip()]
            searchable = f"{j.get('title', '')} {j.get('snippet', '')}".lower()
            if not any(term in searchable for term in terms): return False

        if filters['selected_company'] != "Todas" and j.get('company') != filters['selected_company']: return False
        
        if filters['selected_province'] != "Todas":
            if extraer_provincia(j.get('location', '')) != filters['selected_province']: return False
            if filters['selected_city'] != "Todas las ciudades":
                loc_orig = j.get('location_original', j.get('location', ''))
                orig_city = loc_orig.split(',')[0].strip() if ',' in loc_orig else loc_orig
                if orig_city != filters['selected_city']: return False

        if len(techs) < filters['min_techs']: return False

        salary = j.get('salary')
        has_salary = bool(salary) and salary not in ['N/A', ''] and (salary.replace('.', '').replace(',','').isdigit() if isinstance(salary, str) else True)
        if filters['salary_option'] == "Con salario especificado" and not has_salary: return False
        if filters['salary_option'] == "Sin salario" and has_salary: return False
        
        return True

    return [j for j in all_jobs_unified if match(j)]


def render_filter_stats(filtered_jobs, all_jobs_unified, filters):
    """Renderiza estadísticas de filtrado y resumen de filtros activos."""
    if len(filtered_jobs) != len(all_jobs_unified):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ofertas Filtradas", len(filtered_jobs))
        with col2:
            st.metric("Ofertas Totales", len(all_jobs_unified))
        with col3:
            pct = (len(filtered_jobs) / len(all_jobs_unified)) * 100 if all_jobs_unified else 0
            st.metric("% Mostrado", f"{pct:.1f}%")
        with col4:
            st.metric("Ofertas Excluidas", len(all_jobs_unified) - len(filtered_jobs))

    st.write(f"Mostrando {len(filtered_jobs)} ofertas (de {len(all_jobs_unified)} totales):")

    # Resumen de filtros activos
    active = []
    if filters['selected_company'] != "Todas":
        active.append(f"Empresa: {filters['selected_company']}")
    if filters['selected_province'] != "Todas":
        loc_text = filters['selected_province']
        if filters['selected_city'] != "Todas las ciudades":
            loc_text += f" > {filters['selected_city']}"
        active.append(f"Ubicación: {loc_text}")
    if filters['min_techs'] > 1:
        active.append(f"Min. tecnologías: {filters['min_techs']}")
    if filters['salary_option'] != "Todos":
        active.append(f"Salario: {filters['salary_option']}")

    if active:
        st.info(f"**Filtros activos:** {' | '.join(active)}")
    else:
        st.info("**Sin filtros aplicados** - Mostrando todas las ofertas")


def render_location_stats(filtered_jobs, selected_province):
    """Renderiza la distribución por ubicaciones."""
    if not filtered_jobs:
        return

    st.subheader("Distribucion por Ubicaciones")

    from collections import Counter
    location_counts = Counter()
    city_counts = {}

    for job in filtered_jobs:
        _, province = split_city_province(job.get('location', 'N/A'))
        province = province or job.get('location', 'N/A')
        location_counts[province] += 1

        original_city, _ = split_city_province(job.get('location_original', ''))
        if original_city and original_city != province:
            if province not in city_counts:
                city_counts[province] = Counter()
            city_counts[province][original_city] += 1

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Por Provincia/Comunidad (Top 5):**")
        for province, count in location_counts.most_common(5):
            st.write(f"• **{province}**: {count} ofertas ({(count/len(filtered_jobs))*100:.1f}%)")

    with col2:
        if city_counts and selected_province != "Todas":
            st.markdown(f"**Ciudades en {selected_province}:**")
            province_total = max(1, location_counts.get(selected_province, 1))
            count_total = sum(city_counts[selected_province].values())
            
            for city, count in city_counts[selected_province].most_common():
                st.write(f"• **{city}**: {count} ofertas ({(count/province_total)*100:.1f}%)")
                
            st.write(f"• **Ciudad no especificada / Capital**: {province_total - count_total} ofertas ({((province_total - count_total)/province_total)*100:.1f}%)")
            
        elif city_counts:
            st.markdown("**Top Ciudades (selecciona una provincia para ver detalle):**")
            all_cities = [(city, count, province) for province, cities in city_counts.items() for city, count in cities.items()]
            for city, count, province in sorted(all_cities, key=lambda c: int(c[1]), reverse=True)[:5]:
                st.write(f"• **{city}** ({province}): {count} ofertas")


def render_job_cards(filtered_jobs, selected_techs):
    """Renderiza las tarjetas de ofertas con paginación."""
    display_limit = st.slider("Número de ofertas a mostrar por página:", 5, 50, 20)
    total_jobs = len(filtered_jobs)
    total_pages = (total_jobs - 1) // display_limit + 1 if total_jobs > 0 else 1

    if total_pages > 1:
        page = st.number_input(
            "Página:", min_value=1, max_value=total_pages, value=1, step=1,
            help=f"Selecciona la página de resultados (total: {total_pages})"
        )
    else:
        page = 1

    start_idx = (page - 1) * display_limit
    end_idx = min(start_idx + display_limit, total_jobs)
    st.write(f"Mostrando ofertas {start_idx + 1} a {end_idx} de {total_jobs}")

    for i, job in enumerate(filtered_jobs[start_idx:end_idx], start=start_idx + 1):
        with st.expander(f"{job['company']} - {job['title']}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                loc, orig = job.get('location', 'N/A'), job.get('location_original')
                loc_disp = loc.split(',')[0].strip() if ',' in loc else loc
                if orig and orig != loc:
                    loc_disp += f" (orig: {orig.split(',')[0].strip() if ',' in orig else orig})"
                st.write(f"**Ubicacion:** {loc_disp}")

                salary_display = job.get('salary') if job.get('salary') not in [None, 'N/A', ''] else "No especificado"
                st.write(f"**Salario:** {salary_display}")
                st.write(f"**Publicado:** {job.get('created', '').split('T')[0]}")

            with col2:
                st.write("**Tecnologias requeridas:**")
                tech_tags = [
                    f'<span class="tech-tag tech-tag-match">{t}</span>' if t in selected_techs else f'<span class="tech-tag">{t}</span>'
                    for t in job.get('technologies', [])
                ]
                st.markdown(" ".join(tech_tags), unsafe_allow_html=True)

            if job['url'] != 'N/A':
                st.link_button("Ver oferta completa", job['url'], width='stretch')
