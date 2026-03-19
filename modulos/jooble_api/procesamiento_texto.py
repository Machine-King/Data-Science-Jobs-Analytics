import re

# ================================
# Desde keywords.py
# ================================
technologies = [
    "Python", "SQL", "R", "Java", "Scala", "C++", "Spark",
    "Pandas", "NumPy", "SciPy", "Dask", "Polars", "Vaex",
    "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM", "CatBoost", "Auto-sklearn", "H2O.ai",
    "Deep Learning", "Neural Networks", "Transformers", "Machine Learning", "Artificial Intelligence", "Reinforcement Learning", "Computer Vision", "NLP", "CNN", "RNN", "LSTM", "GANs",
    "NLTK", "spaCy", "Hugging Face", "Gensim", "Pydantic", "FastAPI", "LangChain",
    "Matplotlib", "Seaborn", "Plotly", "Bokeh", "Altair", "Streamlit", "Dash", "D3.js",
    "Jupyter", "Google Colab", "Docker", "Kubernetes", "Git", "GitHub", "GitLab", "Linux", "Windows", "MacOS", "Bash",
    "Hadoop", "Flink", "Hive", "Presto", "Airflow", "Luigi", "Ray", "MLflow", "Kubeflow", "Snowflake", "BigQuery", "Redshift", "Databricks",
    "PostgreSQL", "MySQL", "Oracle", "SQL Server", "MongoDB", "Cassandra", "Neo4j", "Elasticsearch",
    "AWS", "Azure", "GCP", "IBM Cloud", "Oracle Cloud",
    "Tableau", "Power BI", "Qlik",
    "Apache Kafka", "RabbitMQ", "Kinesis",
    "SAS", "Stata", "SPSS", "Matlab",
]

ds_keywords = [
    'data scientist', 'data science', 'científico de datos',
    'data analyst', 'analista de datos', 'data analysis', 'análisis de datos',
    'data engineer', 'ingeniero de datos', 'data engineering',
    'machine learning', 'ml engineer', 'aprendizaje automático',
    'artificial intelligence', 'inteligencia artificial', 'ai engineer',
    'deep learning', 'neural network', 'redes neuronales',
    'computer vision', 'visión por computador', 'vision por computador',
    'business intelligence', 'bi analyst', 'analytics',
    'business analyst', 'analista de negocio',
    'quantitative analyst', 'research analyst',
    'estadístico', 'statistician', 'biostatistician',
    'research scientist', 'investigador', 'científico',
    'data mining', 'minería de datos', 'predictive analytics',
    'nlp engineer', 'mlops', 'data ops', 'feature engineer'
]

# ================================
# Desde variaciones.py
# ================================
VARIACIONES_TECNOLOGIA = {
    "python": ["python", "py", "python3", "python2"],
    "javascript": ["javascript", "js", "node.js", "nodejs", "react", "vue", "angular"],
    "r": ["rstudio"],
    "sql": ["sql", "mysql", "postgresql", "sqlite", "tsql", "t-sql"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", "c-sharp"],
    ".net": [".net", "net framework", "asp.net"],
    "net": [".net", "net framework", "asp.net"],
    "go": ["golang"],
    "machine learning": ["machine learning", "ml", "aprendizaje automático", "aprendizaje automatico"],
    "deep learning": ["deep learning", "dl", "aprendizaje profundo"],
    "artificial intelligence": ["artificial intelligence", "ai", "inteligencia artificial"],
    "tensorflow": ["tensorflow", "tensor flow", "tf"],
    "pytorch": ["pytorch", "torch", "py torch"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "power bi": ["power bi", "powerbi", "power-bi"],
    "business intelligence": ["business intelligence", "bi", "inteligencia de negocio"],
}

def obtener_variaciones_tecnologia(tech):
    return VARIACIONES_TECNOLOGIA.get(tech.lower(), [tech.lower()])


# ================================
# Desde text_utils.py
# ================================
_DS_KEYWORD_PATTERNS = [re.compile(rf'\b{re.escape(kw)}\b') for kw in ds_keywords]

STANDALONE_KEYWORDS = frozenset([
    'scientist', 'analista', 'statistician', 'estadístico', 
    'researcher', 'investigador'
])
CONTEXT_WORDS = frozenset([
    'data', 'machine', 'artificial', 'business', 'research', 'quantitative', 'analytics'
])

def is_data_science_related(title):
    if not title:
        return False

    title_lower = title.lower()

    for pattern in _DS_KEYWORD_PATTERNS:
        if pattern.search(title_lower):
            return True

    for keyword in STANDALONE_KEYWORDS:
        if re.search(rf'\b{re.escape(keyword)}\b', title_lower):
            if any(context in title_lower for context in CONTEXT_WORDS):
                return True
    
    return False

def technology_appears_in_text(tech, text):
    if not text:
        return False
    
    text_lower = text.lower()
    tech_lower = tech.lower()
    
    if re.search(rf'\b{re.escape(tech_lower)}\b', text_lower):
        return True

    for variation in obtener_variaciones_tecnologia(tech):
        if re.search(rf'\b{re.escape(variation)}\b', text_lower):
            return True
    
    return False
