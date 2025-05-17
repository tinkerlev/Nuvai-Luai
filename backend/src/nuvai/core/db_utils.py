# file: db_utils.py

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
from src.nuvai.utils.logger import get_logger

logger = get_logger("db_utils")

def ensure_test_database_exists() -> None:
    """
    Ensures the test database exists without overwriting any existing data.

    Follows OWASP & NIST standards:
    - Does not drop existing databases
    - Automatically creates a test database if missing
    - Uses secure logging and exception handling
    """
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    if not db_name:
        logger.error("❌ DB_NAME is not defined in environment.")
        return

    try:
        with psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        ) as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cursor.fetchone()

                if exists:
                    logger.info(f"🧠 Database '{db_name}' already exists. Skipping creation.")
                else:
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                    logger.info(f"✅ Database '{db_name}' created successfully for test session.")
    except Exception as e:
        logger.exception("❌ Could not verify or create test database.")
        raise
