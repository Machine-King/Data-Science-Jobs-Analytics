import os
from dotenv import load_dotenv

load_dotenv()

JOOBLE_HOST = 'es.jooble.org'
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
MAX_PAGES = 50
DAYS_FILTER = 7
API_DELAY = 0.025
ERROR_WAIT_TIME = 3600 + 600  # 1 hora y 10 minutos
MIN_COMBO_OCCURRENCES = 5
MAX_WORKERS = 3
