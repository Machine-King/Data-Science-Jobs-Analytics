"""
Data Science Jobs Analytics Dashboard App
"""
import streamlit as st
from collections import Counter

from modulos.dashboard.styles import inject_css, render_header
from modulos.dashboard.data_loader import load_jooble_data
from modulos.dashboard.sidebar import render_sidebar
from modulos.dashboard.metrics import render_metrics
from modulos.dashboard.charts import resolve_chart_data, render_chart_tabs
from modulos.dashboard.job_list import render_job_filters, apply_filters, render_filter_stats, render_location_stats, render_job_cards
from modulos.dashboard.insights import render_insights, render_footer

# --- Configuración de la página ---
st.set_page_config(page_title="Data Science Jobs Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# --- Estilos ---
inject_css()

# --- Carga de datos ---
data = load_jooble_data()
if data is None: st.stop()

# --- Componentes del UI ---
render_header(data['metadata'])

selected_techs, charts_search_text = render_sidebar(
    data, data['all_technologies'], data['tech_counter'], data['unified_jobs']
)

render_metrics(data, data['unified_jobs'], data['multi_tech_jobs'], data['jobs_with_salary'])

chart_data_counts, chart_data_source = resolve_chart_data(
    selected_techs, data['tech_counter'], data['jobs_for_charts'], charts_search_text
)
render_chart_tabs(chart_data_counts, chart_data_source)

filters = render_job_filters(data['unified_jobs'], data['all_technologies'])
filtered_jobs = apply_filters(data['unified_jobs'], filters)

render_filter_stats(filtered_jobs, data['unified_jobs'], filters)
render_location_stats(filtered_jobs, filters['selected_province'])
render_job_cards(filtered_jobs, selected_techs)

render_insights(data['unified_jobs'])
render_footer(data['metadata'])
