import os
from dotenv import load_dotenv

load_dotenv()

JOOBLE_HOST = 'es.jooble.org'

def _load_api_keys():
    keys_env = os.getenv("JOOBLE_API_KEYS")
    if keys_env:
        return [k.strip() for k in keys_env.split(",") if k.strip()]
    single_key = os.getenv("JOOBLE_API_KEY")
    return [single_key.strip()] if single_key and single_key.strip() else []

JOOBLE_API_KEYS = _load_api_keys()
MAX_PAGES = 50
DAYS_FILTER = 7
API_DELAY = 0.025
MIN_COMBO_OCCURRENCES = 5
MAX_WORKERS = 3
