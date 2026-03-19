"""
Métricas principales (KPIs) del dashboard.
"""
import streamlit as st


def render_metrics(data, all_jobs_unified, multi_tech_jobs, jobs_with_salary):
    """
    Renderiza las 4 métricas principales del dashboard.
    
    Parameters:
        data (dict): Datos cargados del dashboard.
        all_jobs_unified (list): Lista de todos los trabajos.
        multi_tech_jobs (list): Trabajos con múltiples tecnologías.
        jobs_with_salary (list): Trabajos con salario especificado.
    """
    st.header("Metricas Principales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Ofertas Totales Disponibles",
            f"{data['metadata']['total_jobs']:,}",
            help="Total de ofertas de Jooble almacenadas"
        )

    with col2:
        st.metric(
            "Ofertas Multi-tecnología",
            f"{len(multi_tech_jobs):,}",
            help="Ofertas que mencionan múltiples tecnologías"
        )

    with col3:
        st.metric(
            "Ofertas con Salario",
            f"{len(jobs_with_salary):,}",
            help="Ofertas que especifican información salarial"
        )

    with col4:
        if len(all_jobs_unified) > 0:
            avg_tech = sum(len(job['technologies']) for job in all_jobs_unified) / len(all_jobs_unified)
            st.metric(
                "Promedio Techs/Oferta",
                f"{avg_tech:.1f}",
                help="Número promedio de tecnologías por oferta"
            )
