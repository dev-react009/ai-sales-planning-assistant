import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

backend_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(backend_env)
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(DATABASE_URL)