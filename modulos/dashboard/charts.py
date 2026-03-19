"""
Gráficas de visualización: toggle de fuente de datos y pestañas de ranking, tabla y comparativas.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

from modulos.dashboard.data_loader import load_jooble_data


def resolve_chart_data(selected_techs, tech_counter, jobs_for_charts, charts_search_text):
    """
    Determina los datos de las gráficas según la fuente seleccionada (actual vs histórico).
    
    Parameters:
        selected_techs (list): Tecnologías seleccionadas por el usuario.
        tech_counter (Counter): Conteos globales de tecnologías.
        jobs_for_charts (list): Trabajos filtrados para gráficas.
        charts_search_text (str): Texto de búsqueda para filtrar gráficas.
        
    Returns:
        tuple: (chart_data_counts, chart_data_source)
    """
    st.header("Visualizaciones")

    chart_data_counts = {}
    chart_data_source = ""

    chart_data_toggle = st.radio(
        "Selecciona fuente de datos para las graficas:",
        ["Datos de ofertas de esta semana (Actuales)", "Historico (A partir del 07/09/2025)"],
        index=0,
        help="'Actual': solo las ofertas actuales. 'Histórico': todos los registros históricos.",
        horizontal=True
    )

    filtered_tech_counts = {tech: tech_counter.get(tech, 0) for tech in selected_techs} if selected_techs else dict(tech_counter)

    if chart_data_toggle == "Historico (A partir del 07/09/2025)":
        chart_data_counts, chart_data_source = _resolve_historical_data(selected_techs)
    else:
        chart_data_counts, chart_data_source = _resolve_current_data(
            selected_techs, filtered_tech_counts, jobs_for_charts, charts_search_text
        )

    return chart_data_counts, chart_data_source


def _resolve_historical_data(selected_techs):
    """Carga y procesa datos históricos para las gráficas."""
    st.info("""
    **Historico**: Muestra el total de ofertas historicas almacenadas para cada tecnologia.
    Representa la demanda acumulada a lo largo del tiempo.
    """)

    data_hist = load_jooble_data('jobs_jooble_history')
    jobs_for_charts_hist = [job for job in data_hist['unified_jobs'] if len(job.get('technologies', [])) > 4]
    tech_counter_hist = Counter(tech for job in jobs_for_charts_hist for tech in job.get('technologies', []))

    chart_data_counts = {tech: tech_counter_hist.get(tech, 0) for tech in selected_techs} if selected_techs else dict(tech_counter_hist)

    # Gráfica de evolución semanal
    _render_weekly_evolution(jobs_for_charts_hist, tech_counter_hist)

    return chart_data_counts, "Histórico (Solo ofertas con más de 4 tecnologías)"


def _resolve_current_data(selected_techs, filtered_tech_counts, jobs_for_charts, charts_search_text):
    """Procesa datos actuales para las gráficas."""
    st.info("""
    **Datos Actuales**: Muestra solo las ofertas actuales almacenadas.
    """)

    chart_data_counts = filtered_tech_counts.copy()

    if charts_search_text:
        search_terms = [term.strip().lower() for term in charts_search_text.split(',')]
        matching_jobs = [
            job for job in jobs_for_charts
            if any(term in f"{job.get('title', '')} {job.get('snippet', '')}".lower() for term in search_terms)
        ]
        
        search_filtered = Counter(tech for job in matching_jobs for tech in job.get('technologies', []) if tech in filtered_tech_counts)
        chart_data_counts = dict(search_filtered)
        
        truncated = f"{charts_search_text[:20]}..." if len(charts_search_text) > 20 else charts_search_text
        chart_data_source = f"ofertas actuales (filtradas por '{truncated}')"
    else:
        chart_data_source = "ofertas actuales (solo ofertas con más de 4 tecnologías)"

    return chart_data_counts, chart_data_source


def _render_weekly_evolution(jobs_for_charts_hist, tech_counter_hist):
    """Renderiza la gráfica de evolución semanal de las top 10 tecnologías."""
    st.subheader("Evolucion semanal de las Top 10 tecnologias")
    top_10_hist = [tech for tech, _ in tech_counter_hist.most_common(10)]
    df_hist = pd.DataFrame(jobs_for_charts_hist)

    if not df_hist.empty and 'created' in df_hist.columns:
        df_hist['created'] = pd.to_datetime(df_hist['created'], errors='coerce')
        df_hist = df_hist[df_hist['created'].notna()]
        df_hist = df_hist.explode('technologies')
        df_hist = df_hist[df_hist['technologies'].isin(top_10_hist)]

        if len(df_hist) == 0:
            st.warning("No hay datos para mostrar en la gráfica semanal.")
        else:
            df_hist['week'] = df_hist['created'].dt.to_period('W').astype(str)
            weekly_counts = df_hist.groupby(['week', 'technologies']).size().reset_index(name='count')
            weekly_pivot = weekly_counts.pivot(index='week', columns='technologies', values='count').fillna(0)
            weekly_pivot = weekly_pivot.sort_index()
            
            # --- Crear un slider discontinuo (por semanas) en Streamlit ---
            available_weeks = list(weekly_pivot.index)
            if len(available_weeks) > 10:
                selected_range = st.select_slider(
                    "Desliza para navegar por el histórico (ventana temporal):",
                    options=available_weeks,
                    value=(available_weeks[-min(12, len(available_weeks))], available_weeks[-1])
                )
                start_week, end_week = selected_range
                # Filtrar los datos en base a la selección del slider discontinuo
                mask = (weekly_pivot.index >= start_week) & (weekly_pivot.index <= end_week)
                weekly_pivot = weekly_pivot.loc[mask]

            fig_line = px.line(
                weekly_pivot,
                x=weekly_pivot.index,
                y=weekly_pivot.columns,
                labels={'value': 'Num Ofertas', 'week': 'Semana'},
                title="Evolucion semanal de las Top 10 tecnologias historicas"
            )
            fig_line.update_layout(
                xaxis_title="Semana", yaxis_title="Num Ofertas",
                legend_title="Tecnología", height=500
            )
            st.plotly_chart(fig_line, width='stretch')


def render_chart_tabs(chart_data_counts, chart_data_source):
    """
    Renderiza las 3 pestañas de visualización: Ranking, Tabla Detallada, Comparativas.
    
    Parameters:
        chart_data_counts (dict): Conteos de tecnologías para las gráficas.
        chart_data_source (str): Descripción de la fuente de datos.
    """
    tab1, tab2, tab3 = st.tabs(["Ranking", "Tabla Detallada", "Comparativas"])

    with tab1:
        _render_ranking_tab(chart_data_counts, chart_data_source)

    with tab2:
        _render_table_tab(chart_data_counts, chart_data_source)

    with tab3:
        _render_comparison_tab(chart_data_counts, chart_data_source)


def _render_ranking_tab(chart_data_counts, chart_data_source):
    """Renderiza la pestaña de ranking."""
    st.subheader("Ranking de Tecnologias Mas Demandadas")

    if chart_data_counts:
        sorted_data = dict(sorted(chart_data_counts.items(), key=lambda x: x[1], reverse=True))
        top_20 = dict(list(sorted_data.items())[:20])

        fig_bar = px.bar(
            x=list(top_20.values()), y=list(top_20.keys()),
            orientation='h',
            title=f"Top {len(top_20)} Tecnologías - {chart_data_source}",
            color=list(top_20.values()),
            color_continuous_scale="viridis",
            text=list(top_20.values())
        )
        fig_bar.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=max(600, len(top_20) * 30),
            xaxis_title="Numero de Ofertas", yaxis_title="Tecnologias"
        )
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_bar, width='stretch')
    else:
        st.warning("No hay tecnologías seleccionadas para mostrar.")


def _render_table_tab(chart_data_counts, chart_data_source):
    """Renderiza la pestaña de tabla detallada."""
    st.subheader("Tabla Detallada de Tecnologias")

    if chart_data_counts:
        sorted_data = dict(sorted(chart_data_counts.items(), key=lambda x: x[1], reverse=True))
        total = sum(sorted_data.values())

        df = pd.DataFrame([
            {
                "Posicion": i + 1, "Tecnologia": tech, "Ofertas": count,
                "Porcentaje": f"{(count / total * 100 if total else 0):.1f}%"
            }
            for i, (tech, count) in enumerate(sorted_data.items())
        ])

        st.info(f"**Datos mostrados:** {chart_data_source}")
        st.dataframe(
            df, width='stretch', height=400,
            column_config={
                "Posicion": st.column_config.NumberColumn("Posicion", format="%d"),
                "Ofertas": st.column_config.NumberColumn("Ofertas", format="%d"),
                "Porcentaje": st.column_config.TextColumn("Porcentaje")
            }
        )
    else:
        st.warning("No hay datos de tecnologias disponibles para mostrar.")


def _render_comparison_tab(chart_data_counts, chart_data_source):
    """Renderiza la pestaña de comparativas."""
    st.subheader("Analisis Comparativo")

    if chart_data_counts and len(chart_data_counts) >= 2:
        sorted_data = dict(sorted(chart_data_counts.items(), key=lambda x: x[1], reverse=True))
        tech_to_compare = st.multiselect("Selecciona tecnologías para comparar:", list(sorted_data.keys()), default=list(sorted_data.keys())[:5])

        if tech_to_compare:
            fig_compare = px.bar(
                x=tech_to_compare,
                y=[sorted_data[tech] for tech in tech_to_compare],
                title=f"Comparación de Tecnologías Seleccionadas - {chart_data_source}",
                color=[sorted_data[tech] for tech in tech_to_compare],
                color_continuous_scale="plasma"
            )
            fig_compare.update_layout(
                xaxis_title="Tecnologias", yaxis_title="Numero de Ofertas", showlegend=False
            )
            st.plotly_chart(fig_compare, width='stretch')

            if len(tech_to_compare) >= 3:
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=[sorted_data[tech] for tech in tech_to_compare],
                    theta=tech_to_compare, fill='toself', name='Demanda'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True,
                    title=f"Radar de Demanda - {chart_data_source}"
                )
                st.plotly_chart(fig_radar, width='stretch')
    else:
        st.info("Se necesitan al menos 2 tecnologias para mostrar comparativas.")
