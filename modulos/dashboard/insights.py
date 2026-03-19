"""
Insights adicionales: combinaciones de tecnologías, empresas más activas y footer.
"""
import pandas as pd
import streamlit as st
from collections import Counter
from sqlalchemy import create_engine, text

from modulos.dashboard.data_loader import POSTGRES_CONN_STR


def render_insights(all_jobs_unified):
    """
    Renderiza la sección de insights: combinaciones de tecnologías y empresas más activas.
    
    Parameters:
        all_jobs_unified (list): Lista de todos los trabajos.
    """
    st.markdown("---")
    st.header("Insights Adicionales")

    col1, col2 = st.columns(2)

    with col1:
        _render_tech_combinations(all_jobs_unified)

    with col2:
        _render_top_companies(all_jobs_unified)


def _render_tech_combinations(all_jobs_unified):
    """Renderiza las combinaciones de tecnologías más frecuentes."""
    st.subheader("Top Combinaciones de Tecnologías")
    st.markdown("(A partir de 5 ocurrencias)")

    min_combo_size = st.selectbox(
        "Numero minimo de tecnologias en la combinacion:",
        [2, 3, 4, 5, 6, 7, 8, 9, 10], index=0,
        help="Selecciona el numero minimo de tecnologias por combinacion"
    )
    max_combo_size = st.selectbox(
        "Numero maximo de tecnologias en la combinacion:",
        ["Sin limite", 2, 3, 4, 5, 6, 7, 8, 9, 10], index=0,
        help="Selecciona el numero maximo de tecnologias por combinacion"
    )

    try:
        _sqlalchemy_url = POSTGRES_CONN_STR.replace("postgresql://", "postgresql+psycopg2://") if POSTGRES_CONN_STR else None
        engine = create_engine(_sqlalchemy_url)

        with engine.connect() as conn:
            limit_clause = "" if max_combo_size == "Sin limite" else "AND num_tech <= :max_size"
            query = text(f"""
                SELECT technologies, occurrences, num_tech 
                FROM occurrences_tech 
                WHERE num_tech >= :min_size {limit_clause}
                ORDER BY occurrences DESC 
                LIMIT 15
            """)
            params = {"min_size": min_combo_size}
            if max_combo_size != "Sin limite":
                params["max_size"] = max_combo_size
                
            tech_combos_df = pd.read_sql_query(query, conn, params=params)
        engine.dispose()

        if not tech_combos_df.empty:
            tech_combos_df['Combinacion'] = tech_combos_df['technologies'].apply(
                lambda x: " + ".join(x) if isinstance(x, list) else str(x)
            )
            tech_combos_df['Frecuencia'] = tech_combos_df['occurrences']

            st.dataframe(
                tech_combos_df[['Combinacion', 'Frecuencia']],
                width='stretch',
                column_config={"Frecuencia": st.column_config.NumberColumn("Frecuencia", format="%d")}
            )

            max_freq = tech_combos_df['Frecuencia'].max()
            if max_freq > len(all_jobs_unified):
                st.warning(f"Frecuencia maxima ({max_freq}) excede el numero total de trabajos ({len(all_jobs_unified)})")
        else:
            st.info("No se encontraron combinaciones que cumplan los criterios.")

    except Exception as e:
        st.error(f"Error al cargar combinaciones: {e}")
        st.info("Usando calculo local como alternativa...")

        tech_combinations = [tuple(sorted(j['technologies'])) for j in all_jobs_unified if len(j.get('technologies', [])) > 1]

        if tech_combinations:
            combo_df = pd.DataFrame([
                {"Combinacion": " + ".join(combo), "Frecuencia": freq}
                for combo, freq in Counter(tech_combinations).most_common(10)
            ])
            st.dataframe(combo_df, width='stretch')
        else:
            st.info("No se encontraron combinaciones significativas.")


def _render_top_companies(all_jobs_unified):
    """Renderiza las empresas más activas."""
    st.subheader("Empresas Mas Activas")

    company_counts = Counter(job['company'] for job in all_jobs_unified if job.get('company', 'N/A') != 'N/A')

    if company_counts:
        company_df = pd.DataFrame(
            [{"Empresa": c, "Ofertas": f} for c, f in company_counts.most_common(10)]
        )
        st.dataframe(company_df, width='stretch')
    else:
        st.info("No se encontraron datos de empresas.")


def render_footer(metadata):
    """Renderiza el pie de pagina del dashboard."""
    st.markdown(f"""
    <div class="footer-container">
        <div class="footer-brand">Data Science Jobs Analytics</div>
        <p><strong>Datos obtenidos de:</strong> <a href="https://jooble.org/api/about" target="_blank">Jooble Jobs API</a></p>
        <p><strong>Desarrollado con:</strong> Streamlit + Supabase</p>
        <p><strong>Última actualización:</strong> {metadata['analysis_date']} | <strong>Periodo analizado:</strong> {metadata['week_range']}</p>
        <p><strong>Creador:</strong> Carlos Luis Rodriguez Brito</p>
    </div>
    """, unsafe_allow_html=True)
