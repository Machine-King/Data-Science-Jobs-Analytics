"""
Estilos CSS personalizados y componentes de cabecera del dashboard.
"""
import streamlit as st

CUSTOM_CSS = """
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Variables de color ── */
    :root {
        --bg-primary: #ffffff;
        --bg-card: #ffffff;
        --bg-card-hover: #fef2f2;
        --accent-1: #dc2626;
        --accent-2: #ef4444;
        --accent-3: #b91c1c;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-light: #e2e8f0;
        --border-red: rgba(220, 38, 38, 0.2);
        --shadow-soft: 0 2px 12px rgba(0, 0, 0, 0.06);
        --shadow-red: 0 4px 20px rgba(220, 38, 38, 0.12);
    }

    /* ── Global ── */
    html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stApp"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* [data-testid="stAppViewContainer"] {
        background: #fafafa;
    } */

    /* ── Header ── */
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #b91c1c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    .main-icon {
        font-size: 2.6rem;
        font-weight: 800;
    }
    .sub-header {
        color: var(--text-secondary);
        text-align: center;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
        letter-spacing: 0.2px;
    }
    .sub-header strong { color: #dc2626; }

    /* ── Banner / Week info ── */
    .week-banner {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.95rem;
        font-weight: 500;
        box-shadow: var(--shadow-red);
    }
    .week-banner strong { color: #fef2f2; }

    /* ── Aviso (warning) ── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    /* ── Metric cards (st.metric) ── */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        box-shadow: var(--shadow-soft);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    [data-testid="stMetric"]:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-red);
        transform: translateY(-3px);
        box-shadow: var(--shadow-red);
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #dc2626 !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] button {
        background: transparent !important;
        border-radius: 10px 10px 0 0 !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: #fff !important;
        color: #dc2626 !important;
        border: 1px solid var(--border-red) !important;
        border-bottom: 2px solid #dc2626 !important;
    }
    [data-testid="stTabs"] button:hover {
        color: #ef4444 !important;
    }

    /* ── Expanders (job cards) ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 14px !important;
        margin-bottom: 0.65rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"]:hover {
        border-color: var(--border-red) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(220, 38, 38, 0.08);
    }
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* ── Tech tags ── */
    .tech-tag {
        background: #fef2f2;
        border: 1px solid rgba(220, 38, 38, 0.2);
        border-radius: 20px;
        padding: 0.3rem 0.85rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 500;
        color: #dc2626;
        transition: all 0.2s ease;
    }
    .tech-tag:hover {
        background: #fee2e2;
        border-color: rgba(220, 38, 38, 0.4);
        transform: scale(1.05);
    }
    .tech-tag-match {
        background: #dcfce7 !important;
        border-color: #16a34a !important;
        color: #15803d !important;
    }
    .tech-tag-match:hover {
        background: #bbf7d0 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid var(--border-light) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: #fef2f2;
        border: 1px solid rgba(220, 38, 38, 0.15);
        padding: 0.8rem;
        border-radius: 10px;
    }

    /* ── Dataframes / Tables ── */
    [data-testid="stDataFrame"] {
        border-radius: 14px !important;
        overflow: hidden;
    }

    /* ── Buttons ── */
    .stButton > button, .stLinkButton > a {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.2) !important;
    }
    .stButton > button:hover, .stLinkButton > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.35) !important;
    }

    /* ── Section headers ── */
    h2 {
        color: var(--text-primary) !important;
        padding-bottom: 0.5rem;
    }

    /* ── Selectbox / inputs ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div,
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 1px solid var(--border-light) !important;
        transition: border-color 0.2s ease !important;
    }
    [data-testid="stSelectbox"] > div > div:focus-within,
    [data-testid="stMultiSelect"] > div > div:focus-within,
    .stTextInput > div > div > input:focus {
        border-color: rgba(220, 38, 38, 0.4) !important;
        box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.08) !important;
    }

    /* ── Footer ── */
    .footer-container {
        background: #ffffff;
        border: 1px solid var(--border-light);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-top: 2rem;
        box-shadow: var(--shadow-soft);
    }
    .footer-container p {
        color: var(--text-secondary);
        margin: 0.35rem 0;
        font-size: 0.88rem;
    }
    .footer-container a {
        color: #dc2626;
        text-decoration: none;
        font-weight: 500;
    }
    .footer-container a:hover {
        color: #b91c1c;
    }
    .footer-logo {
        font-size: 1rem;
        font-weight: 600;
    }
    .footer-brand {
        font-size: 1rem;
        font-weight: 600;
        background: linear-gradient(135deg, #dc2626, #ef4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* ── Info / Warning boxes ── */
    [data-testid="stInfo"] {
        border-radius: 12px !important;
    }

    /* ── Radio / toggle ── */
    [data-testid="stRadio"] label {
        font-weight: 500 !important;
    }

    /* ── Smooth scroll ── */
    html { scroll-behavior: smooth; }

    /* ── Number input ── */
    [data-testid="stNumberInput"] input {
        border-radius: 10px !important;
    }

    /* ── Slider ── */
    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #dc2626 !important;
    }
</style>
"""


def inject_css():
    """Inyecta los estilos CSS personalizados en la página."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(metadata):
    """
    Renderiza el aviso, título y banner de metadatos.
    
    Parameters:
        metadata (dict): Diccionario con metadatos del análisis.
    """
    st.warning("""
    **⚠️ Aviso importante:** Debido a limitaciones de la API de Jooble, hay trabajos en los que no se han extraido correctamente todas las tecnologias. Por ello, para las graficas solo se tendran en cuenta las ofertas que tengan mas de 4 tecnologias detectadas. Todos los empleos encontrados estaran disponibles en el buscador, pero por defecto se mostraran solo aquellos con mas de 4 tecnologias.
    """)

    st.markdown('<div style="display: flex; align-items: center; justify-content: center; gap: 10px;"><span class="main-icon">📊</span><h1 class="main-header" style="margin-bottom:0px;">Data Science Jobs Analytics - Jooble</h1></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analisis de la demanda de tecnologias en <strong>Data Science</strong> - Datos de Jooble API</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="week-banner">
    <strong>{metadata['week_range']}</strong> | Analisis realizado el <strong>{metadata['analysis_date']}</strong> | 
    Fuente: <strong>{metadata['source']}</strong> | 
    <strong>{metadata['total_jobs']}</strong> ofertas unicas de <strong>{metadata['total_technologies']}</strong> tecnologias
    </div>
    """, unsafe_allow_html=True)
